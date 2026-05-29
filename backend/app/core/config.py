import logging
import secrets

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from typing import List

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configurações centralizadas da aplicação, lidas de variáveis de ambiente."""

    app_name: str = "Robo-Advisor"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ─── Segurança JWT ────────────────────────────────────────────────
    # Em produção (DEBUG=False), SECRET_KEY DEVE ser definida no .env.
    # Sem ela, a aplicação recusa inicializar para proteger tokens JWT.
    # Gere uma chave com: python -c "import secrets; print(secrets.token_urlsafe(32))"
    secret_key: str = Field(
        default="",
        description="Chave secreta para assinatura de tokens JWT. Obrigatória em produção.",
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

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        if not self.secret_key:
            if not self.debug:
                raise ValueError(
                    "SECRET_KEY deve ser definida no .env quando DEBUG=False (produção). "
                    'Gere com: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )
            # Modo desenvolvimento: gera automaticamente com aviso
            object.__setattr__(self, "secret_key", secrets.token_urlsafe(32))
            logger.warning(
                "SECRET_KEY não configurada — chave gerada automaticamente. "
                "Tokens JWT serão invalidados a cada restart. "
                "Defina SECRET_KEY no .env para evitar isso."
            )
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância global reutilizada via import
settings = Settings()
