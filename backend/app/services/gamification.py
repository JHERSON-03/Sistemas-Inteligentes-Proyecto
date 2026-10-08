"""Racha, puntos, tiempo de estudio y logros."""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models


def register_login(db: Session, user: models.User, today: date | None = None) -> dict:
    """Suma un día de racha si ingresó ayer; si faltó un día la racha se reinicia."""
    today = today or date.today()
    message = None
    if user.last_login == today:
        pass
    elif user.last_login == today - timedelta(days=1):
        user.streak += 1
    else:
        if user.last_login is not None and user.streak > 0:
            message = "Tu racha se reinició, ¡pero hoy empiezas una nueva! 💪"
        user.streak = 1
    user.best_streak = max(user.best_streak, user.streak)
    user.last_login = today
    exists = db.scalar(select(models.LoginDay).where(models.LoginDay.user_id == user.id, models.LoginDay.day == today))
    if not exists:
        db.add(models.LoginDay(user_id=user.id, day=today))
    db.commit()
    return {"streak": user.streak, "message": message}


def add_points(user: models.User, amount: int) -> int:
    user.points += amount
    return amount


def log_study(db: Session, user: models.User, kind: str, minutes: float) -> None:
    db.add(models.StudyLog(user_id=user.id, kind=kind, minutes=minutes, day=date.today()))


def week_start(today: date | None = None) -> date:
    today = today or date.today()
    return today - timedelta(days=today.weekday())


def weekly_minutes_by_kind(db: Session, user: models.User) -> dict[str, float]:
    rows = db.execute(
        select(models.StudyLog.kind, func.sum(models.StudyLog.minutes))
        .where(models.StudyLog.user_id == user.id, models.StudyLog.day >= week_start())
        .group_by(models.StudyLog.kind)
    ).all()
    data = {"ruta": 0.0, "tutor": 0.0, "autoevaluacion": 0.0}
    data.update({k: float(v or 0) for k, v in rows})
    return data


def weekly_points(db: Session, user: models.User) -> int:
    """Puntos de la semana estimados a partir de lo realizado desde el lunes."""
    start = week_start()
    acts = db.scalar(
        select(func.count()).select_from(models.ActivityProgress).where(
            models.ActivityProgress.user_id == user.id,
            models.ActivityProgress.completed.is_(True),
            func.date(models.ActivityProgress.completed_at) >= start,
        )
    ) or 0
    asses = db.scalar(
        select(func.count()).select_from(models.AssessmentAnswer).where(
            models.AssessmentAnswer.user_id == user.id,
            models.AssessmentAnswer.correct.is_(True),
            func.date(models.AssessmentAnswer.created_at) >= start,
        )
    ) or 0
    challenges = db.scalar(
        select(func.count()).select_from(models.ChallengeAnswer).where(
            models.ChallengeAnswer.user_id == user.id,
            models.ChallengeAnswer.correct.is_(True),
            models.ChallengeAnswer.day >= start,
        )
    ) or 0
    sessions = db.scalar(
        select(func.count(func.distinct(models.TutorMessage.session_id))).where(
            models.TutorMessage.user_id == user.id, func.date(models.TutorMessage.created_at) >= start
        )
    ) or 0
    return acts * 10 + asses * 10 + challenges * 10 + sessions * 5


def login_days(db: Session, user: models.User, start: date, end: date) -> set[date]:
    rows = db.scalars(
        select(models.LoginDay.day).where(
            models.LoginDay.user_id == user.id, models.LoginDay.day >= start, models.LoginDay.day <= end
        )
    ).all()
    return set(rows)


def week_streak(db: Session, user: models.User) -> list[dict]:
    """Siete círculos L M M J V S D con estado: done / today / missed / future."""
    today = date.today()
    start = week_start(today)
    days = login_days(db, user, start, start + timedelta(days=6))
    labels = ["L", "M", "M", "J", "V", "S", "D"]
    out = []
    for i, label in enumerate(labels):
        d = start + timedelta(days=i)
        if d == today:
            state = "today"
        elif d > today:
            state = "future"
        else:
            state = "done" if d in days else "missed"
        out.append({"label": label, "date": d.isoformat(), "state": state, "studied": d in days})
    return out


def achievements(db: Session, user: models.User, completed_routes: int) -> list[dict]:
    tutor_sessions = db.scalar(
        select(func.count(func.distinct(models.TutorMessage.session_id))).where(models.TutorMessage.user_id == user.id)
    ) or 0
    catalog = [
        ("primera-ruta", "Primera ruta completada", "route", completed_routes >= 1),
        ("racha-5", "Racha de 5 días", "flame", user.best_streak >= 5),
        ("puntos-100", "100 puntos", "star", user.points >= 100),
        ("puntos-500", "500 puntos", "star", user.points >= 500),
        ("tutor-3", "3 sesiones con el tutor", "bot", tutor_sessions >= 3),
        ("racha-10", "Racha de 10 días", "flame", user.best_streak >= 10),
    ]
    return [{"id": i, "name": n, "icon": ic, "unlocked": ok} for i, n, ic, ok in catalog]
