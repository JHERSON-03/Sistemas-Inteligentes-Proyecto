from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.config import MINUTES_ASSESSMENT, POINTS_ASSESSMENT
from ..core.database import get_db
from ..core.security import current_user
from ..schemas import AssessmentAnswerIn
from ..services import gamification
from ..views import assessment as view

router = APIRouter(prefix="/api/assessments", tags=["autoevaluacion"])

CONFIDENCE_TIPS = {
    ("alta", False): "Estabas muy seguro: revisa con calma en qué paso cambió tu razonamiento.",
    ("baja", True): "¡Acertaste aunque dudabas! Confía más en tu razonamiento.",
}


@router.get("")
def list_assessments(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(models.Assessment).order_by(models.Assessment.id)).all()
    return view.assessment_list_out(items)


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(models.Assessment, assessment_id)
    if a is None:
        raise HTTPException(404, "Evaluación no encontrada")
    return view.assessment_out(a)


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
    return view.check_out(q, correct, CONFIDENCE_TIPS.get((data.confidence, correct)), earned, user)
