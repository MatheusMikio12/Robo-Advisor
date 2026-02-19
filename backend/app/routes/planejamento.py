from fastapi import APIRouter
from app.models.perfil import PlanejamentoInput
from app.services.suitability import classificar_perfil
from app.services.recomendador import gerar_carteira
from app.services.simulador import simular_carteira

router = APIRouter(tags=["Planejamento"])


@router.post("/planejamento")
def gerar_planejamento(dados: PlanejamentoInput):
    """
    Gera um planejamento financeiro completo:
    1. Classifica o perfil de risco
    2. Recomenda carteira de investimentos
    3. Simula crescimento patrimonial
    """

    # 1️⃣ Converter input do frontend para modelo interno
    perfil_input = dados.to_perfil_investidor()

    # 2️⃣ Classificar perfil de risco
    perfil = classificar_perfil(perfil_input)

    # 3️⃣ Gerar carteira recomendada
    carteira = gerar_carteira(perfil)

    # 4️⃣ Simular crescimento da carteira
    simulacao = simular_carteira(
        aporte_inicial=dados.patrimonio_atual,
        aporte_mensal=dados.aporte_mensal,
        anos=dados.prazo_anos,
        carteira=carteira,
    )

    # 5️⃣ Retornar planejamento completo
    return {
        "perfil": perfil,
        "carteira": carteira,
        "resumo": {
            "valor_final": simulacao["valor_final"],
            "total_investido": simulacao["total_investido"],
            "retorno_absoluto": simulacao["retorno_absoluto"],
            "retorno_percentual": simulacao["retorno_percentual"],
            "cagr": simulacao["cagr"],
        },
        "evolucao": simulacao["evolucao"],
    }
