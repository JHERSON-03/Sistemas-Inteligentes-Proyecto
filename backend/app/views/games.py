from .. import models
from ..services.juego_atrapa import PARTIDAS_POR_DIA


def short_name(user: models.User) -> str:
    parts = user.full_name.split()
    return parts[0] + (" " + parts[-1][0] + "." if len(parts) > 1 else "")


def result_out(match: models.GameMatch, correct: list[int], earned: int, user: models.User,
               plays_left: int) -> dict:
    return {
        "score": match.score,
        "hits": match.hits,
        "misses": match.misses,
        "correct": correct,
        "points_earned": earned,
        "total_points": user.points,
        "plays_left": plays_left,
    }


def ranking_out(rows: list[tuple[models.User, int]], user: models.User, plays_left: int) -> dict:
    return {
        "top": [{"position": i + 1, "name": short_name(u), "score": best, "me": u.id == user.id}
                for i, (u, best) in enumerate(rows)],
        "plays_left": plays_left,
        "max_plays": PARTIDAS_POR_DIA,
    }
