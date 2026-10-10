from .. import models
from .common import course_out


def option_out(opt) -> dict:
    """Las opciones se guardan como {"texto", "razon"}; también acepta texto plano."""
    if isinstance(opt, str):
        return {"text": opt, "reason": ""}
    return {"text": opt.get("texto", opt.get("text", "")), "reason": opt.get("razon", opt.get("reason", ""))}


def assessment_list_out(items: list[models.Assessment]) -> list[dict]:
    return [{"id": a.id, "title": a.title, "course": course_out(a.course), "questions": len(a.questions)}
            for a in items]


def assessment_out(a: models.Assessment) -> dict:
    return {
        "id": a.id, "title": a.title,
        "course": course_out(a.course),
        "questions": [{"id": q.id, "order": q.order, "situation": q.situation,
                       "options": [option_out(o) for o in q.options]}
                      for q in a.questions],
    }


def check_out(q: models.AssessmentQuestion, correct: bool, confidence_tip: str | None, earned: int,
              user: models.User) -> dict:
    return {
        "correct": correct,
        "answer": q.answer,
        "feedback": q.feedback_ok if correct else q.feedback_ko,
        "confidence_tip": confidence_tip,
        "points_earned": earned,
        "total_points": user.points,
    }
