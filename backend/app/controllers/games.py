from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..core.database import get_db
from ..core.security import current_user
from ..schemas import CatchCheckIn, CatchResultIn
from ..services import gamification
from ..services import juego_atrapa as atrapa
from ..views import games as view

router = APIRouter(prefix="/api/juegos/atrapa", tags=["juegos"])

LIMIT_REACHED = f"Ya jugaste tus {atrapa.PARTIDAS_POR_DIA} partidas de hoy. ¡Vuelve mañana!"


def plays_left(db: Session, user: models.User) -> int:
    today = db.scalar(select(func.count()).select_from(models.GameMatch).where(
        models.GameMatch.user_id == user.id, models.GameMatch.game == atrapa.JUEGO,
        models.GameMatch.played_at >= atrapa.inicio_del_dia())) or 0
    return max(0, atrapa.PARTIDAS_POR_DIA - today)


@router.get("/ronda")
def new_round(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    left = plays_left(db, user)
    if not left:
        raise HTTPException(429, LIMIT_REACHED)
    return {**atrapa.nueva_ronda(user.id), "plays_left": left}


@router.post("/verificar")
def check_bubble(data: CatchCheckIn, user: models.User = Depends(current_user)):
    """Efecto verde/rojo al atrapar una burbuja. No guarda nada: el puntaje oficial se calcula en /resultado."""
    try:
        ronda = atrapa.abrir_ronda(data.ronda_id, user.id, terminada=False)
    except atrapa.RondaInvalida as e:
        raise HTTPException(400, str(e))
    return {"correct": atrapa.es_correcto(ronda, data.indice)}


@router.post("/resultado")
def save_result(data: CatchResultIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        ronda = atrapa.abrir_ronda(data.ronda_id, user.id)
    except atrapa.RondaInvalida as e:
        raise HTTPException(400, str(e))
    # Una ronda solo se puede guardar una vez: si ya hay una partida posterior a su inicio, es un reenvío
    started = datetime.fromtimestamp(ronda["inicio"], timezone.utc).replace(tzinfo=None)
    repeated = db.scalar(select(func.count()).select_from(models.GameMatch).where(
        models.GameMatch.user_id == user.id, models.GameMatch.game == atrapa.JUEGO,
        models.GameMatch.played_at >= started))
    if repeated:
        raise HTTPException(409, "Esta ronda ya fue registrada")
    left = plays_left(db, user)
    if not left:
        raise HTTPException(429, LIMIT_REACHED)

    result = atrapa.calificar(ronda, data.clicados)
    match = models.GameMatch(user_id=user.id, game=atrapa.JUEGO, prompt=ronda["consigna"]["texto"],
                             score=result["puntaje"], hits=result["aciertos"], misses=result["errores"])
    db.add(match)
    earned = gamification.add_points(user, atrapa.puntos_plataforma(result["puntaje"]))
    db.commit()
    return view.result_out(match, result["correctas"], earned, user, left - 1)


@router.get("/ranking")
def ranking(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    best = func.max(models.GameMatch.score).label("best")
    rows = db.execute(
        select(models.User, best)
        .join(models.GameMatch, models.GameMatch.user_id == models.User.id)
        .where(models.GameMatch.game == atrapa.JUEGO)
        .group_by(models.User.id)
        .order_by(best.desc(), models.User.id)
        .limit(10)
    ).all()
    return view.ranking_out(rows, user, plays_left(db, user))
