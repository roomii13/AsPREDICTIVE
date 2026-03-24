from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(50))
    estado: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource_type: Mapped[str] = mapped_column(String(100), index=True)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Aeropuerto(Base):
    __tablename__ = "aeropuertos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_iata: Mapped[str | None] = mapped_column(String(3), nullable=True)
    codigo_icao: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    ciudad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provincia: Mapped[str | None] = mapped_column(String(100), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="Activo")
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Aeronave(Base):
    __tablename__ = "aeronaves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    matricula: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fabricante: Mapped[str | None] = mapped_column(String(100), nullable=True)
    anio_fabricacion: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operador: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo_aeronave: Mapped[str | None] = mapped_column(String(50), nullable=True)
    peso_maximo_despegue: Mapped[float | None] = mapped_column(Float, nullable=True)
    ultima_revision_mtto: Mapped[datetime | None] = mapped_column(Date, nullable=True)


class TipoIncidente(Base):
    __tablename__ = "tipos_incidente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_oaci: Mapped[str | None] = mapped_column(String(10), nullable=True)
    nombre: Mapped[str] = mapped_column(String(100))
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Incidente(Base):
    __tablename__ = "incidentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aeropuerto_id: Mapped[int | None] = mapped_column(ForeignKey("aeropuertos.id"), nullable=True)
    pista_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aeronave_id: Mapped[int | None] = mapped_column(ForeignKey("aeronaves.id"), nullable=True)
    tipo_incidente_id: Mapped[int | None] = mapped_column(ForeignKey("tipos_incidente.id"), nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    nivel_riesgo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fase_vuelo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    reportado_por: Mapped[str | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    aeropuerto: Mapped[Aeropuerto | None] = relationship()
    aeronave: Mapped[Aeronave | None] = relationship()
    tipo_incidente: Mapped[TipoIncidente | None] = relationship()


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aeropuerto_id: Mapped[int | None] = mapped_column(ForeignKey("aeropuertos.id"), nullable=True)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tipo_alerta: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nivel_criticidad: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mensaje: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_predictivo: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ejecucion_agente_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="Pendiente", index=True)
    atendido_por: Mapped[str | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_resolucion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    aeropuerto: Mapped[Aeropuerto | None] = relationship()
