from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class Course(Base):
    __tablename__ = "cursos"
    id: Mapped[int] = mapped_column("curso_id", primary_key=True)
    slug: Mapped[str] = mapped_column("curso_codigo", String(30), unique=True)
    name: Mapped[str] = mapped_column("curso_nombre", String(60))
    color: Mapped[str] = mapped_column("curso_color", String(7))
    icon: Mapped[str] = mapped_column("curso_icono", String(30))
