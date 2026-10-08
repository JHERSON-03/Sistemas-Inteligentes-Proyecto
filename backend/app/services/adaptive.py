"""Motor adaptativo: progreso, nivel por desempeño, recomendaciones y autonomía."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def progress_map(db: Session, user: models.User) -> dict[int, models.ActivityProgress]:
    rows = db.scalars(select(models.ActivityProgress).where(models.ActivityProgress.user_id == user.id)).all()
    return {p.activity_id: p for p in rows}


def level_from_accuracy(accuracy: float | None) -> str:
    """El nivel sube o baja según los aciertos al primer intento."""
    if accuracy is None or accuracy < 0.5:
        return "básico"
    if accuracy < 0.8:
        return "intermedio"
    return "avanzado"


def route_summary(route: models.LearningRoute, progress: dict[int, models.ActivityProgress]) -> dict:
    total = len(route.activities)
    done = [progress[a.id] for a in route.activities if a.id in progress and progress[a.id].completed]
    first_try = sum(1 for p in done if p.correct_first_try)
    accuracy = first_try / len(done) if done else None
    pct = round(100 * len(done) / total) if total else 0
    status = "completada" if total and len(done) == total else ("en_progreso" if done else "pendiente")
    next_activity = next((a for a in route.activities if not (a.id in progress and progress[a.id].completed)), None)
    return {
        "id": route.id,
        "title": route.title,
        "description": route.description,
        "course": {"slug": route.course.slug, "name": route.course.name, "color": route.course.color},
        "minutes": route.minutes,
        "points": route.bonus_points,
        "total": total,
        "done": len(done),
        "percent": pct,
        "status": status,
        "level": level_from_accuracy(accuracy),
        "accuracy": accuracy,
        "next_activity_id": next_activity.id if next_activity else None,
        "remaining": total - len(done),
    }


def all_routes(db: Session, user: models.User) -> list[dict]:
    progress = progress_map(db, user)
    routes = db.scalars(select(models.LearningRoute).order_by(models.LearningRoute.id)).all()
    summaries = [route_summary(r, progress) for r in routes]
    rec = recommended_route_id(summaries)
    for s in summaries:
        s["recommended"] = s["id"] == rec
    return summaries


def course_progress(db: Session, user: models.User) -> list[dict]:
    summaries = all_routes(db, user)
    courses = db.scalars(select(models.Course).order_by(models.Course.id)).all()
    out = []
    for c in courses:
        rs = [s for s in summaries if s["course"]["slug"] == c.slug]
        total = sum(s["total"] for s in rs)
        done = sum(s["done"] for s in rs)
        out.append({
            "slug": c.slug, "name": c.name, "color": c.color, "icon": c.icon,
            "percent": round(100 * done / total) if total else 0, "done": done, "total": total,
        })
    return out


def recommended_route_id(summaries: list[dict]) -> int | None:
    """Recomienda una ruta no iniciada del curso con menor avance."""
    pending = [s for s in summaries if s["status"] == "pendiente"]
    if not pending:
        return None
    course_pct: dict[str, list[int]] = {}
    for s in summaries:
        course_pct.setdefault(s["course"]["slug"], []).append(s["percent"])
    return min(pending, key=lambda s: sum(course_pct[s["course"]["slug"]]) / len(course_pct[s["course"]["slug"]]))["id"]


def next_step(db: Session, user: models.User) -> dict | None:
    """Siguiente paso: ruta en progreso con menos actividades pendientes; si no, la recomendada."""
    summaries = all_routes(db, user)
    in_progress = [s for s in summaries if s["status"] == "en_progreso"]
    if in_progress:
        # Prioriza la ruta donde el desempeño es más bajo para reforzar
        target = min(in_progress, key=lambda s: ((s["accuracy"] or 0), -s["remaining"]))
    else:
        target = next((s for s in summaries if s.get("recommended")), None)
    if not target:
        return None
    return {
        "route_id": target["id"],
        "title": target["title"].split("(")[0].strip(),
        "course": target["course"],
        "remaining": target["remaining"],
        "next_activity_id": target["next_activity_id"],
    }


def autonomy_level(user: models.User, accuracy: float, activities_done: int, tutor_sessions: int) -> int:
    """Nivel de autonomía (1 a 4) combinando constancia, práctica y precisión."""
    score = 0
    score += min(user.streak, 10) / 10 * 30
    score += min(activities_done, 30) / 30 * 35
    score += accuracy * 25
    score += min(tutor_sessions, 5) / 5 * 10
    if score >= 75:
        return 4
    if score >= 50:
        return 3
    if score >= 25:
        return 2
    return 1
