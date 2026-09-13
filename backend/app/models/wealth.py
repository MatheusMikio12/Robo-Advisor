"""Memória financeira versionada; tabelas adicionais preservam o banco existente."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from app.database import Base


def now():
    return datetime.now(timezone.utc)


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    data = Column(JSON, nullable=False, default=dict)
    revision = Column(Integer, nullable=False, default=1)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)


class WealthRecord(Base):
    __tablename__ = "wealth_records"
    __table_args__ = (UniqueConstraint("user_id", "kind", "external_id"),)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String(30), nullable=False, index=True)
    external_id = Column(String(100), nullable=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)


class Product(Base):
    __tablename__ = "products"
    id = Column(String(120), primary_key=True)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(80), nullable=False)
    data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=now)
