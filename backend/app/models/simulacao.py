from pydantic import BaseModel, Field, model_validator
from typing import List


class CarteiraItem(BaseModel):
    """Um item da carteira de investimentos."""
    ativo: str
    percentual: float = Field(..., ge=0, le=100)


class SimulacaoInput(BaseModel):
    """Modelo de entrada para simulação de carteira."""
    carteira: List[CarteiraItem]
    aporte_inicial: float = Field(..., ge=0)
    aporte_mensal: float = Field(..., ge=0)
    anos: int = Field(..., gt=0)

    @model_validator(mode="after")
    def validar_percentuais(self):
        """Garante que os percentuais da carteira somam 100%."""
        if not self.carteira:
            raise ValueError("A carteira não pode estar vazia.")
        total = sum(item.percentual for item in self.carteira)
        if abs(total - 100) > 0.01:
            raise ValueError(
                f"Os percentuais da carteira devem somar 100%. Soma atual: {total}%"
            )
        return self
