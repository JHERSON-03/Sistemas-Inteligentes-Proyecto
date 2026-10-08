"""Agrega a la base de datos el contenido académico que falte (rutas, actividades, evaluación y retos).

Por defecto solo inserta lo que no existe: no modifica ni borra usuarios, progreso, mensajes ni contenido existente.

Uso (desde la carpeta backend):
    .venv\\Scripts\\python -m app.cargar_contenido            # muestra lo que agregaría (no escribe)
    .venv\\Scripts\\python -m app.cargar_contenido --aplicar  # lo guarda en la base de datos

Con --reemplazar además elimina el contenido que ya no está en seed.py (con su progreso y respuestas) y
actualiza el grado de los usuarios. Antes de borrar guarda un respaldo JSON en backend/respaldos/.
"""
import difflib
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .config import GRADE
from .database import Base, SessionLocal, engine
from .seed import ASSESSMENT, CHALLENGES, COURSES, ROUTES


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return " ".join("".join(c for c in text if unicodedata.category(c) != "Mn").split())


def _similar(a: str, b: str) -> bool:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio() >= 0.85


def sync_content(db: Session) -> list[str]:
    log: list[str] = []

    courses = {c.slug: c for c in db.scalars(select(models.Course))}
    for slug, name, color, icon in COURSES:
        if slug not in courses:
            courses[slug] = models.Course(slug=slug, name=name, color=color, icon=icon)
            db.add(courses[slug])
            log.append(f"+ curso {name}")
    db.flush()

    for slug, title, desc, minutes, bonus, acts in ROUTES:
        route = db.scalar(select(models.LearningRoute).where(
            models.LearningRoute.course_id == courses[slug].id, func.lower(models.LearningRoute.title) == title.lower()))
        if route is None:
            route = models.LearningRoute(course_id=courses[slug].id, title=title, description=desc, minutes=minutes,
                                         bonus_points=bonus)
            db.add(route)
            db.flush()
            log.append(f"+ ruta [{courses[slug].name}] {title}")
        existing = list(route.activities)
        next_order = max((a.order for a in existing), default=0) + 1
        for atitle, q, opts, ans, hint, expl in acts:
            if any(_similar(a.title, atitle) for a in existing):
                continue
            act = models.Activity(route_id=route.id, order=next_order, title=atitle, question=q, options=opts,
                                  answer=ans, hint=hint, explanation=expl)
            db.add(act)
            existing.append(act)
            log.append(f"    + actividad {next_order}. {atitle}  (ruta: {title})")
            next_order += 1
    db.flush()

    slug, title, questions = ASSESSMENT
    assessment = db.scalar(select(models.Assessment).where(func.lower(models.Assessment.title) == title.lower()))
    if assessment is None:
        assessment = models.Assessment(course_id=courses[slug].id, title=title)
        db.add(assessment)
        db.flush()
        log.append(f"+ autoevaluación {title}")
    current = list(assessment.questions)
    next_order = max((q.order for q in current), default=0) + 1
    for situation, opts, ans, ok, ko in questions:
        if any(_similar(q.situation, situation) for q in current):
            continue
        db.add(models.AssessmentQuestion(assessment_id=assessment.id, order=next_order, situation=situation,
                                         options=[{"texto": t, "razon": r} for t, r in opts], answer=ans,
                                         feedback_ok=ok, feedback_ko=ko))
        log.append(f"    + pregunta {next_order}. {situation[:70]}…")
        next_order += 1

    challenges = list(db.scalars(select(models.DailyChallenge)))
    for slug, q, opts, ans, expl in CHALLENGES:
        if any(_similar(c.question, q) for c in challenges):
            continue
        ch = models.DailyChallenge(course_id=courses[slug].id, question=q, options=opts, answer=ans, explanation=expl)
        db.add(ch)
        challenges.append(ch)
        log.append(f"+ reto [{courses[slug].name}] {q}")
    return log


def _row(obj) -> dict:
    return {c.key: getattr(obj, c.key) for c in obj.__mapper__.column_attrs}


def remove_obsolete(db: Session, backup: dict) -> list[str]:
    """Quita el contenido que ya no está en seed.py (y el progreso/respuestas ligados), guardando un respaldo."""
    log: list[str] = []
    route_titles = {title.lower() for _, title, *_ in ROUTES}
    for route in db.scalars(select(models.LearningRoute)).all():
        if route.title.lower() in route_titles:
            continue
        act_ids = [a.id for a in route.activities]
        progress = db.scalars(select(models.ActivityProgress).where(
            models.ActivityProgress.activity_id.in_(act_ids))).all() if act_ids else []
        backup["progreso_actividad"] += [_row(p) for p in progress]
        backup["actividades"] += [_row(a) for a in route.activities]
        backup["rutas"].append(_row(route))
        for p in progress:
            db.delete(p)
        for a in route.activities:
            db.delete(a)
        db.delete(route)
        log.append(f"- ruta {route.title} ({len(act_ids)} actividades, {len(progress)} progresos)")

    _, assessment_title, _ = ASSESSMENT
    for a in db.scalars(select(models.Assessment)).all():
        if a.title.lower() == assessment_title.lower():
            continue
        q_ids = [q.id for q in a.questions]
        answers = db.scalars(select(models.AssessmentAnswer).where(
            models.AssessmentAnswer.question_id.in_(q_ids))).all() if q_ids else []
        backup["respuestas_evaluacion"] += [_row(x) for x in answers]
        backup["preguntas_evaluacion"] += [_row(q) for q in a.questions]
        backup["evaluaciones"].append(_row(a))
        for x in answers:
            db.delete(x)
        for q in a.questions:
            db.delete(q)
        db.delete(a)
        log.append(f"- autoevaluación {a.title} ({len(q_ids)} preguntas, {len(answers)} respuestas)")

    for ch in db.scalars(select(models.DailyChallenge)).all():
        if any(_similar(ch.question, q) for _, q, *_ in CHALLENGES):
            continue
        answers = db.scalars(select(models.ChallengeAnswer).where(models.ChallengeAnswer.challenge_id == ch.id)).all()
        backup["respuestas_reto"] += [_row(x) for x in answers]
        backup["retos_diarios"].append(_row(ch))
        for x in answers:
            db.delete(x)
        db.delete(ch)
        log.append(f"- reto {ch.question} ({len(answers)} respuestas)")

    for u in db.scalars(select(models.User).where(models.User.grade != GRADE)).all():
        backup["usuarios_grado"].append({"id": u.id, "usuario": u.username, "grado": u.grade})
        log.append(f"~ usuario {u.username}: grado {u.grade} → {GRADE}")
        u.grade = GRADE
    db.flush()
    return log


def main() -> None:
    apply = "--aplicar" in sys.argv
    replace = "--reemplazar" in sys.argv
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        backup = {k: [] for k in ("rutas", "actividades", "progreso_actividad", "evaluaciones",
                                  "preguntas_evaluacion", "respuestas_evaluacion", "retos_diarios",
                                  "respuestas_reto", "usuarios_grado")}
        log = remove_obsolete(db, backup) if replace else []
        if apply and log:
            folder = Path(__file__).resolve().parent.parent / "respaldos"
            folder.mkdir(exist_ok=True)
            path = folder / f"respaldo_{datetime.now():%Y%m%d_%H%M%S}.json"
            path.write_text(json.dumps(backup, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            print(f"Respaldo de lo eliminado: {path}\n")
        log += sync_content(db)
        print("\n".join(log) if log else "No falta contenido: la base ya está completa.")
        if apply and log:
            db.commit()
            print(f"\n✔ Guardado: {len(log)} elementos agregados.")
        else:
            db.rollback()
            if log:
                print("\n(Simulación: no se guardó nada. Ejecuta con --aplicar para guardarlo.)")


if __name__ == "__main__":
    main()
