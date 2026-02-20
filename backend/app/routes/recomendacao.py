from fastapi import APIRouter, Depends
from app.auth.models.user import User
from app.core.dependencies import get_current_user
from app.models.perfil import PerfilInvestidor
from app.services.suitability import classificar_perfil
from app.services.recomendador import gerar_carteira, explicar_recomendacao

router = APIRouter(tags=["Recomendação"])


@router.post("/recomendacao")
def recomendar(
    perfil: PerfilInvestidor,
    current_user: User = Depends(get_current_user),
):
    perfil_classificado = classificar_perfil(perfil)
    carteira = gerar_carteira(perfil_classificado)
    explicacao = explicar_recomendacao(perfil_classificado, perfil)

    return {
        "perfil_classificado": perfil_classificado,
        "carteira_recomendada": carteira,
        "explicacao": explicacao,
    }
