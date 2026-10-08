import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import MINUTES_TUTOR_MESSAGE, POINTS_TUTOR_SESSION
from ..database import get_db
from ..schemas import TutorMessageIn, TutorResetIn
from ..security import current_user
from ..services import gamification
from ..services.tutor_ai import tutor_reply

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

SUGGESTIONS = [
    "¿Cómo resuelvo x² − 5x + 6 = 0?",
    "¿Qué causó la Guerra del Pacífico?",
    "Ayúdame a mejorar mi resumen",
]


def greeting(first_name: str) -> str:
    return (f"¡Hola, {first_name}! Soy tu tutor de aprendizaje autónomo. Estoy aquí para acompañarte sin hacer "
            "el trabajo por ti. ¿Sobre qué tema quieres reflexionar hoy?")


# En la base de datos el emisor se guarda como "alumno" / "tutor"
DB_ROLE = {"user": "alumno", "assistant": "tutor"}
API_ROLE = {"alumno": "user", "tutor": "assistant", "user": "user", "assistant": "assistant"}


def as_api(m: models.TutorMessage) -> dict:
    return {"role": API_ROLE.get(m.role, "user"), "content": m.content}


def session_messages(db: Session, user_id: int, session_id: str) -> list[models.TutorMessage]:
    return db.scalars(select(models.TutorMessage).where(
        models.TutorMessage.user_id == user_id, models.TutorMessage.session_id == session_id
    ).order_by(models.TutorMessage.id)).all()


@router.get("/session")
def current_session(course: str = "matematica", user: models.User = Depends(current_user),
                    db: Session = Depends(get_db)):
    """Retoma la última conversación del curso o abre una nueva."""
    last = db.scalar(select(models.TutorMessage).where(
        models.TutorMessage.user_id == user.id, models.TutorMessage.course == course
    ).order_by(models.TutorMessage.id.desc()))
    session_id = last.session_id if last else uuid.uuid4().hex
    msgs = session_messages(db, user.id, session_id) if last else []
    return {
        "session_id": session_id,
        "course": course,
        "greeting": greeting(user.full_name.split()[0]),
        "messages": [as_api(m) for m in msgs],
        "suggestions": SUGGESTIONS,
        "points_per_session": POINTS_TUTOR_SESSION,
    }


@router.post("/reset")
def reset(data: TutorResetIn, user: models.User = Depends(current_user)):
    return {"session_id": uuid.uuid4().hex, "course": data.course, "greeting": greeting(user.full_name.split()[0]),
            "messages": []}


@router.post("/message")
def send_message(data: TutorMessageIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    session_id = data.session_id or uuid.uuid4().hex
    previous = session_messages(db, user.id, session_id)
    history = [as_api(m) for m in previous]
    history.append({"role": "user", "content": data.message.strip()})

    reply, engine = tutor_reply(history, user.full_name.split()[0], data.course)

    db.add(models.TutorMessage(user_id=user.id, session_id=session_id, course=data.course, role=DB_ROLE["user"],
                               content=data.message.strip()))
    db.add(models.TutorMessage(user_id=user.id, session_id=session_id, course=data.course, role=DB_ROLE["assistant"],
                               content=reply))
    earned = gamification.add_points(user, POINTS_TUTOR_SESSION) if not previous else 0
    gamification.log_study(db, user, "tutor", MINUTES_TUTOR_MESSAGE)
    db.commit()
    return {"session_id": session_id, "reply": reply, "engine": engine, "points_earned": earned,
            "total_points": user.points}
