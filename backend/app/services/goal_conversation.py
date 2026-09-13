"""Small, explicit intake state machine. Unknown amounts stay absent until answered."""
import re
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_UP
from app.models.wealth_schemas import Goal


def normalize(text):
    return unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode().strip()


QUESTIONS = {
    "name": "O que você quer realizar? Dê um nome ao seu objetivo, por exemplo: entrada do apartamento.",
    "target": "Quanto você pretende juntar, em reais? Pode escrever 10000 ou 10 mil.",
    "years": "Daqui a quantos anos gostaria de realizar isso? Nesta primeira versão, use um número inteiro de 1 a 50.",
    "current": "Quanto já está guardado para esse objetivo, em reais? Se ainda não começou, informe zero.",
    "contribution": "Quanto consegue guardar por mês para esse objetivo? Se ainda não souber, escreva pular.",
}


def amount(text):
    value = normalize(text).replace("r$", "").strip()
    match = re.fullmatch(r"(\d+(?:[.,]\d+)*)(?:\s*(mil|milhao|milhoes))?", value)
    if not match:
        raise ValueError("Informe apenas um valor, por exemplo 1500,50 ou 10 mil.")
    number, suffix = match.groups()
    if "," in number:
        number = number.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", number):
        number = number.replace(".", "")
    try:
        result = Decimal(number) * {None: 1, "mil": 1000, "milhao": 1000000, "milhoes": 1000000}[suffix]
        if not result.is_finite() or result > Decimal("1e12") or result.as_tuple().exponent < -2:
            raise ValueError("Use um valor de até um trilhão, com no máximo dois centavos decimais.")
        return float(result)
    except InvalidOperation as exc:
        raise ValueError("Não consegui identificar o valor. Use, por exemplo, 1500,50.") from exc


def intake(text, history):
    previous = history[-1].get("intake") if history else None
    normalized = normalize(text)
    if normalized in ("cancelar", "sair", "cancelar objetivo"):
        return {"text": "Rascunho encerrado. Objetivos que você já confirmou permanecem salvos. O que gostaria de explorar?", "intake": None}
    if normalized in ("criar um objetivo", "criar objetivo", "novo objetivo", "quero planejar um objetivo"):
        return {"text": QUESTIONS["name"], "intake": {"version": 1, "field": "name", "answers": {}}}
    if not previous:
        return None
    if previous.get("field") == "review":
        return {"text": "A proposta está pronta. Use Confirmar objetivo para salvá-la, ou escreva novo objetivo para recomeçar. Para ajustar os valores, use Meu plano após confirmar.", "intake": previous}
    field = previous["field"]
    answers = dict(previous["answers"])
    if normalized == "pular":
        return {"text": "Sem problema. Seu rascunho continua aqui, sem preencher esse dado por você. Para calcular e salvar, ainda preciso desta informação. " + QUESTIONS[field], "intake": previous}
    try:
        if field == "name":
            if not text.strip() or len(text.strip()) > 120:
                raise ValueError("Use um nome entre 1 e 120 caracteres.")
            answers[field] = text.strip()
        elif field == "years":
            match = re.fullmatch(r"(\d+)\s*(?:anos?)?", normalized)
            if not match or not 1 <= int(match[1]) <= 50:
                raise ValueError(QUESTIONS[field])
            answers[field] = int(match[1])
        else:
            answers[field] = amount(text)
            if field == "target" and answers[field] <= 0:
                raise ValueError("O valor desejado precisa ser maior que zero.")
            if field == "contribution" and answers[field] > 1e9:
                raise ValueError("O valor mensal máximo nesta versão é um bilhão de reais.")
    except ValueError as exc:
        return {"text": str(exc), "intake": previous}
    keys = list(QUESTIONS)
    next_index = keys.index(field) + 1
    summary = ""
    if field == "years":
        summary = "Já temos um objetivo e um prazo. Agora vamos considerar o que você já guardou, sem presumir saldo zero. "
    if next_index < len(keys):
        next_field = keys[next_index]
        return {"text": summary + QUESTIONS[next_field], "intake": {"version": 1, "field": next_field, "answers": answers}}
    goal = Goal(**answers).model_dump()
    monthly = max(Decimal(0), Decimal(str(goal["target"])) - Decimal(str(goal["current"]))) / (goal["years"] * 12)
    monthly = monthly.quantize(Decimal("0.01"), rounding=ROUND_UP)
    return {"text": "Confira a proposta abaixo antes de salvar. Esta conta divide o valor que falta pelos meses disponíveis, sem rendimento nem inflação. Não é uma recomendação de investimento. Seu orçamento total ainda precisa ser verificado.",
            "intake": {"version": 1, "field": "review", "answers": answers},
            "proposal": goal, "monthly_reference": float(monthly)}
