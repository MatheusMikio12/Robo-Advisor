from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class PerfilSalvo(Base):
    """Perfil de suitability persistido por usuário — upsert, sempre um registro por user."""
    __tablename__ = "perfis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    perfil_classificado = Column(String, nullable=False)
    idade = Column(Integer, nullable=False)
    renda = Column(Float, nullable=False)
    patrimonio = Column(Float, nullable=False)
    horizonte_anos = Column(Integer, nullable=False)
    objetivo = Column(String, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
