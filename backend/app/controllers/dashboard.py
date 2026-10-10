from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..core.config import POINTS_DAILY_CHALLENGE
from ..core.database import get_db
from ..core.security import current_user
from ..schemas import OptionIn
from ..services import adaptive, gamification
from ..views import dashboard as view

router = APIRouter(prefix="/api", tags=["dashboard"])


def todays_challenge(db: Session) -> models.DailyChallenge:
    challenges = db.scalars(select(models.DailyChallenge).order_by(models.DailyChallenge.id)).all()
    return challenges[date.today().toordinal() % len(challenges)]


def classmates(db: Session, user: models.User) -> list[models.User]:
    return db.scalars(
        select(models.User)
        .where(models.User.grade == user.grade, models.User.section == user.section)
        .order_by(models.User.points.desc(), models.User.id)
    ).all()


@router.get("/dashboard")
def dashboard(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    summaries = adaptive.all_routes(db, user)
    completed_routes = sum(1 for s in summaries if s["status"] == "completada")
    minutes = gamification.weekly_minutes_by_kind(db, user)

    challenge = todays_challenge(db)
    answered = db.scalar(
        select(models.ChallengeAnswer).where(models.ChallengeAnswer.user_id == user.id,
                                             models.ChallengeAnswer.day == date.today())
    )

    return view.dashboard_out(
        user,
        weekly_points=gamification.weekly_points(db, user),
        week_hours=round(sum(minutes.values()) / 60, 1),
        topics_done=sum(s["done"] for s in summaries),
        topics_total=sum(s["total"] for s in summaries),
        week=gamification.week_streak(db, user),
        courses=adaptive.course_progress(db, user),
        next_step=adaptive.next_step(db, user),
        challenge=view.challenge_out(challenge, answered),
        badges=gamification.achievements(db, user, completed_routes),
        ranking=view.ranking_out(classmates(db, user), user),
    )


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
    return view.challenge_answer_out(challenge, correct, earned, user)
