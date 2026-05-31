import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.auth.models.user import User, UserCreate, TokenData
from app.core.config import settings
from app.models.revoked_token import RevokedToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def seed_admin_user(db: Session) -> None:
    """Cria o usuário administrador padrão se ainda não existir (idempotente).

    Credenciais vêm de settings.admin_email / settings.admin_password (.env).
    Padrão de dev: admin@admin.com / Admin@123.
    """
    if get_user(db, email=settings.admin_email):
        return
    create_user(
        db,
        UserCreate(email=settings.admin_email, password=settings.admin_password),
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") == "refresh":
            return None  # recusa usar refresh token como access token
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except jwt.PyJWTError:
        return None


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    # jti (JWT ID) único permite revogação individual do token (logout / rotação)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_refresh_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None  # recusa usar access token como refresh token
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email, jti=payload.get("jti"), exp=payload.get("exp"))
    except jwt.PyJWTError:
        return None


# ─── Revogação de refresh tokens (blocklist) ──────────────────────────

def is_token_revoked(db: Session, jti: str | None) -> bool:
    """True se o jti consta na blocklist (token invalidado)."""
    if not jti:
        return False
    return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None


def revoke_token(db: Session, jti: str | None, exp: int | None) -> None:
    """Adiciona o jti à blocklist. Idempotente — ignora se já revogado."""
    if not jti or is_token_revoked(db, jti):
        return
    expires_at = (
        datetime.fromtimestamp(exp, tz=timezone.utc)
        if exp
        else datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(RevokedToken(jti=jti, expires_at=expires_at))
    db.commit()
