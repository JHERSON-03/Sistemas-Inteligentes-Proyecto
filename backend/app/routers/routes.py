from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import MINUTES_ACTIVITY, POINTS_ACTIVITY
from ..database import get_db
from ..schemas import OptionIn
from ..security import current_user
from ..services import adaptive, gamification

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
    summary = adaptive.route_summary(route, progress)
    summary["activities"] = [
        {
            "id": a.id, "order": a.order, "title": a.title, "question": a.question, "options": a.options,
            "completed": a.id in progress and progress[a.id].completed,
            "attempts": progress[a.id].attempts if a.id in progress else 0,
        }
        for a in route.activities
    ]
    return summary


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
        return {"correct": True, "already_completed": True, "explanation": activity.explanation, "points_earned": 0,
                "total_points": user.points}

    prog.attempts += 1
    correct = data.option == activity.answer
    earned = 0
    route_completed = False
    if correct:
        prog.completed = True
        prog.correct_first_try = prog.attempts == 1
        prog.completed_at = datetime.utcnow()
        earned += gamification.add_points(user, POINTS_ACTIVITY)
        gamification.log_study(db, user, "rutas", MINUTES_ACTIVITY)
        db.flush()
        route = activity.route
        summary = adaptive.route_summary(route, adaptive.progress_map(db, user))
        if summary["status"] == "completada":
            route_completed = True
            earned += gamification.add_points(user, route.bonus_points)
    db.commit()

    summary = adaptive.route_summary(activity.route, adaptive.progress_map(db, user))
    return {
        "correct": correct,
        "hint": None if correct else activity.hint,
        "explanation": activity.explanation if correct else None,
        "points_earned": earned,
        "route_completed": route_completed,
        "total_points": user.points,
        "route": summary,
    }
