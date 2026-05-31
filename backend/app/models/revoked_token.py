from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class RevokedToken(Base):
    """Blocklist de refresh tokens revogados (logout ou rotação).

    Armazena o `jti` (JWT ID) do refresh token. Um token cujo jti está aqui
    é recusado mesmo que a assinatura e a expiração ainda sejam válidas.
    O campo `expires_at` permite limpeza periódica de registros já expirados.
    """
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
