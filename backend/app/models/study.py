from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class StudyLog(Base):
    """Minutos de estudio por tipo: ruta, tutor, autoevaluacion."""
    __tablename__ = "registro_estudio"
    id: Mapped[int] = mapped_column("estudio_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("estudio_usuario_id", ForeignKey("usuarios.usuario_id"), index=True)
    kind: Mapped[str] = mapped_column("estudio_tipo", String(20))
    minutes: Mapped[float] = mapped_column("estudio_minutos", Numeric(6, 1, asdecimal=False))
    day: Mapped[date] = mapped_column("estudio_dia", Date, default=date.today)
