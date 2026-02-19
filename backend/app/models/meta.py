"""
📌 MODELO MetaFinanceira — Define a "forma" dos dados de entrada para metas financeiras.

CONCEITO (Pydantic BaseModel):
- Pydantic valida AUTOMATICAMENTE os dados antes de chegarem à lógica de negócio.
- Se o usuário mandar `valor_alvo: -1000`, o Pydantic retorna erro 422 sozinho.
- Field(...) = campo obrigatório. Field(None) = campo opcional.

POR QUE OPTIONAL?
- O usuário pode querer calcular: "quanto preciso aportar?" (aportes_mensal = None)
  OU "em quanto tempo chego lá?" (prazo_desejado = None).
- Pelo menos UM dos dois precisa ser preenchido — validamos isso no `model_validator`.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal


class MetaFinanceiraInput(BaseModel):
    """
    Modelo de entrada para o endpoint POST /meta.

    O usuário DEVE fornecer:
      - valor_alvo: quanto quer acumular (ex: 1_000_000)
      - patrimonio_atual: quanto já tem investido
      - objetivo: tipo de meta (afeta a rentabilidade esperada)

    E OPCIONALMENTE um dos dois (ou ambos):
      - prazo_desejado: em quantos anos quer atingir a meta
      - aporte_mensal: quanto pode investir por mês

    Se faltar o aporte_mensal → o sistema CALCULA o aporte necessário.
    Se faltar o prazo_desejado → o sistema CALCULA o prazo necessário.
    Se ambos forem fornecidos → o sistema verifica se a meta é viável.
    """

    valor_alvo: float = Field(
        ..., gt=0, description="Valor-alvo desejado em R$ (ex: 1000000)"
    )
    patrimonio_atual: float = Field(
        ..., ge=0, description="Patrimônio atual investido em R$"
    )
    aporte_mensal: Optional[float] = Field(
        None, ge=0, description="Aporte mensal em R$ (opcional — será calculado se não informado)"
    )
    prazo_desejado: Optional[int] = Field(
        None, gt=0, le=50, description="Prazo desejado em anos (opcional — será calculado se não informado)"
    )
    objetivo: Literal["aposentadoria", "imovel", "reserva", "crescimento"] = Field(
        ..., description="Objetivo financeiro — determina a rentabilidade esperada"
    )

    @model_validator(mode="after")
    def validar_pelo_menos_um_parametro(self):
        """
        📌 model_validator roda DEPOIS que todos os campos foram validados individualmente.
        Garante que o usuário forneceu pelo menos um dos parâmetros calculáveis.
        Sem isso, não temos informação suficiente para calcular nada.
        """
        if self.aporte_mensal is None and self.prazo_desejado is None:
            raise ValueError(
                "Informe pelo menos 'aporte_mensal' ou 'prazo_desejado'. "
                "O sistema calculará o que estiver faltando."
            )
        return self
