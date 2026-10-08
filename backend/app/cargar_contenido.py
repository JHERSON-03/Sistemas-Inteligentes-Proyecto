"""Agrega a la base de datos el contenido académico que falte (rutas, actividades, evaluación y retos).

Solo inserta lo que no existe: no modifica ni borra usuarios, progreso, mensajes ni contenido existente.

Uso (desde la carpeta backend):
    .venv\\Scripts\\python -m app.cargar_contenido            # muestra lo que agregaría (no escribe)
    .venv\\Scripts\\python -m app.cargar_contenido --aplicar  # lo guarda en la base de datos
"""
import difflib
import sys
import unicodedata

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
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


def main() -> None:
    apply = "--aplicar" in sys.argv
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        log = sync_content(db)
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
