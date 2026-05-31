from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.models.user import UserCreate, UserResponse, User, TokenPair, RefreshRequest
from app.auth.services import auth_service
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")  # previne criação massiva de contas
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth_service.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já registrado.")
    return auth_service.create_user(db=db, user=user)


@router.post("/login", response_model=TokenPair)
@limiter.limit("5/minute")  # mitiga brute-force de senha por IP
def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = auth_service.get_user(db, email=form_data.username)
    if not user or not auth_service.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenPair)
def refresh_access_token(body: RefreshRequest, db: Session = Depends(get_db)):
    """Renova o access token usando um refresh token válido.

    Aplica rotação: o refresh token usado é revogado e um novo é emitido,
    impedindo replay de um token já consumido.
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth_service.decode_refresh_token(body.refresh_token)
    if token_data is None:
        raise invalid
    if auth_service.is_token_revoked(db, token_data.jti):
        raise invalid
    user = auth_service.get_user(db, email=token_data.email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    # Rotação: revoga o token usado antes de emitir o novo par
    auth_service.revoke_token(db, token_data.jti, token_data.exp)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(body: RefreshRequest, db: Session = Depends(get_db)):
    """Revoga o refresh token informado (blocklist). Idempotente.

    Após o logout o refresh token não pode mais renovar a sessão, mesmo
    que sua assinatura e expiração ainda sejam válidas.
    """
    token_data = auth_service.decode_refresh_token(body.refresh_token)
    if token_data is not None:
        auth_service.revoke_token(db, token_data.jti, token_data.exp)
    # Resposta uniforme: não revela se o token era válido
    return {"detail": "Logout efetuado."}


@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
