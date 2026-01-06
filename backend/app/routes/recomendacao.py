from fastapi import APIRouter
from app.models.perfil import PerfilInvestidor
from app.services.suitability import classificar_perfil
from app.services.recomendador import gerar_carteira, explicar_recomendacao

router = APIRouter()

@router.post("/recomendacao")
def recomendar(perfil: PerfilInvestidor):
    perfil_classificado = classificar_perfil(perfil)
    carteira = gerar_carteira(perfil_classificado)
    explicacao = explicar_recomendacao(perfil_classificado, perfil)

    return {
        "perfil_classificado": perfil_classificado,
        "carteira_recomendada": carteira,
        "explicacao": explicacao
    }
