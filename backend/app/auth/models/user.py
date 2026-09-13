from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# ─── SQLAlchemy Model (camada de dados) ──────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


# ─── Pydantic Schemas (camada de contrato/validação) ─────────────────
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,  # bcrypt trunca após 72 bytes
        description="Senha do usuário (8-72 caracteres, com maiúscula e número)",
    )

    @field_validator("password")
    @classmethod
    def validar_forca_senha(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("A senha deve ocupar até 72 bytes em UTF-8.")
        if not any(c.isupper() for c in v):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula.")
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter ao menos um número.")
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPair(BaseModel):
    """Retornado no login — inclui access e refresh token."""
    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    auth_version: int = 0
    email: str | None = None
    jti: str | None = None  # JWT ID — usado para revogação de refresh tokens
    exp: int | None = None  # timestamp de expiração (unix)
