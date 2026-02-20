from fastapi import APIRouter, Depends
from app.auth.models.user import User
from app.core.dependencies import get_current_user
from app.models.simulacao import SimulacaoInput
from app.services.simulador import simular_carteira

router = APIRouter(tags=["Simulação"])


@router.post("/simulacao")
def simular(
    dados: SimulacaoInput,
    current_user: User = Depends(get_current_user),
):
    """Simula a evolução de uma carteira de investimentos."""
    # Converte CarteiraItem (Pydantic) → list[dict] esperado pelo simulador
    carteira_list = [
        {"ativo": item.ativo, "percentual": item.percentual}
        for item in dados.carteira
    ]
    resultado = simular_carteira(
        carteira=carteira_list,
        aporte_inicial=dados.aporte_inicial,
        aporte_mensal=dados.aporte_mensal,
        anos=dados.anos,
    )
    return resultado
