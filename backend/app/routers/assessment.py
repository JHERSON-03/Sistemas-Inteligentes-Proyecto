from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import MINUTES_ASSESSMENT, POINTS_ASSESSMENT
from ..database import get_db
from ..schemas import AssessmentAnswerIn
from ..security import current_user
from ..services import gamification

router = APIRouter(prefix="/api/assessments", tags=["autoevaluacion"])

CONFIDENCE_TIPS = {
    ("muy", False): "Estabas muy seguro: revisa con calma en qué paso cambió tu razonamiento.",
    ("nada", True): "¡Acertaste aunque dudabas! Confía más en tu razonamiento.",
}


@router.get("")
def list_assessments(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(models.Assessment).order_by(models.Assessment.id)).all()
    return [{"id": a.id, "title": a.title, "course": {"slug": a.course.slug, "name": a.course.name,
                                                       "color": a.course.color}, "questions": len(a.questions)}
            for a in items]


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(models.Assessment, assessment_id)
    if a is None:
        raise HTTPException(404, "Evaluación no encontrada")
    return {
        "id": a.id, "title": a.title,
        "course": {"slug": a.course.slug, "name": a.course.name, "color": a.course.color},
        "questions": [{"id": q.id, "order": q.order, "situation": q.situation, "options": q.options}
                      for q in a.questions],
    }


@router.post("/questions/{question_id}/check")
def check_answer(question_id: int, data: AssessmentAnswerIn, user: models.User = Depends(current_user),
                 db: Session = Depends(get_db)):
    q = db.get(models.AssessmentQuestion, question_id)
    if q is None or data.option >= len(q.options):
        raise HTTPException(404, "Pregunta no encontrada")
    correct = data.option == q.answer
    earned = gamification.add_points(user, POINTS_ASSESSMENT) if correct else 0
    db.add(models.AssessmentAnswer(user_id=user.id, question_id=q.id, selected=data.option,
                                   confidence=data.confidence, correct=correct))
    gamification.log_study(db, user, "autoevaluacion", MINUTES_ASSESSMENT)
    db.commit()
    return {
        "correct": correct,
        "answer": q.answer,
        "feedback": q.feedback_ok if correct else q.feedback_ko,
        "confidence_tip": CONFIDENCE_TIPS.get((data.confidence, correct)),
        "points_earned": earned,
        "total_points": user.points,
    }
