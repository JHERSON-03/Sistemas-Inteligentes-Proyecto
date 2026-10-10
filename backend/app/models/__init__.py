"""Capa de Modelo: entidades ORM mapeadas al esquema en español de la base de datos (Supabase/PostgreSQL).

Los atributos de Python se mantienen en inglés; el primer argumento de cada mapped_column
es el nombre real de la columna en la base de datos.
"""
from .assessment import Assessment, AssessmentAnswer, AssessmentQuestion
from .challenge import ChallengeAnswer, DailyChallenge
from .course import Course
from .route import Activity, ActivityProgress, LearningRoute
from .study import StudyLog
from .tutor import TutorMessage
from .user import LoginDay, User

__all__ = [
    "Activity", "ActivityProgress", "Assessment", "AssessmentAnswer", "AssessmentQuestion", "ChallengeAnswer",
    "Course", "DailyChallenge", "LearningRoute", "LoginDay", "StudyLog", "TutorMessage", "User",
]
