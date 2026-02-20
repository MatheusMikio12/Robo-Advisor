import secrets

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações centralizadas da aplicação, lidas de variáveis de ambiente."""

    app_name: str = "Robo-Advisor"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ─── Segurança JWT ────────────────────────────────────────────────
    # DEVE ser definida no .env com uma string aleatória forte.
    # O default gera uma chave aleatória em runtime (seguro, mas tokens
    # são invalidados a cada restart — ideal para dev, NÃO para prod).
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Chave secreta para assinatura de tokens JWT",
    )
    access_token_expire_minutes: int = 30

    # ─── Banco de Dados ───────────────────────────────────────────────
    database_url: str = "sqlite:///./sql_app.db"

    # ─── CORS — origens permitidas ────────────────────────────────────
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância global reutilizada via import
settings = Settings()
