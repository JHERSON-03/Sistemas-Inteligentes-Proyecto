from .. import models


def route_detail_out(route: models.LearningRoute, summary: dict, progress: dict) -> dict:
    summary["activities"] = [
        {
            "id": a.id, "order": a.order, "title": a.title, "question": a.question, "options": a.options,
            "completed": a.id in progress and progress[a.id].completed,
            "attempts": progress[a.id].attempts if a.id in progress else 0,
        }
        for a in route.activities
    ]
    return summary


def already_completed_out(activity: models.Activity, user: models.User) -> dict:
    return {"correct": True, "already_completed": True, "explanation": activity.explanation, "points_earned": 0,
            "total_points": user.points}


def answer_out(activity: models.Activity, correct: bool, earned: int, route_completed: bool, user: models.User,
               summary: dict) -> dict:
    return {
        "correct": correct,
        "hint": None if correct else activity.hint,
        "explanation": activity.explanation if correct else None,
        "points_earned": earned,
        "route_completed": route_completed,
        "total_points": user.points,
        "route": summary,
    }
