import logging
import time
import uuid
from sqlalchemy import text

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.routes import meta, planejamento, recomendacao, simulacao, suitability, wealth as wealth_routes
from app.auth.routes import auth
from app.routes import security
from app.database import engine, Base
# Garante que todos os models SQLAlchemy sejam registrados antes do create_all
from app.models import suitability_db  # noqa: F401
from app.models import revoked_token  # noqa: F401
from app.models import wealth  # noqa: F401

# Create tables (for development without alembic)
if settings.debug:
    Base.metadata.create_all(bind=engine)

# Seed do usuário administrador padrão (idempotente)
from app.auth.services import auth_service  # noqa: E402
from app.database import SessionLocal  # noqa: E402

_seed_db = SessionLocal()
try:
    if settings.debug:
        auth_service.seed_admin_user(_seed_db)
finally:
    _seed_db.close()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="API de planejamento financeiro inteligente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def request_trace(request: Request, call_next):
    started = time.perf_counter()
    trace_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = trace_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Não registrar corpo, querystring, tokens ou dados financeiros.
    logger.info("request_id=%s method=%s status=%s duration_ms=%.1f", trace_id, request.method, response.status_code, (time.perf_counter()-started)*1000)
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — origens lidas das configurações
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)

# Registrar TODOS os routers
app.include_router(auth.router)
app.include_router(meta.router)
app.include_router(planejamento.router)
app.include_router(recomendacao.router)
app.include_router(simulacao.router)
app.include_router(suitability.router)
app.include_router(wealth_routes.router)
app.include_router(security.router)


# ─── Handler global de exceções ─────────────────────────────────────────────
# Captura exceções não tratadas e retorna mensagem segura (sem stack trace)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Erro não tratado path=%s type=%s", request.url.path, type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente."},
    )


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de verificação de saúde da API."""
    return {"status": "ok", "app": settings.app_name}


@app.get("/health/ready", tags=["Health"])
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status":"unavailable"})
