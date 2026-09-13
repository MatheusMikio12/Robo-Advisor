"""Regras auditáveis: nenhum resultado depende de texto produzido por LLM."""
from datetime import date, datetime, timezone
import math
import random
from app.models.wealth_schemas import Diagnosis, Simulation

VERSION = "prisma-policy-1.0"
CLASSES = {"liquidez": "Liquidez e reserva", "inflacao": "Proteção contra inflação",
           "brasil": "Ações brasileiras diversificadas", "global": "Ações globais diversificadas",
           "imobiliario": "Fundos imobiliários"}


def policy(p: Diagnosis) -> dict:
    months = {"estavel": 6, "variavel": 9, "incerta": 12}[p.stability]
    reserve_target = p.expenses * months
    gap = max(0, reserve_target - p.reserve)
    surplus = max(0, p.income - p.expenses)
    contribution = min(surplus, p.contribution)
    tolerance = {"nenhuma": 0, "baixa": 1, "media": 2, "alta": 3}[p.loss_tolerance]
    capacity = 3
    reasons = []
    if gap > 0:
        capacity = 0
        reasons.append("Complete a reserva de emergência antes de ampliar o risco.")
    if p.debt > 0 and p.debt_rate >= 12:
        capacity = 0
        reasons.append("Compare a quitação da dívida com investir: seu custo é elevado. O limite de 12% a.a. é uma regra inicial, não uma taxa de mercado.")
    if p.horizon <= 2 or p.liquidity_months <= 12 or p.goal == "reserva":
        capacity = 0
        reasons.append("Prazo curto ou necessidade de resgate pede preservação e liquidez.")
    elif p.horizon <= 5 or p.liquidity_months <= 36:
        capacity = min(capacity, 1)
        reasons.append("O prazo intermediário limita a exposição a oscilações.")
    if p.stability == "incerta":
        capacity = min(capacity, 1)
    knowledge = {"nenhuma": 0, "basica": 2, "avancada": 3}[p.experience]
    score = min(tolerance, capacity, knowledge)
    if knowledge < min(tolerance, capacity):
        reasons.append("O conhecimento declarado limita a complexidade e o risco da carteira inicial.")
    if p.contribution > surplus:
        reasons.append("O aporte foi limitado à sobra mensal informada.")
    weights = [
        {"liquidez": 100},
        {"liquidez": 60, "inflacao": 25, "global": 15},
        {"liquidez": 35, "inflacao": 30, "global": 25, "brasil": 10},
        {"liquidez": 20, "inflacao": 25, "global": 35, "brasil": 15, "imobiliario": 5},
    ][score].copy()
    removed = sum(weights.pop(c, 0) for c in p.excluded_classes)
    if removed and "liquidez" not in p.excluded_classes:
        weights["liquidez"] = weights.get("liquidez", 0) + removed
    else:
        weights = {} if removed else weights
    if not weights:
        reasons.append("As restrições impedem uma alocação compatível; revise-as antes de investir.")
    if p.currency != "BRL":
        reasons.append("O objetivo está em outra moeda. A carteira em reais não elimina risco cambial; seleção suspensa até incluir instrumentos compatíveis.")
    return {
        "version": VERSION, "profile": ["Conservador", "Conservador", "Moderado", "Arrojado"][score],
        "risk_score": score, "tolerance": tolerance, "capacity": capacity,
        "reserve_months": months, "reserve_target": round(reserve_target, 2), "reserve_gap": round(gap, 2),
        "monthly_surplus": round(p.income - p.expenses, 2), "contribution": round(contribution, 2),
        "investable": round(max(0, p.assets - max(reserve_target, p.reserve)), 2),
        "savings_rate": round((p.income - p.expenses) / p.income * 100, 2) if p.income else None,
        "max_issuer_pct": p.max_issuer_pct, "reasons": reasons,
        "allocation": [{"key": k, "name": CLASSES[k], "percent": v} for k, v in weights.items()],
        "selection_blocked": not weights or p.currency != "BRL" or (p.debt > 0 and p.debt_rate >= 12),
        "assumptions": ["Carteiras-modelo com limites determinísticos; não são otimização de retorno.",
                        "Reserva informada integra o patrimônio; não é somada novamente.",
                        "Liquidez e risco de mercado são critérios distintos."]}


def product_exclusions(product: dict, p: Diagnosis, pol: dict, today: date) -> list[str]:
    reasons = []
    try:
        observed = date.fromisoformat(product["as_of"][:10])
        if (today - observed).days > 7 or observed > today:
            reasons.append("Dados fora da janela de validade de 7 dias")
    except (KeyError, TypeError, ValueError):
        reasons.append("Sem data verificável")
    if not product.get("eligible", False):
        reasons.append("Cadastro incompleto ou oferta não verificada")
    if product.get("currency") != p.currency:
        reasons.append("Moeda incompatível")
    if product.get("risk", 99) > pol["risk_score"]:
        reasons.append("Risco acima do limite")
    if product.get("liquidity_days", 99999) > p.liquidity_months * 30:
        reasons.append("Liquidez incompatível")
    if product.get("asset_class") in p.excluded_classes:
        reasons.append("Classe excluída pelo cliente")
    if product.get("platform") != "Tesouro Direto" and product.get("platform") not in p.institutions:
        reasons.append("Disponibilidade na instituição não confirmada")
    if product.get("minimum", float("inf")) > max(pol["contribution"], pol["investable"]):
        reasons.append("Investimento mínimo acima do valor disponível")
    if product.get("asset_class") == "inflacao":
        try:
            years = (date.fromisoformat(product["maturity"]) - today).days / 365.25
            if years > p.horizon or years < max(1, p.horizon - 5):
                reasons.append("Vencimento desalinhado ao objetivo")
        except (KeyError, ValueError):
            reasons.append("Vencimento não informado")
    return reasons


def recommend(p: Diagnosis, products: list[dict], holdings: list[dict], today=None) -> dict:
    today = today or date.today()
    pol = policy(p)
    selected, excluded = [], []
    issuer_value = {}
    # Posições existentes reduzem o limite disponível por emissor na carteira consolidada.
    local_holdings = [h for h in holdings if h.get("currency") == "BRL"]
    held = sum(h["value"] for h in local_holdings)
    # O patrimônio declarado já contém as posições; não somá-las novamente.
    available_base = max(0, p.assets - p.reserve) if pol["reserve_gap"] else pol["investable"]
    uninvested = max(0, available_base - sum(h["value"] for h in local_holdings if h["asset_class"] != "liquidez"))
    purchase_budget = uninvested + pol["contribution"]
    total = max(p.assets, held) + pol["contribution"]
    for h in local_holdings:
        issuer_value[h["issuer"]] = issuer_value.get(h["issuer"], 0) + h["value"]
    for slot in pol["allocation"]:
        candidates = []
        for product in products:
            if product.get("asset_class") != slot["key"]:
                continue
            errors = product_exclusions(product, p, pol, today)
            if errors:
                excluded.append({"id": product["id"], "name": product["name"], "reasons": errors})
            else:
                # Compare apenas instrumentos da mesma classe. Evita ranking por rentabilidade passada.
                score = round(100 - product.get("fee_pct", 0) * 10 - product.get("liquidity_days", 0) * .1
                              - product.get("risk", 0) * 5, 2)
                candidates.append({**product, "score": score})
        candidates.sort(key=lambda x: (-x["score"], x["id"]))
        remaining = float(slot["percent"])
        choices = []
        if not pol["selection_blocked"]:
            for candidate in candidates:
                issuer = candidate["issuer"]
                limit = 100 if issuer == "Tesouro Nacional" else p.max_issuer_pct
                capacity_amount = max(0, total * limit / 100 - issuer_value.get(issuer, 0))
                weight = min(remaining, capacity_amount / purchase_budget * 100 if purchase_budget else 0)
                amount = purchase_budget * weight / 100
                if weight <= 0 or amount < candidate["minimum"]:
                    continue
                choices.append({"product": candidate, "percent": round(weight, 2), "amount": round(amount, 2),
                                "why": f"Cumpre a função de {slot['name'].lower()}, com prazo, risco e mínimo compatíveis.",
                                "alternatives": [{"id": c["id"], "name": c["name"], "score": c["score"]} for c in candidates if c["id"] != candidate["id"]][:3]})
                issuer_value[issuer] = issuer_value.get(issuer, 0) + amount
                remaining -= weight
                if remaining <= 0:
                    break
        selected.append({**slot, "products": choices, "unallocated_percent": round(remaining, 2),
                         "message": "Sem produto elegível confirmado para esta parcela." if remaining else ""})
    drift = []
    if held:
        for slot in pol["allocation"]:
            actual = sum(h["value"] for h in local_holdings if h["asset_class"] == slot["key"]) / held * 100
            delta = actual - slot["percent"]
            drift.append({"name": slot["name"], "actual": round(actual, 2), "target": slot["percent"],
                          "delta": round(delta, 2), "review": abs(delta) >= 5})
    return {"policy": pol, "allocation": selected, "excluded": excluded, "drift": drift, "purchase_budget": round(purchase_budget,2),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "method": "Elegibilidade antes do ranking; custos, liquidez e risco. Peso soberano pode chegar a 100%. Sem ordens automáticas."}


def simulate(s: Simulation) -> dict:
    rng = random.Random(s.seed)
    sigma = s.volatility / 100
    # annual_return é retorno aritmético esperado; GBM usa correção -sigma²/2.
    mu = math.log1p(s.annual_return / 100)
    fee = math.log1p(s.fees / 100) / 12
    years = [[] for _ in range(s.years)]
    contributions = []
    depletion = 0
    for _ in range(s.paths):
        balance, basis, deposited = s.initial, s.initial, s.initial
        ran_out = False
        for month in range(1, s.years * 12 + 1):
            balance *= math.exp((mu - sigma * sigma / 2) / 12 - fee + sigma / math.sqrt(12) * rng.gauss(0, 1))
            inflator = (1 + s.inflation / 100) ** (month / 12)
            paused = s.pause_start > 0 and s.pause_start <= month < s.pause_start + s.pause_months
            retired = s.withdrawal_start > 0 and month >= s.withdrawal_start
            contribution = 0 if paused or retired else s.contribution
            balance += contribution
            basis += contribution
            deposited += contribution
            withdrawal = (s.monthly_withdrawal * inflator if retired else 0) + (s.shock_amount * inflator if month == s.shock_month else 0)
            if withdrawal:
                gain_fraction = max(0, balance - basis) / balance if balance else 0
                gross = withdrawal / (1 - gain_fraction * s.tax / 100)
                if gross > balance:
                    ran_out = True
                sold = min(gross, balance)
                basis *= 1 - sold / balance if balance else 0
                balance -= sold
            if month % 12 == 0:
                net = balance - max(0, balance - basis) * s.tax / 100
                years[month // 12 - 1].append(net / inflator)
        contributions.append(deposited)
        depletion += ran_out
    series = []
    for year, values in enumerate(years, 1):
        values.sort()
        series.append({"year": year, "p10": round(values[int(.1 * (s.paths - 1))], 2),
                       "p50": round(values[int(.5 * (s.paths - 1))], 2), "p90": round(values[int(.9 * (s.paths - 1))], 2)})
    return {"series": series, "success_probability": round(sum(x >= s.target for x in years[-1]) / s.paths * 100, 1) if s.target else None,
            "depletion_probability": round(depletion / s.paths * 100, 1), "total_contributed_nominal": round(contributions[0], 2),
            "assumptions": s.model_dump(), "units": "Reais de hoje, líquidos de custos e imposto aproximado",
            "limitations": ["Cenários condicionais às premissas, não previsão nem garantia.",
                            "Retornos lognormais independentes; crises e correlações variáveis podem ser subestimadas.",
                            "Alíquota única sobre ganho positivo em resgates e saldo terminal; não substitui apuração tributária por produto.",
                            "Retiradas e imprevistos corrigidos pela inflação; aporte nominal constante."]}
