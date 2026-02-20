from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base
from pydantic import BaseModel, EmailStr, Field


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
        description="Senha do usuário (8-72 caracteres)",
    )


class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
