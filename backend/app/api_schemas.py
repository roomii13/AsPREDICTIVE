from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RolUsuario = Literal["administrador", "inspector", "analista", "supervisor"]
NivelRiesgo = Literal["Bajo", "Medio", "Alto", "Crítico"]


class UsuarioOut(BaseModel):
    id: str
    nombre: str
    email: str
    rol: RolUsuario
    estado: bool
    ultimo_login: datetime | None = None
    created_at: datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(LoginRequest):
    nombre: str = Field(min_length=2, max_length=100)
    rol: RolUsuario


class AuthResponse(BaseModel):
    access_token: str
    user: UsuarioOut


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class AuditLogOut(BaseModel):
    id: int
    actor_user_id: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    details_json: str | None = None
    created_at: datetime


class ModelMetricsOut(BaseModel):
    model_version: str
    training_rows: int
    accuracy: float | None = None
    samples_train: int | None = None
    samples_test: int | None = None


class CatalogAeropuertoOut(BaseModel):
    id: int
    codigo_iata: str | None = None
    codigo_icao: str
    nombre: str
    ciudad: str | None = None
    provincia: str | None = None
    categoria: str | None = None
    estado: str
    latitud: float | None = None
    longitud: float | None = None
    created_at: datetime


class CatalogTipoIncidenteOut(BaseModel):
    id: int
    codigo_oaci: str | None = None
    nombre: str
    categoria: str | None = None


class CatalogAeronaveOut(BaseModel):
    id: int
    matricula: str
    modelo: str | None = None
    fabricante: str | None = None
    anio_fabricacion: int | None = None
    operador: str | None = None
    tipo_aeronave: str | None = None
    peso_maximo_despegue: float | None = None
    ultima_revision_mtto: datetime | None = None


class RelatedAeropuertoOut(BaseModel):
    nombre: str
    codigo_icao: str | None = None


class RelatedTipoIncidenteOut(BaseModel):
    nombre: str


class RelatedAeronaveOut(BaseModel):
    matricula: str


class IncidentePayload(BaseModel):
    aeropuerto_id: int | None = None
    tipo_incidente_id: int | None = None
    aeronave_id: int | None = None
    fecha_hora: datetime
    descripcion: str | None = None
    nivel_riesgo: NivelRiesgo
    fase_vuelo: str | None = None
    latitud: float | None = None
    longitud: float | None = None


class IncidenteOut(BaseModel):
    id: int
    aeropuerto_id: int | None = None
    pista_id: int | None = None
    aeronave_id: int | None = None
    tipo_incidente_id: int | None = None
    fecha_hora: datetime
    descripcion: str | None = None
    nivel_riesgo: str | None = None
    fase_vuelo: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    reportado_por: str | None = None
    created_at: datetime
    aeropuertos: RelatedAeropuertoOut | None = None
    tipos_incidente: RelatedTipoIncidenteOut | None = None
    aeronaves: RelatedAeronaveOut | None = None


class AlertaCreate(BaseModel):
    aeropuerto_id: int | None = None
    tipo_alerta: str
    nivel_criticidad: str
    mensaje: str
    score_predictivo: float | None = None
    estado: str = "Pendiente"


class RelatedAlertaAeropuertoOut(BaseModel):
    nombre: str


class AlertaOut(BaseModel):
    id: int
    aeropuerto_id: int | None = None
    fecha_generacion: datetime
    tipo_alerta: str | None = None
    nivel_criticidad: str | None = None
    mensaje: str | None = None
    score_predictivo: float | None = None
    ejecucion_agente_id: int | None = None
    estado: str
    atendido_por: str | None = None
    fecha_resolucion: datetime | None = None
    aeropuertos: RelatedAlertaAeropuertoOut | None = None


class FormCatalogsResponse(BaseModel):
    aeropuertos: list[CatalogAeropuertoOut]
    tipos_incidente: list[CatalogTipoIncidenteOut]
    aeronaves: list[CatalogAeronaveOut]


class DashboardStats(BaseModel):
    totalIncidentes: int
    alertasActivas: int
    aeropuertos: int
    riesgoPromedio: int
    riesgoFuturo: int


class DashboardSummaryResponse(BaseModel):
    stats: DashboardStats
    recentIncidentes: list[IncidenteOut]
    alertas: list[AlertaOut]
