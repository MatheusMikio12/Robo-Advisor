from pydantic import BaseModel, Field
from typing import Literal


class PerfilInvestidor(BaseModel):
    """Modelo interno para análise de suitability."""

    idade: int = Field(..., ge=18, le=100, description="Idade do investidor")
    renda: float = Field(..., gt=0, description="Renda mensal em R$")
    patrimonio: float = Field(..., ge=0, description="Patrimônio atual em R$")
    horizonte_anos: int = Field(..., gt=0, le=50, description="Horizonte de investimento em anos")
    objetivo: Literal["aposentadoria", "imovel", "reserva", "crescimento"] = Field(
        ..., description="Objetivo financeiro principal"
    )


class PlanejamentoInput(BaseModel):
    """Modelo de entrada do endpoint /planejamento — espelha exatamente o payload do frontend."""

    idade: int = Field(..., ge=18, le=100)
    renda_mensal: float = Field(..., gt=0)
    patrimonio_atual: float = Field(..., ge=0)
    aporte_mensal: float = Field(..., ge=0)
    prazo_anos: int = Field(..., gt=0, le=50)
    objetivo: Literal["aposentadoria", "imovel", "reserva", "crescimento"]

    def to_perfil_investidor(self) -> PerfilInvestidor:
        """Converte o input do frontend para o modelo interno de suitability."""
        return PerfilInvestidor(
            idade=self.idade,
            renda=self.renda_mensal,
            patrimonio=self.patrimonio_atual,
            horizonte_anos=self.prazo_anos,
            objetivo=self.objetivo,
        )
