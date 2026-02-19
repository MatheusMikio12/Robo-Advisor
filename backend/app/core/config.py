from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações centralizadas da aplicação, lidas de variáveis de ambiente."""

    app_name: str = "Robo-Advisor"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS — origens permitidas (separar por vírgula na env var)
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
