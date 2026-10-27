"""Límite de peticiones con los contadores guardados en la base de datos.

En Vercel cada petición puede atenderla una instancia distinta, así que los contadores no pueden vivir en memoria.
Se usa una ventana fija: el primer uso abre la ventana y los siguientes suman hasta que vence.
"""
import math
import random
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import case, delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from .. import models
from .config import SERVERLESS
from .database import IS_SQLITE, get_db
from .security import current_user

insert = sqlite_insert if IS_SQLITE else pg_insert
TABLE = models.RateLimit.__table__
# La ventana más larga es de un día: filas con más de dos días ya vencieron y se pueden borrar
STALE_AFTER = timedelta(days=2)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _wait_text(seconds: int) -> str:
    if seconds < 60:
        return _plural(seconds, "segundo")
    minutes = math.ceil(seconds / 60)
    if minutes < 60:
        return _plural(minutes, "minuto")
    return _plural(math.ceil(minutes / 60), "hora")


def _reject(message: str, started_at: datetime, window: int, now: datetime):
    seconds = max(1, math.ceil(window - (now - started_at).total_seconds()))
    raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, message.format(espera=_wait_text(seconds)),
                        headers={"Retry-After": str(seconds)})


def check(db: Session, key: str, limit: tuple[int, int], message: str):
    """Lanza 429 si la clave ya agotó su límite, sin sumar un uso."""
    maximum, window = limit
    now = _now()
    row = db.execute(select(TABLE.c.limite_conteo, TABLE.c.limite_inicio)
                     .where(TABLE.c.limite_clave == key)).first()
    if row and row.limite_conteo >= maximum and row.limite_inicio > now - timedelta(seconds=window):
        _reject(message, row.limite_inicio, window, now)


def hit(db: Session, key: str, limit: tuple[int, int], message: str):
    """Suma un uso a la clave y lanza 429 si se pasó del máximo. Es una sola consulta atómica."""
    maximum, window = limit
    now = _now()
    c = TABLE.c
    expired = c.limite_inicio <= now - timedelta(seconds=window)
    stmt = insert(TABLE).values(limite_clave=key, limite_inicio=now, limite_conteo=1)
    stmt = stmt.on_conflict_do_update(index_elements=[c.limite_clave], set_={
        c.limite_inicio: case((expired, now), else_=c.limite_inicio),
        c.limite_conteo: case((expired, 1), else_=c.limite_conteo + 1),
    }).returning(c.limite_conteo, c.limite_inicio)
    count, started_at = db.execute(stmt).one()
    if random.random() < 0.01:
        db.execute(delete(TABLE).where(c.limite_inicio < now - STALE_AFTER))
    db.commit()
    if count > maximum:
        _reject(message, started_at, window, now)


def reset(db: Session, key: str):
    """Borra el contador de la clave. Se guarda con el siguiente commit."""
    db.execute(delete(TABLE).where(TABLE.c.limite_clave == key))


def client_ip(request: Request) -> str:
    if SERVERLESS:
        # Vercel pone la IP real del visitante en estos encabezados
        forwarded = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip()
        if ip:
            return ip
    return request.client.host if request.client else "desconocida"


def limit_by_ip(name: str, limit: tuple[int, int], message: str):
    """Dependencia de FastAPI que cuenta las peticiones de cada IP."""
    def dependency(request: Request, db: Session = Depends(get_db)):
        hit(db, f"{name}:ip:{client_ip(request)}", limit, message)
    return dependency


def limit_by_user(name: str, limit: tuple[int, int], message: str):
    """Dependencia de FastAPI que cuenta las peticiones de cada alumno con sesión iniciada."""
    def dependency(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
        hit(db, f"{name}:usuario:{user.id}", limit, message)
    return dependency
