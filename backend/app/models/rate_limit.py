from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class RateLimit(Base):
    """Contador de peticiones de una clave (ej. "tutor_minuto:usuario:7") dentro de su ventana de tiempo."""
    __tablename__ = "limites_peticion"
    key: Mapped[str] = mapped_column("limite_clave", String(150), primary_key=True)
    started_at: Mapped[datetime] = mapped_column("limite_inicio", DateTime)
    count: Mapped[int] = mapped_column("limite_conteo", Integer)
