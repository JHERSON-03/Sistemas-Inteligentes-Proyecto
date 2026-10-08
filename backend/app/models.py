"""Modelos ORM mapeados al esquema en español de la base de datos (Supabase/PostgreSQL).

Los atributos de Python se mantienen en inglés; el primer argumento de cada mapped_column
es el nombre real de la columna en la base de datos.
"""
from datetime import date, datetime

from sqlalchemy import (JSON, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
                        func)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# JSONB en PostgreSQL, JSON en SQLite
JsonType = JSON().with_variant(JSONB(), "postgresql")


class User(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column("usuario", String(50), unique=True, index=True)
    dni: Mapped[str] = mapped_column("dni", String(8), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column("clave_hash", String(200))
    full_name: Mapped[str] = mapped_column("nombre_completo", String(120))
    grade: Mapped[str] = mapped_column("grado", String(20), default="5to Sec.")
    section: Mapped[str] = mapped_column("seccion", String(2), default="B")
    points: Mapped[int] = mapped_column("puntos", Integer, default=0)
    streak: Mapped[int] = mapped_column("racha", Integer, default=0)
    best_streak: Mapped[int] = mapped_column("mejor_racha", Integer, default=0)
    last_login: Mapped[date | None] = mapped_column("ultimo_ingreso", Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime, default=datetime.utcnow,
                                                 server_default=func.now())


class LoginDay(Base):
    """Un registro por cada día que el alumno ingresó (racha y calendario)."""
    __tablename__ = "dias_ingreso"
    __table_args__ = (UniqueConstraint("usuario_id", "dia"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id"), index=True)
    day: Mapped[date] = mapped_column("dia", Date)


class Course(Base):
    __tablename__ = "cursos"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column("codigo", String(30), unique=True)
    name: Mapped[str] = mapped_column("nombre", String(60))
    color: Mapped[str] = mapped_column("color", String(7))
    icon: Mapped[str] = mapped_column("icono", String(30))


class LearningRoute(Base):
    __tablename__ = "rutas"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column("curso_id", ForeignKey("cursos.id"))
    title: Mapped[str] = mapped_column("titulo", String(120))
    description: Mapped[str] = mapped_column("descripcion", Text)
    minutes: Mapped[int] = mapped_column("minutos", Integer, default=30)
    bonus_points: Mapped[int] = mapped_column("puntos_bonus", Integer, default=50)
    course: Mapped[Course] = relationship()
    activities: Mapped[list["Activity"]] = relationship(order_by="Activity.order", back_populates="route")


class Activity(Base):
    __tablename__ = "actividades"
    __table_args__ = (UniqueConstraint("ruta_id", "orden"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column("ruta_id", ForeignKey("rutas.id"))
    order: Mapped[int] = mapped_column("orden", Integer)
    title: Mapped[str] = mapped_column("titulo", String(120))
    question: Mapped[str] = mapped_column("pregunta", Text)
    options: Mapped[list] = mapped_column("opciones", JsonType)
    answer: Mapped[int] = mapped_column("respuesta", Integer)
    hint: Mapped[str] = mapped_column("pista", Text)
    explanation: Mapped[str] = mapped_column("explicacion", Text)
    route: Mapped[LearningRoute] = relationship(back_populates="activities")


class ActivityProgress(Base):
    __tablename__ = "progreso_actividad"
    __table_args__ = (UniqueConstraint("usuario_id", "actividad_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id"), index=True)
    activity_id: Mapped[int] = mapped_column("actividad_id", ForeignKey("actividades.id"))
    attempts: Mapped[int] = mapped_column("intentos", Integer, default=0)
    correct_first_try: Mapped[bool] = mapped_column("acerto_primer_intento", Boolean, default=False)
    completed: Mapped[bool] = mapped_column("completada", Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column("completada_en", DateTime, nullable=True)


class Assessment(Base):
    __tablename__ = "evaluaciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column("curso_id", ForeignKey("cursos.id"))
    title: Mapped[str] = mapped_column("titulo", String(120))
    course: Mapped[Course] = relationship()
    questions: Mapped[list["AssessmentQuestion"]] = relationship(order_by="AssessmentQuestion.order")


class AssessmentQuestion(Base):
    __tablename__ = "preguntas_evaluacion"
    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column("evaluacion_id", ForeignKey("evaluaciones.id"))
    order: Mapped[int] = mapped_column("orden", Integer)
    situation: Mapped[str] = mapped_column("situacion", Text)
    options: Mapped[list] = mapped_column("opciones", JsonType)  # [{"texto": "...", "razon": "..."}]
    answer: Mapped[int] = mapped_column("respuesta", Integer)
    feedback_ok: Mapped[str] = mapped_column("comentario_ok", Text)
    feedback_ko: Mapped[str] = mapped_column("comentario_mal", Text)


class AssessmentAnswer(Base):
    __tablename__ = "respuestas_evaluacion"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id"), index=True)
    question_id: Mapped[int] = mapped_column("pregunta_id", ForeignKey("preguntas_evaluacion.id"))
    selected: Mapped[int] = mapped_column("seleccion", Integer)
    confidence: Mapped[str] = mapped_column("confianza", String(20))  # baja | media | alta
    correct: Mapped[bool] = mapped_column("correcta", Boolean)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime, default=datetime.utcnow,
                                                 server_default=func.now())


class DailyChallenge(Base):
    __tablename__ = "retos_diarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column("curso_id", ForeignKey("cursos.id"))
    question: Mapped[str] = mapped_column("pregunta", Text)
    options: Mapped[list] = mapped_column("opciones", JsonType)
    answer: Mapped[int] = mapped_column("respuesta", Integer)
    explanation: Mapped[str] = mapped_column("explicacion", Text)
    course: Mapped[Course] = relationship()


class ChallengeAnswer(Base):
    __tablename__ = "respuestas_reto"
    __table_args__ = (UniqueConstraint("usuario_id", "dia"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id"))
    challenge_id: Mapped[int] = mapped_column("reto_id", ForeignKey("retos_diarios.id"))
    day: Mapped[date] = mapped_column("dia", Date)
    correct: Mapped[bool] = mapped_column("correcta", Boolean)


class TutorMessage(Base):
    __tablename__ = "mensajes_tutor"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id"), index=True)
    session_id: Mapped[str] = mapped_column("sesion_id", String(40), index=True)
    course: Mapped[str] = mapped_column("curso", String(30))
    role: Mapped[str] = mapped_column("emisor", String(10))  # "alumno" | "tutor"
    content: Mapped[str] = mapped_column("contenido", Text)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime, default=datetime.utcnow,
                                                 server_default=func.now())


class StudyLog(Base):
    """Minutos de estudio por tipo: ruta, tutor, autoevaluacion."""
    __tablename__ = "registro_estudio"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id"), index=True)
    kind: Mapped[str] = mapped_column("tipo", String(20))
    minutes: Mapped[float] = mapped_column("minutos", Numeric(6, 1, asdecimal=False))
    day: Mapped[date] = mapped_column("dia", Date, default=date.today)
