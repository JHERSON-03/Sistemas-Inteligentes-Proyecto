from .. import models
from ..core.config import POINTS_TUTOR_SESSION

# Preguntas sugeridas por curso, alineadas con los temas de las rutas de 1ro de secundaria
SUGGESTIONS = {
    "historia": [
        "¿Quiénes construyeron Chan Chan?",
        "¿Por qué Caral es tan importante?",
        "¿Cómo vivían los primeros pobladores del Perú?",
    ],
    "ciencia": [
        "¿Cómo calculo la rapidez de un mototaxi?",
        "¿Qué partes tiene una célula?",
        "¿Por qué las plantas necesitan luz solar?",
    ],
    "matematica": [
        "¿Cómo resuelvo 2x + 3 = 11?",
        "¿Cuánto es (−4) + 9 y por qué?",
        "¿Cómo ubico números enteros en la recta?",
    ],
    "comunicacion": [
        "Ayúdame a mejorar mi cuento",
        "¿Cuándo lleva tilde una palabra aguda?",
        "¿Cómo encuentro la idea principal de un texto?",
    ],
}

# En la base de datos el emisor se guarda como "alumno" / "tutor"
API_ROLE = {"alumno": "user", "tutor": "assistant", "user": "user", "assistant": "assistant"}


def greeting(first_name: str) -> str:
    return (f"¡Hola, {first_name}! Soy tu tutor de aprendizaje autónomo. Estoy aquí para acompañarte sin hacer "
            "el trabajo por ti. ¿Sobre qué tema quieres reflexionar hoy?")


def message_out(m: models.TutorMessage) -> dict:
    return {"role": API_ROLE.get(m.role, "user"), "content": m.content}


def session_out(session_id: str, course: str, first_name: str, msgs: list[models.TutorMessage]) -> dict:
    return {
        "session_id": session_id,
        "course": course,
        "greeting": greeting(first_name),
        "messages": [message_out(m) for m in msgs],
        "suggestions": SUGGESTIONS.get(course, SUGGESTIONS["matematica"]),
        "points_per_session": POINTS_TUTOR_SESSION,
    }


def reset_out(session_id: str, course: str, first_name: str) -> dict:
    return {"session_id": session_id, "course": course, "greeting": greeting(first_name), "messages": []}


def reply_out(session_id: str, reply: str, engine: str, earned: int, user: models.User) -> dict:
    return {"session_id": session_id, "reply": reply, "engine": engine, "points_earned": earned,
            "total_points": user.points}
