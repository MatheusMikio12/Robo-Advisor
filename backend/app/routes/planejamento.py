from fastapi import APIRouter
from app.models.perfil import PerfilInvestidor
from app.services.suitability import classificar_perfil
from app.services.recomendador import gerar_carteira
from app.services.simulador import simular_carteira

router = APIRouter(prefix="/planejamento", tags=["Planejamento"], redirect_slashes=False)


@router.post("/")
def gerar_planejamento(dados: dict):

    # 1️⃣ Adaptar o JSON externo para o modelo interno
    perfil_input = PerfilInvestidor(
        idade=dados["idade"],
        renda=dados["renda_mensal"],
        patrimonio=dados["patrimonio_atual"],
        horizonte_anos=dados["prazo_anos"],
        objetivo=dados["objetivo"]
    )

    # 2️⃣ Classificar perfil de risco
    perfil = classificar_perfil(perfil_input)

    # 3️⃣ Gerar carteira recomendada
    carteira = gerar_carteira(perfil)

    # 4️⃣ Simular crescimento da carteira
    simulacao = simular_carteira(
        aporte_inicial=dados["patrimonio_atual"],
        aporte_mensal=dados["aporte_mensal"],
        anos=dados["prazo_anos"],
        carteira=carteira
    )

    # 5️⃣ Retornar planejamento completo (estrutura esperada pelo frontend)
    return {
        "perfil": perfil,
        "carteira": carteira,
        "resumo": {
            "valor_final": simulacao.get("valor_final", 0),
            "total_investido": simulacao.get("total_investido", 0),
            "retorno_absoluto": simulacao.get("retorno_absoluto", 0),
            "retorno_percentual": simulacao.get("retorno_percentual", 0),
            "cagr": simulacao.get("cagr", 0)
        },
        "evolucao": simulacao.get("evolucao", [])
    }
