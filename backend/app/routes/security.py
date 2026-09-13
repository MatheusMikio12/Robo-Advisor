from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.auth.models.user import User, UserCreate
from app.auth.services import auth_service
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.database import get_db
from app.models.wealth import WealthRecord
from app.services.account_security import security_record, cipher

router = APIRouter(prefix="/auth", tags=["Segurança"])


class EmailInput(BaseModel):
    email: EmailStr


class ResetInput(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str


class VerifyInput(BaseModel):
    password: str = Field(max_length=72)
    code: str = Field(default="", max_length=8)


@router.get("/security")
def security_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = security_record(db, user)
    return {"mfa": record.data.get("mfa", False), "password_reset_available": bool(settings.smtp_host)}


@router.post("/password/forgot")
@limiter.limit("3/hour")
def forgot(request: Request, body: EmailInput, db: Session = Depends(get_db)):
    if not settings.smtp_host:
        raise HTTPException(503, "Recuperação por e-mail ainda não configurada neste ambiente.")
    user = auth_service.get_user(db, body.email)
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        record = WealthRecord(user_id=user.id, kind="reset", external_id=hashlib.sha256(token.encode()).hexdigest(),
                             data={"expires": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(), "used": False})
        db.add(record)
        message = EmailMessage()
        message["Subject"] = "Redefinir senha do Prisma"
        message["From"] = settings.smtp_sender
        message["To"] = user.email
        message.set_content(f"Abra {settings.frontend_url}/login?reset={token} para redefinir a senha. O link expira em 30 minutos.")
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.starttls()
                if settings.smtp_username:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
            db.commit()
        except Exception:
            db.rollback()
            # Resposta uniforme evita revelar a existência da conta.
    return {"detail": "Se a conta existir, você receberá um link de recuperação."}


@router.post("/password/reset")
@limiter.limit("5/minute")
def reset(request: Request, body: ResetInput, db: Session = Depends(get_db)):
    digest = hashlib.sha256(body.token.encode()).hexdigest()
    row = db.query(WealthRecord).filter_by(kind="reset", external_id=digest).with_for_update().first()
    if not row or row.data["used"] or datetime.fromisoformat(row.data["expires"]) <= datetime.now(timezone.utc):
        raise HTTPException(400, "Link inválido ou expirado.")
    user = db.get(User, row.user_id)
    try:
        validated = UserCreate(email=user.email, password=body.password)
    except ValueError:
        raise HTTPException(422, "Use de 8 a 72 caracteres, incluindo maiúscula e número.") from None
    consumed = db.query(WealthRecord).filter(WealthRecord.id == row.id, WealthRecord.data["used"].as_boolean() == False).update(  # noqa: E712
        {"data": {**row.data, "used": True}}, synchronize_session=False)
    if not consumed:
        raise HTTPException(400, "Link inválido ou expirado.")
    user.hashed_password = auth_service.get_password_hash(validated.password)
    sec = security_record(db, user)
    sec.data = {**sec.data, "version": sec.data.get("version", 0) + 1}
    db.commit()
    return {"detail": "Senha atualizada. Faça login novamente."}


@router.post("/mfa/setup")
@limiter.limit("5/minute")
def setup(request: Request, body: VerifyInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not auth_service.verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Senha incorreta.")
    sec = security_record(db, user)
    if sec.data.get("mfa"):
        raise HTTPException(409, "Autenticação em duas etapas já está ativa.")
    secret = pyotp.random_base32()
    sec.data = {**sec.data, "pending_secret": cipher().encrypt(secret.encode()).decode()}
    db.commit()
    return {"secret": secret, "uri": pyotp.TOTP(secret).provisioning_uri(user.email, issuer_name="Prisma")}


@router.post("/mfa/enable")
@limiter.limit("5/minute")
def enable(request: Request, body: VerifyInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sec = security_record(db, user)
    pending = sec.data.get("pending_secret")
    if not pending or not auth_service.verify_password(body.password, user.hashed_password) or not pyotp.TOTP(cipher().decrypt(pending.encode()).decode()).verify(body.code):
        raise HTTPException(400, "Senha ou código inválido.")
    sec.data = {"version": sec.data.get("version", 0) + 1, "mfa": True, "secret": pending}
    db.commit()
    return {"detail": "Autenticação em duas etapas ativada. Entre novamente."}


@router.post("/mfa/disable")
@limiter.limit("5/minute")
def disable(request: Request, body: VerifyInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sec = security_record(db, user)
    if not sec.data.get("mfa") or not auth_service.verify_password(body.password, user.hashed_password) or not pyotp.TOTP(cipher().decrypt(sec.data["secret"].encode()).decode()).verify(body.code):
        raise HTTPException(400, "Senha ou código inválido.")
    sec.data = {"version": sec.data.get("version", 0) + 1, "mfa": False}
    db.commit()
    return {"detail": "Autenticação em duas etapas desativada. Entre novamente."}
