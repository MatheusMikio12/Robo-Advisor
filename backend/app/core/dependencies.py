"""
📌 Dependências globais reutilizáveis em qualquer rota.

Mover `get_current_user` para cá evita dependência circular:
rotas de negócio não precisam importar de rotas de auth.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.models.user import User
from app.auth.services import auth_service
from app.database import get_db
from app.services.account_security import version

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """Valida o token JWT e retorna o usuário autenticado."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth_service.decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user = auth_service.get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    if token_data.auth_version != version(db, user):
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )
    return user
