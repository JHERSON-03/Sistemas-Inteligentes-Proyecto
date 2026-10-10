from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.config import GRADE
from ..core.database import Base


class User(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column("usuario_id", primary_key=True)
    username: Mapped[str] = mapped_column("usuario_usuario", String(50), unique=True, index=True)
    dni: Mapped[str] = mapped_column("usuario_dni", String(8), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column("usuario_clave_hash", String(200))
    full_name: Mapped[str] = mapped_column("usuario_nombre_completo", String(120))
    grade: Mapped[str] = mapped_column("usuario_grado", String(20), default=GRADE)
    section: Mapped[str] = mapped_column("usuario_seccion", String(2), default="B")
    points: Mapped[int] = mapped_column("usuario_puntos", Integer, default=0)
    streak: Mapped[int] = mapped_column("usuario_racha", Integer, default=0)
    best_streak: Mapped[int] = mapped_column("usuario_mejor_racha", Integer, default=0)
    last_login: Mapped[date | None] = mapped_column("usuario_ultimo_ingreso", Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column("usuario_creado_en", DateTime, default=datetime.utcnow,
                                                 server_default=func.now())


class LoginDay(Base):
    """Un registro por cada día que el alumno ingresó (racha y calendario)."""
    __tablename__ = "dias_ingreso"
    __table_args__ = (UniqueConstraint("ingreso_usuario_id", "ingreso_dia"),)
    id: Mapped[int] = mapped_column("ingreso_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("ingreso_usuario_id", ForeignKey("usuarios.usuario_id"), index=True)
    day: Mapped[date] = mapped_column("ingreso_dia", Date)
