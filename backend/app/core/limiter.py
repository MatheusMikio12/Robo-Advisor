"""Instância compartilhada do rate limiter (slowapi).

Mantida em módulo próprio para evitar import circular entre main.py e os routers
que precisam aplicar limites dedicados (ex: auth.py).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"], enabled=settings.rate_limit_enabled or not settings.debug)
