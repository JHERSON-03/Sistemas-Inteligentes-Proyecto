from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..config import POINTS_DAILY_CHALLENGE, WEEKLY_GOAL_HOURS
from ..database import get_db
from ..schemas import OptionIn
from ..security import current_user
from ..services import adaptive, gamification

router = APIRouter(prefix="/api", tags=["dashboard"])


def todays_challenge(db: Session) -> models.DailyChallenge:
    challenges = db.scalars(select(models.DailyChallenge).order_by(models.DailyChallenge.id)).all()
    return challenges[date.today().toordinal() % len(challenges)]


def ranking(db: Session, user: models.User) -> dict:
    classmates = db.scalars(
        select(models.User)
        .where(models.User.grade == user.grade, models.User.section == user.section)
        .order_by(models.User.points.desc(), models.User.id)
    ).all()
    rows = [
        {"position": i + 1, "name": u.full_name.split()[0] + " " + u.full_name.split()[-1][0] + ".",
         "points": u.points, "me": u.id == user.id}
        for i, u in enumerate(classmates)
    ]
    mine = next(r for r in rows if r["me"])
    return {"top": rows[:3], "me": mine, "total": len(rows)}


@router.get("/dashboard")
def dashboard(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    summaries = adaptive.all_routes(db, user)
    total_acts = sum(s["total"] for s in summaries)
    done_acts = sum(s["done"] for s in summaries)
    completed_routes = sum(1 for s in summaries if s["status"] == "completada")
    minutes = gamification.weekly_minutes_by_kind(db, user)
    hours = round(sum(minutes.values()) / 60, 1)

    challenge = todays_challenge(db)
    answered = db.scalar(
        select(models.ChallengeAnswer).where(models.ChallengeAnswer.user_id == user.id,
                                             models.ChallengeAnswer.day == date.today())
    )
    badges = gamification.achievements(db, user, completed_routes)

    return {
        "stats": {
            "streak": user.streak,
            "best_streak": user.best_streak,
            "points": user.points,
            "weekly_points": gamification.weekly_points(db, user),
            "week_hours": hours,
            "goal_hours": WEEKLY_GOAL_HOURS,
            "topics_done": done_acts,
            "topics_total": total_acts,
        },
        "week": gamification.week_streak(db, user),
        "courses": adaptive.course_progress(db, user),
        "next_step": adaptive.next_step(db, user),
        "challenge": {
            "id": challenge.id,
            "course": {"name": challenge.course.name, "color": challenge.course.color},
            "question": challenge.question,
            "options": challenge.options,
            "points": POINTS_DAILY_CHALLENGE,
            "answered": answered is not None,
            "was_correct": answered.correct if answered else None,
            "explanation": challenge.explanation if answered else None,
        },
        "achievements": [b for b in badges if b["unlocked"]][:3] or badges[:3],
        "ranking": ranking(db, user),
    }


@router.post("/challenge/{challenge_id}/answer")
def answer_challenge(challenge_id: int, data: OptionIn, user: models.User = Depends(current_user),
                     db: Session = Depends(get_db)):
    challenge = todays_challenge(db)
    if challenge.id != challenge_id:
        raise HTTPException(400, "Este reto ya no está disponible")
    already = db.scalar(select(func.count()).select_from(models.ChallengeAnswer).where(
        models.ChallengeAnswer.user_id == user.id, models.ChallengeAnswer.day == date.today()))
    if already:
        raise HTTPException(409, "Ya resolviste el reto de hoy. ¡Vuelve mañana!")
    correct = data.option == challenge.answer
    earned = gamification.add_points(user, POINTS_DAILY_CHALLENGE) if correct else 0
    db.add(models.ChallengeAnswer(user_id=user.id, challenge_id=challenge.id, day=date.today(), correct=correct))
    db.commit()
    return {"correct": correct, "answer": challenge.answer, "explanation": challenge.explanation,
            "points_earned": earned, "total_points": user.points}
