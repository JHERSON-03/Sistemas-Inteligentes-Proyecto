from .. import models
from ..core.config import POINTS_DAILY_CHALLENGE, WEEKLY_GOAL_HOURS


def ranking_out(classmates: list[models.User], user: models.User) -> dict:
    rows = [
        {"position": i + 1, "name": u.full_name.split()[0] + " " + u.full_name.split()[-1][0] + ".",
         "points": u.points, "me": u.id == user.id}
        for i, u in enumerate(classmates)
    ]
    mine = next(r for r in rows if r["me"])
    return {"top": rows[:3], "me": mine, "total": len(rows)}


def challenge_out(challenge: models.DailyChallenge, answered: models.ChallengeAnswer | None) -> dict:
    return {
        "id": challenge.id,
        "course": {"name": challenge.course.name, "color": challenge.course.color},
        "question": challenge.question,
        "options": challenge.options,
        "points": POINTS_DAILY_CHALLENGE,
        "answered": answered is not None,
        "was_correct": answered.correct if answered else None,
        "explanation": challenge.explanation if answered else None,
    }


def dashboard_out(user: models.User, *, weekly_points: int, week_hours: float, topics_done: int, topics_total: int,
                  week: list, courses: list, next_step, challenge: dict, badges: list, ranking: dict) -> dict:
    return {
        "stats": {
            "streak": user.streak,
            "best_streak": user.best_streak,
            "points": user.points,
            "weekly_points": weekly_points,
            "week_hours": week_hours,
            "goal_hours": WEEKLY_GOAL_HOURS,
            "topics_done": topics_done,
            "topics_total": topics_total,
        },
        "week": week,
        "courses": courses,
        "next_step": next_step,
        "challenge": challenge,
        "achievements": [b for b in badges if b["unlocked"]][:3] or badges[:3],
        "ranking": ranking,
    }


def challenge_answer_out(challenge: models.DailyChallenge, correct: bool, earned: int, user: models.User) -> dict:
    return {"correct": correct, "answer": challenge.answer, "explanation": challenge.explanation,
            "points_earned": earned, "total_points": user.points}
