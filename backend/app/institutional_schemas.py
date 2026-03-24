from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FormTemplateFieldPayload(BaseModel):
    clave: str = Field(min_length=1, max_length=100)
    etiqueta: str = Field(min_length=1, max_length=150)
    tipo_campo: str = Field(min_length=1, max_length=50)
    requerido: bool = False
    opciones: list[str] = Field(default_factory=list)
    orden: int = 0


class FormTemplatePayload(BaseModel):
    organization_key: str = "default"
    nombre: str = Field(min_length=2, max_length=150)
    modulo: str = Field(min_length=2, max_length=50)
    version: int = 1
    estado: str = "Activo"
    fields: list[FormTemplateFieldPayload] = Field(default_factory=list)


class FormTemplateFieldOut(BaseModel):
    id: int
    clave: str
    etiqueta: str
    tipo_campo: str
    requerido: bool
    opciones: list[str] = Field(default_factory=list)
    orden: int


class FormTemplateOut(BaseModel):
    id: int
    organization_key: str
    nombre: str
    modulo: str
    version: int
    estado: str
    created_by: str | None = None
    created_at: datetime
    fields: list[FormTemplateFieldOut] = Field(default_factory=list)


class InspectionPayload(BaseModel):
    organization_key: str = "default"
    template_id: int | None = None
    aeropuerto_id: int | None = None
    titulo: str = Field(min_length=2, max_length=200)
    alcance: str | None = None
    estado: str = "Pendiente"
    criticidad: str | None = None
    fecha_programada: datetime | None = None
    observaciones: str | None = None


class InspectionOut(BaseModel):
    id: int
    organization_key: str
    template_id: int | None = None
    aeropuerto_id: int | None = None
    titulo: str
    alcance: str | None = None
    estado: str
    criticidad: str | None = None
    fecha_programada: datetime | None = None
    fecha_ejecucion: datetime | None = None
    responsable_id: str | None = None
    observaciones: str | None = None
    created_at: datetime


class CorrectiveActionPayload(BaseModel):
    organization_key: str = "default"
    inspection_id: int | None = None
    incidente_id: int | None = None
    titulo: str = Field(min_length=2, max_length=200)
    descripcion: str | None = None
    prioridad: str = "Media"
    estado: str = "Abierta"
    fecha_vencimiento: datetime | None = None


class CorrectiveActionStatusPayload(BaseModel):
    estado: str


class CorrectiveActionOut(BaseModel):
    id: int
    organization_key: str
    inspection_id: int | None = None
    incidente_id: int | None = None
    titulo: str
    descripcion: str | None = None
    prioridad: str
    estado: str
    fecha_vencimiento: datetime | None = None
    responsable_id: str | None = None
    created_at: datetime
    updated_at: datetime


class TrainingCoursePayload(BaseModel):
    organization_key: str = "default"
    nombre: str = Field(min_length=2, max_length=200)
    categoria: str | None = None
    modalidad: str | None = None
    vigencia_meses: int | None = None
    obligatorio_para: list[str] = Field(default_factory=list)
    estado: str = "Activo"


class TrainingCourseOut(BaseModel):
    id: int
    organization_key: str
    nombre: str
    categoria: str | None = None
    modalidad: str | None = None
    vigencia_meses: int | None = None
    obligatorio_para: list[str] = Field(default_factory=list)
    estado: str
    created_at: datetime


class TrainingRecordPayload(BaseModel):
    organization_key: str = "default"
    course_id: int
    user_id: str | None = None
    estado: str = "Pendiente"
    fecha_vencimiento: datetime | None = None
    observaciones: str | None = None


class TrainingRecordCompletePayload(BaseModel):
    puntaje: float | None = None
    observaciones: str | None = None


class TrainingRecordOut(BaseModel):
    id: int
    course_id: int
    user_id: str | None = None
    organization_key: str
    estado: str
    fecha_asignacion: datetime
    fecha_completado: datetime | None = None
    fecha_vencimiento: datetime | None = None
    puntaje: float | None = None
    observaciones: str | None = None
    created_at: datetime


class NotificationEventOut(BaseModel):
    id: int
    organization_key: str
    canal: str
    tipo: str
    titulo: str
    mensaje: str
    severidad: str
    estado: str
    destinatario_user_id: str | None = None
    recurso_tipo: str | None = None
    recurso_id: str | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    created_at: datetime


class NotificationReadPayload(BaseModel):
    estado: str = "Leida"


class RegulatoryExportOut(BaseModel):
    generado_en: datetime
    formato: str
    nombre_archivo: str
    contenido: str


class BulkOperationResultOut(BaseModel):
    eliminados: int
    detalle: str
