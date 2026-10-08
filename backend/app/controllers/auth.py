from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import models
from ..config import GRADE
from ..database import get_db
from ..schemas import LoginIn, RegisterIn
from ..security import create_token, current_user, hash_password, verify_password
from ..services.gamification import register_login

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_out(user: models.User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "first_name": user.full_name.split()[0],
        "grade": user.grade,
        "section": user.section,
        "points": user.points,
        "streak": user.streak,
        "best_streak": user.best_streak,
    }


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    ident = data.identifier.strip()
    user = db.scalar(select(models.User).where(or_(models.User.username == ident.lower(), models.User.dni == ident)))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario/DNI o contraseña incorrectos")
    streak = register_login(db, user)
    return {"token": create_token(user.id), "user": user_out(user), "streak_message": streak["message"]}


@router.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    username = data.username.lower()
    taken = db.scalar(select(models.User).where(or_(models.User.username == username, models.User.dni == data.dni)))
    if taken:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese usuario o DNI ya está registrado")
    user = models.User(
        username=username, dni=data.dni, full_name=data.full_name.strip(),
        password_hash=hash_password(data.password), grade=GRADE, section=data.section,
    )
    db.add(user)
    db.commit()
    register_login(db, user)
    return {"token": create_token(user.id), "user": user_out(user), "streak_message": None}


@router.post("/forgot")
def forgot():
    return {"message": "Pide a tu tutor o docente que restablezca tu contraseña desde la secretaría del colegio."}


@router.get("/me")
def me(user: models.User = Depends(current_user)):
    return user_out(user)
