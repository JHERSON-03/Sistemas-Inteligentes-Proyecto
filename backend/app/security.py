import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import models
from .config import SECRET_KEY, TOKEN_HOURS
from .database import get_db

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """bcrypt, compatible con crypt(clave, gen_salt('bf')) de pgcrypto en Supabase."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith("$2"):
        try:
            return bcrypt.checkpw(password.encode(), stored.encode())
        except ValueError:
            return False
    # Formato anterior (PBKDF2): salt$hash
    salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm="HS256")


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)
) -> models.User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inicia sesión para continuar")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tu sesión expiró, vuelve a ingresar")
    user = db.get(models.User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")
    return user
