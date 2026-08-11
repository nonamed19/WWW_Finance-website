import base64
import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import ApiToken, User


def hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(12)
    iterations = 600000
    encoded = base64.b64encode(hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)).decode().strip()
    return f"pbkdf2_sha256${iterations}${salt}${encoded}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = base64.b64encode(hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))).decode().strip()
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError):
        return False


def create_token(db: Session, user: User) -> str:
    db.query(ApiToken).filter(ApiToken.user_id == user.id).delete()
    token = ApiToken(key=secrets.token_hex(32), user_id=user.id)
    db.add(token); db.commit()
    return token.key


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Token "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials were not provided.")
    token = db.get(ApiToken, header[6:])
    user = db.get(User, token.user_id) if token else None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    return user
