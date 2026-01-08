from pydantic import BaseModel

class PerfilInvestidor(BaseModel):
    idade: int
    renda: float
    patrimonio: float
    horizonte_anos: int
    objetivo: str
