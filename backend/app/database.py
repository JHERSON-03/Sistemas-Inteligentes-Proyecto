from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL


def _normalize(url: str) -> str:
    """Acepta la URL tal como la copia Supabase (postgresql://...) y usa el driver psycopg 3."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


DB_URL = _normalize(DATABASE_URL)
IS_SQLITE = DB_URL.startswith("sqlite")

if IS_SQLITE:
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    # Supabase cierra conexiones inactivas: pre_ping las revisa antes de usarlas.
    # prepare_threshold=None evita errores con el pooler de Supabase (modo transacción).
    engine = create_engine(
        DB_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_recycle=300,
        connect_args={"prepare_threshold": None, "connect_timeout": 10},
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
