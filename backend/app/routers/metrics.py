import calendar
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..security import current_user
from ..services import adaptive, gamification
from ..services.tutor_ai import metrics_comment

router = APIRouter(prefix="/api", tags=["metricas"])

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
          "noviembre", "diciembre"]


@router.get("/metrics")
def metrics(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    courses = adaptive.course_progress(db, user)
    minutes = gamification.weekly_minutes_by_kind(db, user)

    progress = list(adaptive.progress_map(db, user).values())
    done = [p for p in progress if p.completed]
    first_try = sum(1 for p in done if p.correct_first_try)
    within_hint = sum(1 for p in done if p.attempts <= 2)
    answers = db.scalars(select(models.AssessmentAnswer).where(models.AssessmentAnswer.user_id == user.id)).all()
    graded = len(done) + len(answers)
    accuracy = (first_try + sum(a.correct for a in answers)) / graded if graded else 0.0
    tutor_sessions = db.scalar(select(func.count(func.distinct(models.TutorMessage.session_id))).where(
        models.TutorMessage.user_id == user.id)) or 0
    level = adaptive.autonomy_level(user, accuracy, len(done), tutor_sessions)

    weakest = min((c for c in courses if c["total"]), key=lambda c: c["percent"], default=None)
    comment = metrics_comment(user.full_name.split()[0], {
        "streak": user.streak,
        "hint_accuracy": within_hint / len(done) if done else None,
        "weakest": weakest["name"] if weakest else None,
    })

    today = date.today()
    first = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    studied = gamification.login_days(db, user, first, today.replace(day=last_day))
    avg = sum(c["percent"] for c in courses) / len(courses) if courses else 0

    return {
        "year": today.year,
        "status": "Vas muy bien" if avg >= 60 else ("Vas mejorando" if avg >= 30 else "¡Tú puedes!"),
        "courses": sorted(courses, key=lambda c: -c["percent"]),
        "time": [
            {"kind": "ruta", "label": "Rutas adaptativas", "hours": round(minutes["ruta"] / 60, 1), "color": "#284078"},
            {"kind": "tutor", "label": "Tutor IA", "hours": round(minutes["tutor"] / 60, 1), "color": "#A8A028"},
            {"kind": "autoevaluacion", "label": "Autoevaluación", "hours": round(minutes["autoevaluacion"] / 60, 1),
             "color": "#0F9F6E"},
        ],
        "streak": user.streak,
        "best_streak": user.best_streak,
        "points": user.points,
        "autonomy": {"level": level, "max": 4},
        "accuracy": round(accuracy * 100),
        "ai_comment": comment,
        "calendar": {
            "month": MONTHS[today.month - 1],
            "first_weekday": first.weekday(),
            "days": last_day,
            "today": today.day,
            "studied": sorted(d.day for d in studied),
        },
    }
