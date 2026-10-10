from datetime import date

from .. import models

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
          "noviembre", "diciembre"]


def status_label(avg: float) -> str:
    return "Vas muy bien" if avg >= 60 else ("Vas mejorando" if avg >= 30 else "¡Tú puedes!")


def time_out(minutes: dict) -> list[dict]:
    return [
        {"kind": "ruta", "label": "Rutas adaptativas", "hours": round(minutes["ruta"] / 60, 1), "color": "#284078"},
        {"kind": "tutor", "label": "Tutor IA", "hours": round(minutes["tutor"] / 60, 1), "color": "#A8A028"},
        {"kind": "autoevaluacion", "label": "Autoevaluación", "hours": round(minutes["autoevaluacion"] / 60, 1),
         "color": "#0F9F6E"},
    ]


def metrics_out(user: models.User, *, today: date, first: date, last_day: int, studied: list[date], courses: list,
                avg: float, minutes: dict, level: int, accuracy: float, comment: str) -> dict:
    return {
        "year": today.year,
        "status": status_label(avg),
        "courses": sorted(courses, key=lambda c: -c["percent"]),
        "time": time_out(minutes),
        "streak": user.streak,
        "best_streak": user.best_streak,
        "points": user.points,
        "autonomy": {"level": level, "max": 4},
        "accuracy": round(accuracy * 100),
        "ai_comment": comment,
        "calendar": {
            "month": MONTHS[today.month - 1],
            "first_weekday": first.weekday(),
            "days": last_day,
            "today": today.day,
            "studied": sorted(d.day for d in studied),
        },
    }
