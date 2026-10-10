from .. import models
from .common import first_name


def user_out(user: models.User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "first_name": first_name(user),
        "grade": user.grade,
        "section": user.section,
        "points": user.points,
        "streak": user.streak,
        "best_streak": user.best_streak,
    }


def session_out(token: str, user: models.User, streak_message: str | None) -> dict:
    return {"token": token, "user": user_out(user), "streak_message": streak_message}
