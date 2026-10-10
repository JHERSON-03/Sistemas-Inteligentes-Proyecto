from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .course import Course
from .types import JsonType


class DailyChallenge(Base):
    __tablename__ = "retos_diarios"
    id: Mapped[int] = mapped_column("reto_id", primary_key=True)
    course_id: Mapped[int] = mapped_column("reto_curso_id", ForeignKey("cursos.curso_id"))
    question: Mapped[str] = mapped_column("reto_pregunta", Text)
    options: Mapped[list] = mapped_column("reto_opciones", JsonType)
    answer: Mapped[int] = mapped_column("reto_respuesta", Integer)
    explanation: Mapped[str] = mapped_column("reto_explicacion", Text)
    course: Mapped[Course] = relationship()


class ChallengeAnswer(Base):
    __tablename__ = "respuestas_reto"
    __table_args__ = (UniqueConstraint("respuesta_reto_usuario_id", "respuesta_reto_dia"),)
    id: Mapped[int] = mapped_column("respuesta_reto_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("respuesta_reto_usuario_id", ForeignKey("usuarios.usuario_id"))
    challenge_id: Mapped[int] = mapped_column("respuesta_reto_reto_id", ForeignKey("retos_diarios.reto_id"))
    day: Mapped[date] = mapped_column("respuesta_reto_dia", Date)
    correct: Mapped[bool] = mapped_column("respuesta_reto_correcta", Boolean)
