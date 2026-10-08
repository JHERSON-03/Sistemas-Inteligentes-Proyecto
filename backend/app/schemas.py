from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    identifier: str = Field(..., description="Usuario o DNI")
    password: str


class RegisterIn(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=120)
    dni: str = Field(..., pattern=r"^\d{8}$")
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.]+$")
    password: str = Field(..., min_length=6)
    section: str = Field("A", pattern=r"^[A-E]$")


class OptionIn(BaseModel):
    option: int = Field(..., ge=0)


class AssessmentAnswerIn(BaseModel):
    option: int = Field(..., ge=0)
    confidence: str = Field(..., pattern=r"^(nada|regular|muy)$")


class TutorMessageIn(BaseModel):
    course: str = Field(..., pattern=r"^(historia|ciencia|matematica|comunicacion)$")
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class TutorResetIn(BaseModel):
    course: str = Field(..., pattern=r"^(historia|ciencia|matematica|comunicacion)$")
