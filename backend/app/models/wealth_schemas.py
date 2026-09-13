from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


Money = float


class Diagnosis(StrictModel):
    age: int = Field(ge=18, le=100)
    income: Money = Field(ge=0, le=1e9)
    expenses: Money = Field(ge=0, le=1e9)
    assets: Money = Field(ge=0, le=1e12)
    reserve: Money = Field(ge=0, le=1e12)
    debt: Money = Field(ge=0, le=1e12)
    debt_rate: float = Field(ge=0, le=1000, description="Custo efetivo anual em %")
    contribution: Money = Field(ge=0, le=1e9)
    horizon: int = Field(ge=1, le=50)
    goal: Literal["reserva", "imovel", "aposentadoria", "crescimento", "educacao", "viagem"]
    stability: Literal["estavel", "variavel", "incerta"]
    experience: Literal["nenhuma", "basica", "avancada"]
    loss_tolerance: Literal["nenhuma", "baixa", "media", "alta"]
    liquidity_months: int = Field(ge=0, le=600)
    currency: Literal["BRL", "USD", "EUR"] = "BRL"
    institutions: list[str] = Field(default_factory=list, max_length=20)
    excluded_classes: list[Literal["liquidez", "inflacao", "brasil", "global", "imobiliario"]] = Field(default_factory=list)
    max_issuer_pct: float = Field(default=25, ge=5, le=100)

    @model_validator(mode="after")
    def validate_reserve(self):
        if self.reserve > self.assets:
            raise ValueError("A reserva faz parte do patrimônio e não pode ultrapassá-lo.")
        return self


class Goal(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    target: Money = Field(gt=0, le=1e12)
    current: Money = Field(ge=0, le=1e12)
    contribution: Money = Field(ge=0, le=1e9)
    years: int = Field(ge=1, le=50)
    priority: Literal["alta", "media", "baixa"] = "media"
    currency: Literal["BRL", "USD", "EUR"] = "BRL"


class Simulation(StrictModel):
    initial: Money = Field(ge=0, le=1e12)
    contribution: Money = Field(ge=0, le=1e9)
    years: int = Field(ge=1, le=50)
    target: Money = Field(default=0, ge=0, le=1e12)
    annual_return: float = Field(default=6, ge=-50, le=40)
    volatility: float = Field(default=10, ge=0, le=60)
    inflation: float = Field(default=4, ge=0, le=30)
    fees: float = Field(default=0.5, ge=0, le=10)
    tax: float = Field(default=15, ge=0, le=40)
    pause_start: int = Field(default=0, ge=0, le=600)
    pause_months: int = Field(default=0, ge=0, le=600)
    withdrawal_start: int = Field(default=0, ge=0, le=600)
    monthly_withdrawal: Money = Field(default=0, ge=0, le=1e9)
    shock_month: int = Field(default=0, ge=0, le=600)
    shock_amount: Money = Field(default=0, ge=0, le=1e12)
    paths: int = Field(default=400, ge=100, le=1000)
    seed: int = Field(default=42, ge=0, le=2**32-1)


class Holding(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    institution: str = Field(min_length=1, max_length=120)
    issuer: str = Field(min_length=1, max_length=120)
    asset_class: Literal["liquidez", "inflacao", "brasil", "global", "imobiliario", "outros"]
    value: Money = Field(ge=0, le=1e12)
    currency: Literal["BRL", "USD", "EUR"] = "BRL"


class ImportRequest(StrictModel):
    format: Literal["csv", "ofx"]
    content: str = Field(min_length=1, max_length=1_000_000)
    account: str = Field(min_length=1, max_length=120)
    confirm: bool = False


class Message(StrictModel):
    text: str = Field(min_length=1, max_length=3000)
    request_id: str = Field(min_length=1, max_length=80)


class Contribution(StrictModel):
    amount: Money = Field(gt=0, le=1e9)
    date: date
    request_id: str = Field(min_length=1, max_length=80)


class DraftDiagnosis(Diagnosis):
    @model_validator(mode="after")
    def validate_reserve(self):
        # Permite revisar patrimônio e reserva em passos diferentes.
        return self


class Draft(StrictModel):
    # Rascunho completo, ainda não confirmado como diagnóstico vigente.
    answers: DraftDiagnosis
    step: int = Field(ge=0, le=15)
