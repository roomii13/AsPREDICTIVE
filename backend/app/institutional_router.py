from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .db import get_db
from .institutional_models import CorrectiveAction, FormTemplate, FormTemplateField, Inspection, NotificationEvent, TrainingCourse, TrainingRecord
from .institutional_schemas import (
    CorrectiveActionOut,
    CorrectiveActionPayload,
    CorrectiveActionStatusPayload,
    FormTemplateOut,
    FormTemplatePayload,
    InspectionOut,
    InspectionPayload,
    BulkOperationResultOut,
    NotificationEventOut,
    NotificationReadPayload,
    RegulatoryExportOut,
    TrainingCourseOut,
    TrainingCoursePayload,
    TrainingRecordCompletePayload,
    TrainingRecordOut,
    TrainingRecordPayload,
)
from .models import Usuario
from .observability import write_audit_log
from .security import decode_access_token


router = APIRouter(prefix="/institutional", tags=["institutional"])


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Usuario:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")

    token = authorization.split(" ", 1)[1]
    try:
        user_id = decode_access_token(token)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error

    user = db.get(Usuario, user_id)
    if not user or not user.estado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario invalido")
    return user


def require_roles(*allowed_roles: str):
    def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos suficientes")
        return current_user

    return dependency


def to_template_out(template: FormTemplate, fields: list[FormTemplateField]) -> FormTemplateOut:
    sorted_fields = sorted(fields, key=lambda item: item.orden)
    return FormTemplateOut(
        id=template.id,
        organization_key=template.organization_key,
        nombre=template.nombre,
        modulo=template.modulo,
        version=template.version,
        estado=template.estado,
        created_by=template.created_by,
        created_at=template.created_at,
        fields=[
            {
                "id": field.id,
                "clave": field.clave,
                "etiqueta": field.etiqueta,
                "tipo_campo": field.tipo_campo,
                "requerido": field.requerido,
                "opciones": json.loads(field.opciones_json) if field.opciones_json else [],
                "orden": field.orden,
            }
            for field in sorted_fields
        ],
    )


def create_notification(
    db: Session,
    organization_key: str,
    tipo: str,
    titulo: str,
    mensaje: str,
    severidad: str = "Media",
    destinatario_user_id: str | None = None,
    recurso_tipo: str | None = None,
    recurso_id: str | None = None,
) -> None:
    db.add(
        NotificationEvent(
            organization_key=organization_key,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            severidad=severidad,
            destinatario_user_id=destinatario_user_id,
            recurso_tipo=recurso_tipo,
            recurso_id=recurso_id,
        )
    )


@router.get("/form-templates", response_model=list[FormTemplateOut])
def list_form_templates(
    organization_key: str | None = Query(default=None),
    _: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FormTemplateOut]:
    statement = select(FormTemplate).order_by(FormTemplate.modulo.asc(), FormTemplate.nombre.asc())
    if organization_key:
        statement = statement.where(FormTemplate.organization_key == organization_key)
    templates = list(db.scalars(statement))
    fields = list(db.scalars(select(FormTemplateField)))
    fields_by_template: dict[int, list[FormTemplateField]] = {}
    for field in fields:
        fields_by_template.setdefault(field.template_id, []).append(field)
    return [to_template_out(template, fields_by_template.get(template.id, [])) for template in templates]


@router.post("/form-templates", response_model=FormTemplateOut, status_code=201)
def create_form_template(
    payload: FormTemplatePayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor")),
    db: Session = Depends(get_db),
) -> FormTemplateOut:
    template = FormTemplate(
        organization_key=payload.organization_key,
        nombre=payload.nombre,
        modulo=payload.modulo,
        version=payload.version,
        estado=payload.estado,
        created_by=current_user.id,
    )
    db.add(template)
    db.flush()

    created_fields: list[FormTemplateField] = []
    for field in payload.fields:
        field_model = FormTemplateField(
            template_id=template.id,
            clave=field.clave,
            etiqueta=field.etiqueta,
            tipo_campo=field.tipo_campo,
            requerido=field.requerido,
            opciones_json=json.dumps(field.opciones),
            orden=field.orden,
        )
        db.add(field_model)
        created_fields.append(field_model)

    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="form_template_creado",
        resource_type="form_template",
        resource_id=str(template.id),
        details={"organization_key": payload.organization_key, "modulo": payload.modulo, "nombre": payload.nombre},
    )
    db.commit()
    return to_template_out(template, created_fields)


@router.get("/inspections", response_model=list[InspectionOut])
def list_inspections(
    organization_key: str | None = Query(default=None),
    _: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InspectionOut]:
    statement = select(Inspection).order_by(Inspection.created_at.desc())
    if organization_key:
        statement = statement.where(Inspection.organization_key == organization_key)
    return list(db.scalars(statement))


@router.post("/inspections", response_model=InspectionOut, status_code=201)
def create_inspection(
    payload: InspectionPayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor", "inspector")),
    db: Session = Depends(get_db),
) -> InspectionOut:
    inspection = Inspection(
        organization_key=payload.organization_key,
        template_id=payload.template_id,
        aeropuerto_id=payload.aeropuerto_id,
        titulo=payload.titulo,
        alcance=payload.alcance,
        estado=payload.estado,
        criticidad=payload.criticidad,
        fecha_programada=payload.fecha_programada,
        observaciones=payload.observaciones,
        responsable_id=current_user.id,
    )
    db.add(inspection)
    create_notification(
        db,
        organization_key=payload.organization_key,
        tipo="inspection_created",
        titulo="Nueva inspeccion programada",
        mensaje=f"Se registro la inspeccion '{payload.titulo}' con estado {payload.estado}.",
        severidad=payload.criticidad or "Media",
        destinatario_user_id=current_user.id,
        recurso_tipo="inspection",
    )
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="inspeccion_creada",
        resource_type="inspection",
        resource_id=None,
        details={"organization_key": payload.organization_key, "titulo": payload.titulo, "estado": payload.estado},
    )
    db.commit()
    db.refresh(inspection)
    return inspection


@router.delete("/inspections/{inspection_id}", status_code=204)
def delete_inspection(
    inspection_id: int,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor")),
    db: Session = Depends(get_db),
) -> None:
    inspection = db.get(Inspection, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspeccion no encontrada")

    linked_actions = list(db.scalars(select(CorrectiveAction).where(CorrectiveAction.inspection_id == inspection_id)))
    for action in linked_actions:
        action.inspection_id = None
        action.updated_at = datetime.utcnow()

    db.execute(
        delete(NotificationEvent).where(
            NotificationEvent.organization_key == inspection.organization_key,
            NotificationEvent.tipo == "inspection_created",
            NotificationEvent.mensaje.contains(f"'{inspection.titulo}'"),
        )
    )

    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="inspeccion_eliminada",
        resource_type="inspection",
        resource_id=str(inspection_id),
        details={"titulo": inspection.titulo},
    )
    db.delete(inspection)
    db.commit()


@router.delete("/inspections", response_model=BulkOperationResultOut)
def delete_test_inspections(
    organization_key: str = Query(default="default"),
    title: str | None = Query(default=None),
    only_pending: bool = Query(default=True),
    current_user: Usuario = Depends(require_roles("administrador", "supervisor")),
    db: Session = Depends(get_db),
) -> BulkOperationResultOut:
    statement = select(Inspection).where(Inspection.organization_key == organization_key)
    if title:
        statement = statement.where(Inspection.titulo == title)
    if only_pending:
        statement = statement.where(Inspection.estado == "Pendiente")

    inspections = list(db.scalars(statement))
    if not inspections:
        return BulkOperationResultOut(eliminados=0, detalle="No se encontraron inspecciones para eliminar")

    inspection_ids = [inspection.id for inspection in inspections]
    inspection_titles = sorted({inspection.titulo for inspection in inspections})

    linked_actions = list(db.scalars(select(CorrectiveAction).where(CorrectiveAction.inspection_id.in_(inspection_ids))))
    for action in linked_actions:
        action.inspection_id = None
        action.updated_at = datetime.utcnow()

    for inspection in inspections:
        db.delete(inspection)

    for inspection_title in inspection_titles:
        db.execute(
            delete(NotificationEvent).where(
                NotificationEvent.organization_key == organization_key,
                NotificationEvent.tipo == "inspection_created",
                NotificationEvent.mensaje.contains(f"'{inspection_title}'"),
            )
        )

    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="inspecciones_eliminadas",
        resource_type="inspection",
        details={
            "organization_key": organization_key,
            "titulo": title,
            "only_pending": only_pending,
            "eliminados": len(inspection_ids),
        },
    )
    db.commit()
    return BulkOperationResultOut(
        eliminados=len(inspection_ids),
        detalle="Inspecciones eliminadas correctamente",
    )


@router.get("/corrective-actions", response_model=list[CorrectiveActionOut])
def list_corrective_actions(
    organization_key: str | None = Query(default=None),
    _: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CorrectiveActionOut]:
    statement = select(CorrectiveAction).order_by(CorrectiveAction.created_at.desc())
    if organization_key:
        statement = statement.where(CorrectiveAction.organization_key == organization_key)
    return list(db.scalars(statement))


@router.post("/corrective-actions", response_model=CorrectiveActionOut, status_code=201)
def create_corrective_action(
    payload: CorrectiveActionPayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor", "inspector")),
    db: Session = Depends(get_db),
) -> CorrectiveActionOut:
    action = CorrectiveAction(
        organization_key=payload.organization_key,
        inspection_id=payload.inspection_id,
        incidente_id=payload.incidente_id,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        prioridad=payload.prioridad,
        estado=payload.estado,
        fecha_vencimiento=payload.fecha_vencimiento,
        responsable_id=current_user.id,
    )
    db.add(action)
    create_notification(
        db,
        organization_key=payload.organization_key,
        tipo="corrective_action_created",
        titulo="Nueva accion correctiva",
        mensaje=f"Se creo la accion correctiva '{payload.titulo}' con prioridad {payload.prioridad}.",
        severidad=payload.prioridad,
        destinatario_user_id=current_user.id,
        recurso_tipo="corrective_action",
    )
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="accion_correctiva_creada",
        resource_type="corrective_action",
        details={"organization_key": payload.organization_key, "titulo": payload.titulo, "prioridad": payload.prioridad},
    )
    db.commit()
    db.refresh(action)
    return action


@router.post("/corrective-actions/{action_id}/status", response_model=CorrectiveActionOut)
def update_corrective_action_status(
    action_id: int,
    payload: CorrectiveActionStatusPayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor", "inspector")),
    db: Session = Depends(get_db),
) -> CorrectiveActionOut:
    action = db.get(CorrectiveAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Accion correctiva no encontrada")
    action.estado = payload.estado
    action.updated_at = datetime.utcnow()
    create_notification(
        db,
        organization_key=action.organization_key,
        tipo="corrective_action_updated",
        titulo="Accion correctiva actualizada",
        mensaje=f"La accion '{action.titulo}' cambio a estado {payload.estado}.",
        severidad=action.prioridad,
        destinatario_user_id=current_user.id,
        recurso_tipo="corrective_action",
        recurso_id=str(action_id),
    )
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="accion_correctiva_actualizada",
        resource_type="corrective_action",
        resource_id=str(action_id),
        details={"estado": payload.estado},
    )
    db.commit()
    db.refresh(action)
    return action


@router.get("/training/courses", response_model=list[TrainingCourseOut])
def list_training_courses(
    organization_key: str | None = Query(default=None),
    _: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TrainingCourseOut]:
    statement = select(TrainingCourse).order_by(TrainingCourse.nombre.asc())
    if organization_key:
        statement = statement.where(TrainingCourse.organization_key == organization_key)
    courses = list(db.scalars(statement))
    return [
        TrainingCourseOut(
            id=course.id,
            organization_key=course.organization_key,
            nombre=course.nombre,
            categoria=course.categoria,
            modalidad=course.modalidad,
            vigencia_meses=course.vigencia_meses,
            obligatorio_para=json.loads(course.obligatorio_para_json) if course.obligatorio_para_json else [],
            estado=course.estado,
            created_at=course.created_at,
        )
        for course in courses
    ]


@router.post("/training/courses", response_model=TrainingCourseOut, status_code=201)
def create_training_course(
    payload: TrainingCoursePayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor")),
    db: Session = Depends(get_db),
) -> TrainingCourseOut:
    course = TrainingCourse(
        organization_key=payload.organization_key,
        nombre=payload.nombre,
        categoria=payload.categoria,
        modalidad=payload.modalidad,
        vigencia_meses=payload.vigencia_meses,
        obligatorio_para_json=json.dumps(payload.obligatorio_para),
        estado=payload.estado,
    )
    db.add(course)
    create_notification(
        db,
        organization_key=payload.organization_key,
        tipo="training_course_created",
        titulo="Nuevo curso disponible",
        mensaje=f"Se creo el curso '{payload.nombre}' para gestion institucional.",
        severidad="Baja",
        destinatario_user_id=current_user.id,
        recurso_tipo="training_course",
    )
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="curso_capacitacion_creado",
        resource_type="training_course",
        details={"organization_key": payload.organization_key, "nombre": payload.nombre},
    )
    db.commit()
    db.refresh(course)
    return TrainingCourseOut(
        id=course.id,
        organization_key=course.organization_key,
        nombre=course.nombre,
        categoria=course.categoria,
        modalidad=course.modalidad,
        vigencia_meses=course.vigencia_meses,
        obligatorio_para=payload.obligatorio_para,
        estado=course.estado,
        created_at=course.created_at,
    )


@router.get("/training/records", response_model=list[TrainingRecordOut])
def list_training_records(
    organization_key: str | None = Query(default=None),
    _: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TrainingRecordOut]:
    statement = select(TrainingRecord).order_by(TrainingRecord.created_at.desc())
    if organization_key:
        statement = statement.where(TrainingRecord.organization_key == organization_key)
    return list(db.scalars(statement))


@router.post("/training/records", response_model=TrainingRecordOut, status_code=201)
def create_training_record(
    payload: TrainingRecordPayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor")),
    db: Session = Depends(get_db),
) -> TrainingRecordOut:
    record = TrainingRecord(
        organization_key=payload.organization_key,
        course_id=payload.course_id,
        user_id=payload.user_id,
        estado=payload.estado,
        fecha_vencimiento=payload.fecha_vencimiento,
        observaciones=payload.observaciones,
    )
    db.add(record)
    create_notification(
        db,
        organization_key=payload.organization_key,
        tipo="training_assigned",
        titulo="Capacitacion asignada",
        mensaje=f"Se asigno el curso {payload.course_id} con estado {payload.estado}.",
        severidad="Media",
        destinatario_user_id=payload.user_id or current_user.id,
        recurso_tipo="training_record",
    )
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="asignacion_capacitacion_creada",
        resource_type="training_record",
        details={"organization_key": payload.organization_key, "course_id": payload.course_id, "estado": payload.estado},
    )
    db.commit()
    db.refresh(record)
    return record


@router.post("/training/records/{record_id}/complete", response_model=TrainingRecordOut)
def complete_training_record(
    record_id: int,
    payload: TrainingRecordCompletePayload,
    current_user: Usuario = Depends(require_roles("administrador", "supervisor")),
    db: Session = Depends(get_db),
) -> TrainingRecordOut:
    record = db.get(TrainingRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de capacitacion no encontrado")
    record.estado = "Completado"
    record.fecha_completado = datetime.utcnow()
    record.puntaje = payload.puntaje
    record.observaciones = payload.observaciones
    create_notification(
        db,
        organization_key=record.organization_key,
        tipo="training_completed",
        titulo="Capacitacion completada",
        mensaje=f"El registro de capacitacion {record.id} fue completado.",
        severidad="Baja",
        destinatario_user_id=current_user.id,
        recurso_tipo="training_record",
        recurso_id=str(record_id),
    )
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="capacitacion_completada",
        resource_type="training_record",
        resource_id=str(record_id),
        details={"puntaje": payload.puntaje},
    )
    db.commit()
    db.refresh(record)
    return record


@router.get("/notifications", response_model=list[NotificationEventOut])
def list_notifications(
    organization_key: str | None = Query(default=None),
    _: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationEventOut]:
    statement = select(NotificationEvent).order_by(NotificationEvent.created_at.desc()).limit(100)
    if organization_key:
        statement = statement.where(NotificationEvent.organization_key == organization_key)
    return list(db.scalars(statement))


@router.post("/notifications/{notification_id}/read", response_model=NotificationEventOut)
def mark_notification_read(
    notification_id: int,
    payload: NotificationReadPayload,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationEventOut:
    notification = db.get(NotificationEvent, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    notification.estado = payload.estado
    notification.read_at = datetime.utcnow()
    write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="notificacion_leida",
        resource_type="notification_event",
        resource_id=str(notification_id),
        details={"estado": payload.estado},
    )
    db.commit()
    db.refresh(notification)
    return notification


@router.get("/exports/regulatory", response_model=RegulatoryExportOut)
def export_regulatory_report(
    organization_key: str = Query(default="default"),
    _: Usuario = Depends(require_roles("administrador", "supervisor", "analista")),
    db: Session = Depends(get_db),
) -> RegulatoryExportOut:
    inspections = list(db.scalars(select(Inspection).where(Inspection.organization_key == organization_key).order_by(Inspection.created_at.desc()).limit(10)))
    actions = list(db.scalars(select(CorrectiveAction).where(CorrectiveAction.organization_key == organization_key).order_by(CorrectiveAction.created_at.desc()).limit(10)))
    records = list(db.scalars(select(TrainingRecord).where(TrainingRecord.organization_key == organization_key).order_by(TrainingRecord.created_at.desc()).limit(10)))
    notifications = list(db.scalars(select(NotificationEvent).where(NotificationEvent.organization_key == organization_key).order_by(NotificationEvent.created_at.desc()).limit(10)))

    lines = [
        "REPORTE REGULATORIO ASPREDICTIVE",
        f"Organizacion: {organization_key}",
        f"Generado: {datetime.utcnow().isoformat()}",
        "",
        "1. INSPECCIONES",
    ]
    lines.extend([f"- {item.titulo} | estado={item.estado} | criticidad={item.criticidad or 'N/D'}" for item in inspections] or ["- Sin registros"])
    lines.append("")
    lines.append("2. ACCIONES CORRECTIVAS")
    lines.extend([f"- {item.titulo} | prioridad={item.prioridad} | estado={item.estado}" for item in actions] or ["- Sin registros"])
    lines.append("")
    lines.append("3. CAPACITACIONES")
    lines.extend([f"- registro {item.id} | course_id={item.course_id} | estado={item.estado}" for item in records] or ["- Sin registros"])
    lines.append("")
    lines.append("4. NOTIFICACIONES")
    lines.extend([f"- {item.titulo} | severidad={item.severidad} | estado={item.estado}" for item in notifications] or ["- Sin registros"])
    lines.append("")
    lines.append("5. TRAZABILIDAD")
    lines.append("Este reporte puede utilizarse como base previa para exporte PDF institucional.")

    return RegulatoryExportOut(
        generado_en=datetime.utcnow(),
        formato="txt",
        nombre_archivo=f"reporte_regulatorio_{organization_key}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt",
        contenido="\n".join(lines),
    )
