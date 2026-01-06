from fastapi import APIRouter
from app.models.simulacao import SimulacaoInput
from app.services.simulador import simular_carteira

router = APIRouter()

@router.post("/simulacao")
def simular(input: SimulacaoInput):
    resultado = simular_carteira(
        carteira=input.carteira,
        aporte_inicial=input.aporte_inicial,
        aporte_mensal=input.aporte_mensal,
        anos=input.anos
    )
    return resultado
