from pydantic import BaseModel, Field

class PerfilInvestidor(BaseModel):
    idade: int = Field(..., gt=17, lt=100)
    renda_mensal: float = Field(..., gt=0)
    patrimonio: float = Field(..., ge=0)
    horizonte_anos: int = Field(..., gt=0)
    tolerancia_risco: int = Field(..., ge=1, le=5)
    objetivo: str
