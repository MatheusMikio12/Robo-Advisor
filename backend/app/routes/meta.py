"""
📌 ROTA /meta — Endpoint REST para o Sistema de Metas Financeiras.

CONCEITO (APIRouter):
- APIRouter é como um "sub-app" do FastAPI. Cada arquivo de rota define um grupo
  de endpoints relacionados, e depois registramos no main.py com app.include_router().
- Isso mantém o código organizado — cada domínio em seu próprio arquivo.

FLUXO DA REQUISIÇÃO:
  Frontend (fetch POST /meta) → FastAPI recebe
  → Pydantic valida (MetaFinanceiraInput) → se inválido, retorna 422
  → Se válido, chama calcular_meta() (service)
  → Retorna resultado como JSON
"""

from fastapi import APIRouter, Depends
from app.auth.models.user import User
from app.core.dependencies import get_current_user
from app.models.meta import MetaFinanceiraInput
from app.services.planejador import calcular_meta

# tags=["Metas"] agrupa os endpoints no Swagger UI (docs_url="/docs")
router = APIRouter(tags=["Metas Financeiras"])


@router.post("/meta")
def definir_meta(
    dados: MetaFinanceiraInput,
    current_user: User = Depends(get_current_user),
):
    """
    Calcula o plano para atingir uma meta financeira.

    Três modos de operação:
    - Sem `aporte_mensal`: calcula o aporte necessário
    - Sem `prazo_desejado`: calcula o prazo necessário
    - Com ambos: verifica a viabilidade da meta
    """
    resultado = calcular_meta(
        valor_alvo=dados.valor_alvo,
        patrimonio_atual=dados.patrimonio_atual,
        objetivo=dados.objetivo,
        aporte_mensal=dados.aporte_mensal,
        prazo_desejado=dados.prazo_desejado,
    )
    return resultado
