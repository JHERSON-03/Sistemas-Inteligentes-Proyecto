from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    dni: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    full_name: Mapped[str] = mapped_column(String(120))
    grade: Mapped[str] = mapped_column(String(20), default="5to Sec.")
    section: Mapped[str] = mapped_column(String(2), default="B")
    points: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_login: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LoginDay(Base):
    """Un registro por cada día que el alumno ingresó (racha y calendario)."""
    __tablename__ = "login_days"
    __table_args__ = (UniqueConstraint("user_id", "day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    day: Mapped[date] = mapped_column(Date)


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(60))
    color: Mapped[str] = mapped_column(String(7))
    icon: Mapped[str] = mapped_column(String(30))


class LearningRoute(Base):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    minutes: Mapped[int] = mapped_column(Integer, default=30)
    bonus_points: Mapped[int] = mapped_column(Integer, default=50)
    course: Mapped[Course] = relationship()
    activities: Mapped[list["Activity"]] = relationship(order_by="Activity.order", back_populates="route")


class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(120))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)
    answer: Mapped[int] = mapped_column(Integer)
    hint: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    route: Mapped[LearningRoute] = relationship(back_populates="activities")


class ActivityProgress(Base):
    __tablename__ = "activity_progress"
    __table_args__ = (UniqueConstraint("user_id", "activity_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_first_try: Mapped[bool] = mapped_column(Boolean, default=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    title: Mapped[str] = mapped_column(String(120))
    course: Mapped[Course] = relationship()
    questions: Mapped[list["AssessmentQuestion"]] = relationship(order_by="AssessmentQuestion.order")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"))
    order: Mapped[int] = mapped_column(Integer)
    situation: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)  # [{"text": "...", "reason": "..."}]
    answer: Mapped[int] = mapped_column(Integer)
    feedback_ok: Mapped[str] = mapped_column(Text)
    feedback_ko: Mapped[str] = mapped_column(Text)


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("assessment_questions.id"))
    selected: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[str] = mapped_column(String(20))
    correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)
    answer: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text)
    course: Mapped[Course] = relationship()


class ChallengeAnswer(Base):
    __tablename__ = "challenge_answers"
    __table_args__ = (UniqueConstraint("user_id", "day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    challenge_id: Mapped[int] = mapped_column(ForeignKey("daily_challenges.id"))
    day: Mapped[date] = mapped_column(Date)
    correct: Mapped[bool] = mapped_column(Boolean)


class TutorMessage(Base):
    __tablename__ = "tutor_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(40), index=True)
    course: Mapped[str] = mapped_column(String(30))
    role: Mapped[str] = mapped_column(String(10))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StudyLog(Base):
    """Minutos de estudio por tipo: rutas, tutor, autoevaluacion."""
    __tablename__ = "study_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    minutes: Mapped[float] = mapped_column(Float)
    day: Mapped[date] = mapped_column(Date, default=date.today)
