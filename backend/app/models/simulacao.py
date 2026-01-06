from pydantic import BaseModel, Field
from typing import Dict

class SimulacaoInput(BaseModel):
    carteira: Dict[str, float]
    aporte_inicial: float = Field(..., ge=0)
    aporte_mensal: float = Field(..., ge=0)
    anos: int = Field(..., gt=0)
