from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.config import MINUTES_ACTIVITY, POINTS_ACTIVITY
from ..core.database import get_db
from ..core.security import current_user
from ..schemas import OptionIn
from ..services import adaptive, gamification
from ..views import routes as view

router = APIRouter(prefix="/api", tags=["rutas"])


@router.get("/routes")
def list_routes(course: str | None = None, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    routes = adaptive.all_routes(db, user)
    if course:
        routes = [r for r in routes if r["course"]["slug"] == course]
    return routes


@router.get("/routes/{route_id}")
def route_detail(route_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    route = db.get(models.LearningRoute, route_id)
    if route is None:
        raise HTTPException(404, "Ruta no encontrada")
    progress = adaptive.progress_map(db, user)
    return view.route_detail_out(route, adaptive.route_summary(route, progress), progress)


@router.post("/activities/{activity_id}/answer")
def answer_activity(activity_id: int, data: OptionIn, user: models.User = Depends(current_user),
                    db: Session = Depends(get_db)):
    activity = db.get(models.Activity, activity_id)
    if activity is None or data.option >= len(activity.options):
        raise HTTPException(404, "Actividad no encontrada")
    prog = db.scalar(select(models.ActivityProgress).where(
        models.ActivityProgress.user_id == user.id, models.ActivityProgress.activity_id == activity_id))
    if prog is None:
        prog = models.ActivityProgress(user_id=user.id, activity_id=activity_id, attempts=0)
        db.add(prog)
    if prog.completed:
        return view.already_completed_out(activity, user)

    prog.attempts += 1
    correct = data.option == activity.answer
    earned = 0
    route_completed = False
    if correct:
        prog.completed = True
        prog.correct_first_try = prog.attempts == 1
        prog.completed_at = datetime.utcnow()
        earned += gamification.add_points(user, POINTS_ACTIVITY)
        gamification.log_study(db, user, "ruta", MINUTES_ACTIVITY)
        db.flush()
        route = activity.route
        summary = adaptive.route_summary(route, adaptive.progress_map(db, user))
        if summary["status"] == "completada":
            route_completed = True
            earned += gamification.add_points(user, route.bonus_points)
    db.commit()

    summary = adaptive.route_summary(activity.route, adaptive.progress_map(db, user))
    return view.answer_out(activity, correct, earned, route_completed, user, summary)
