from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class TutorMessage(Base):
    __tablename__ = "mensajes_tutor"
    id: Mapped[int] = mapped_column("mensaje_id", primary_key=True)
    user_id: Mapped[int] = mapped_column("mensaje_usuario_id", ForeignKey("usuarios.usuario_id"), index=True)
    session_id: Mapped[str] = mapped_column("mensaje_sesion_id", String(40), index=True)
    course: Mapped[str] = mapped_column("mensaje_curso", String(30))
    role: Mapped[str] = mapped_column("mensaje_emisor", String(10))  # "alumno" | "tutor"
    content: Mapped[str] = mapped_column("mensaje_contenido", Text)
    # Al reiniciar el diálogo la conversación se archiva (no se borra) para poder analizar las preguntas
    archived: Mapped[bool] = mapped_column("mensaje_archivado", Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column("mensaje_creado_en", DateTime, default=datetime.utcnow,
                                                 server_default=func.now())
