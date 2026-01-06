from fastapi import FastAPI
from app.routes.recomendacao import router
from app.routes.recomendacao import router as recomendacao_router
from app.routes.simulacao import router as simulacao_router

app = FastAPI(
    title="Robo Advisor API",
    description="API de recomendação de investimentos personalizada",
    version="0.1"
)

app.include_router(router)

app.include_router(recomendacao_router)
app.include_router(simulacao_router)