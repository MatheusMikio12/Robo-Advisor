import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routes import meta, planejamento, recomendacao, simulacao
from app.auth.routes import auth
from app.database import engine, Base

# Create tables (for development without alembic)
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="API de planejamento financeiro inteligente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — origens lidas das configurações
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)

# Registrar TODOS os routers
app.include_router(auth.router)
app.include_router(meta.router)
app.include_router(planejamento.router)
app.include_router(recomendacao.router)
app.include_router(simulacao.router)


# ─── Handler global de exceções ─────────────────────────────────────
# Captura exceções não tratadas e retorna mensagem segura (sem stack trace)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado em {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente."},
    )


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de verificação de saúde da API."""
    return {"status": "ok", "app": settings.app_name}
