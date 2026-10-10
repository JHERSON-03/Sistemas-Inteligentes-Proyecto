from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .course import Course
from .types import JsonType


class LearningRoute(Base):
    __tablename__ = "rutas"
    id: Mapped[int] = mapped_column("ruta_id", primary_key=True)
    course_id: Mapped[int] = mapped_column("ruta_curso_id", ForeignKey("cursos.curso_id"))
    title: Mapped[str] = mapped_column("ruta_titulo", String(120))
    description: Mapped[str] = mapped_column("ruta_descripcion", Text)
    minutes: Mapped[int] = mapped_column("ruta_minutos", Integer, default=30)
    bonus_points: Mapped[int] = mapped_column("ruta_puntos_bonus", Integer, default=50)
    course: Mapped[Course] = relationship()
    activities: Mapped[list["Activity"]] = relationship(order_by="Activity.order", back_populates="route")


class Activity(Base):
    __tablename__ = "actividades"
    __table_args__ = (UniqueConstraint("actividad_ruta_id", "actividad_orden"),)
    id: Mapped[int] = mapped_column("actividad_id", primary_key=True)
    route_id: Mapped[int] = mapped_column("actividad_ruta_id", ForeignKey("rutas.ruta_id"))
    order: Mapped[int] = mapped_column("actividad_orden", Integer)
    title: Mapped[str] = mapped_column("actividad_titulo", String(120))
    question: Mapped[str] = mapped_column("actividad_pregunta", Text)
    options: Mapped[list] = mapped_column("actividad_opciones", JsonType)
    answer: Mapped[int] = mapped_column("actividad_respuesta", Integer)
    hint: Mapped[str] = mapped_column("actividad_pista", Text)
    explanation: Mapped[str] = mapped_column("actividad_explicacion", Text)
    route: Mapped[LearningRoute] = relationship(back_populates="activities")


class ActivityProgress(Base):
    __tablename__ = "progreso_actividad"
    __table_args__ = (UniqueConstraint("progreso_usuario_id", "progreso_actividad_id"),)
    id: Mapped[int] = mapped_column("progreso_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("progreso_usuario_id", ForeignKey("usuarios.usuario_id"), index=True)
    activity_id: Mapped[int] = mapped_column("progreso_actividad_id", ForeignKey("actividades.actividad_id"))
    attempts: Mapped[int] = mapped_column("progreso_intentos", Integer, default=0)
    correct_first_try: Mapped[bool] = mapped_column("progreso_acerto_primer_intento", Boolean, default=False)
    completed: Mapped[bool] = mapped_column("progreso_completada", Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column("progreso_completada_en", DateTime, nullable=True)
