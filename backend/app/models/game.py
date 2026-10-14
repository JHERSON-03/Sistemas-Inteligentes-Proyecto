from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .user import User


class GameMatch(Base):
    """Una partida terminada de un minijuego (ej. "Atrapa la respuesta")."""
    __tablename__ = "partidas_juego"
    id: Mapped[int] = mapped_column("partida_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("partida_usuario_id", ForeignKey("usuarios.usuario_id"), index=True)
    game: Mapped[str] = mapped_column("partida_juego", String(30))
    prompt: Mapped[str] = mapped_column("partida_consigna", String(120))
    score: Mapped[int] = mapped_column("partida_puntaje", Integer)
    hits: Mapped[int] = mapped_column("partida_aciertos", Integer)
    misses: Mapped[int] = mapped_column("partida_errores", Integer)
    played_at: Mapped[datetime] = mapped_column("partida_fecha", DateTime, default=datetime.utcnow,
                                                server_default=func.now())
    user: Mapped[User] = relationship()
