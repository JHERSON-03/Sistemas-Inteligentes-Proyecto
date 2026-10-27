import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import models
from ..core import rate_limit
from ..core.config import LIMIT_TUTOR_DAY, LIMIT_TUTOR_MINUTE, MINUTES_TUTOR_MESSAGE, POINTS_TUTOR_SESSION
from ..core.database import get_db
from ..core.security import current_user
from ..schemas import TutorMessageIn, TutorResetIn
from ..services import gamification
from ..services.tutor_ai import tutor_reply
from ..views import tutor as view
from ..views.common import first_name

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

# En la base de datos el emisor se guarda como "alumno" / "tutor"
DB_ROLE = {"user": "alumno", "assistant": "tutor"}

TUTOR_MINUTE_MESSAGE = "Estás enviando mensajes muy rápido. Espera {espera} y vuelve a escribir."
TUTOR_DAY_MESSAGE = "Llegaste al límite de mensajes con el tutor por hoy. Podrás volver a escribir en {espera}."


def session_messages(db: Session, user_id: int, session_id: str) -> list[models.TutorMessage]:
    return db.scalars(select(models.TutorMessage).where(
        models.TutorMessage.user_id == user_id, models.TutorMessage.session_id == session_id
    ).order_by(models.TutorMessage.id)).all()


@router.get("/session")
def current_session(course: str = "matematica", user: models.User = Depends(current_user),
                    db: Session = Depends(get_db)):
    """Retoma la última conversación no archivada del curso o abre una nueva."""
    last = db.scalar(select(models.TutorMessage).where(
        models.TutorMessage.user_id == user.id, models.TutorMessage.course == course,
        models.TutorMessage.archived.is_(False),
    ).order_by(models.TutorMessage.id.desc()))
    session_id = last.session_id if last else uuid.uuid4().hex
    msgs = session_messages(db, user.id, session_id) if last else []
    return view.session_out(session_id, course, first_name(user), msgs)


@router.post("/reset")
def reset(data: TutorResetIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Archiva la conversación del curso: deja de mostrarse, pero se conserva para analizar las preguntas."""
    db.execute(update(models.TutorMessage).where(
        models.TutorMessage.user_id == user.id, models.TutorMessage.course == data.course,
        models.TutorMessage.archived.is_(False),
    ).values(archived=True))
    db.commit()
    return view.reset_out(uuid.uuid4().hex, data.course, first_name(user))


# El límite por minuto va primero: si rechaza el mensaje, no se descuenta del límite diario
@router.post("/message", dependencies=[
    Depends(rate_limit.limit_by_user("tutor_minuto", LIMIT_TUTOR_MINUTE, TUTOR_MINUTE_MESSAGE)),
    Depends(rate_limit.limit_by_user("tutor_dia", LIMIT_TUTOR_DAY, TUTOR_DAY_MESSAGE)),
])
def send_message(data: TutorMessageIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    session_id = data.session_id or uuid.uuid4().hex
    previous = session_messages(db, user.id, session_id)
    history = [view.message_out(m) for m in previous]
    history.append({"role": "user", "content": data.message.strip()})

    reply, engine = tutor_reply(history, first_name(user), data.course)

    db.add(models.TutorMessage(user_id=user.id, session_id=session_id, course=data.course, role=DB_ROLE["user"],
                               content=data.message.strip()))
    db.add(models.TutorMessage(user_id=user.id, session_id=session_id, course=data.course, role=DB_ROLE["assistant"],
                               content=reply))
    earned = gamification.add_points(user, POINTS_TUTOR_SESSION) if not previous else 0
    gamification.log_study(db, user, "tutor", MINUTES_TUTOR_MESSAGE)
    db.commit()
    return view.reply_out(session_id, reply, engine, earned, user)
