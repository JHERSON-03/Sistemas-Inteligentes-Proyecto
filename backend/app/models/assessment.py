from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .course import Course
from .types import JsonType


class Assessment(Base):
    __tablename__ = "evaluaciones"
    id: Mapped[int] = mapped_column("evaluacion_id", primary_key=True)
    course_id: Mapped[int] = mapped_column("evaluacion_curso_id", ForeignKey("cursos.curso_id"))
    title: Mapped[str] = mapped_column("evaluacion_titulo", String(120))
    course: Mapped[Course] = relationship()
    questions: Mapped[list["AssessmentQuestion"]] = relationship(order_by="AssessmentQuestion.order")


class AssessmentQuestion(Base):
    __tablename__ = "preguntas_evaluacion"
    id: Mapped[int] = mapped_column("pregunta_id", primary_key=True)
    assessment_id: Mapped[int] = mapped_column("pregunta_evaluacion_id", ForeignKey("evaluaciones.evaluacion_id"))
    order: Mapped[int] = mapped_column("pregunta_orden", Integer)
    situation: Mapped[str] = mapped_column("pregunta_situacion", Text)
    options: Mapped[list] = mapped_column("pregunta_opciones", JsonType)  # [{"texto": "...", "razon": "..."}]
    answer: Mapped[int] = mapped_column("pregunta_respuesta", Integer)
    feedback_ok: Mapped[str] = mapped_column("pregunta_comentario_ok", Text)
    feedback_ko: Mapped[str] = mapped_column("pregunta_comentario_mal", Text)


class AssessmentAnswer(Base):
    __tablename__ = "respuestas_evaluacion"
    id: Mapped[int] = mapped_column("respuesta_eval_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("respuesta_eval_usuario_id", ForeignKey("usuarios.usuario_id"), index=True)
    question_id: Mapped[int] = mapped_column("respuesta_eval_pregunta_id",
                                             ForeignKey("preguntas_evaluacion.pregunta_id"))
    selected: Mapped[int] = mapped_column("respuesta_eval_seleccion", Integer)
    confidence: Mapped[str] = mapped_column("respuesta_eval_confianza", String(20))  # baja | media | alta
    correct: Mapped[bool] = mapped_column("respuesta_eval_correcta", Boolean)
    created_at: Mapped[datetime] = mapped_column("respuesta_eval_creado_en", DateTime, default=datetime.utcnow,
                                                 server_default=func.now())
