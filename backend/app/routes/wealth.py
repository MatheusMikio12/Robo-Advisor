from datetime import datetime, timezone, date
from typing import Literal
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.auth.models.user import User
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.database import get_db
from app.models.wealth import FinancialProfile, WealthRecord, Product, AuditEvent
from app.models.wealth_schemas import Diagnosis, Goal, Simulation, Holding, ImportRequest, Message, Contribution, Draft
from app.services.wealth_engine import policy, recommend, simulate
from app.services.statement_import import parse_statement
from app.services.catalog import fetch_products
from app.services.concierge import respond

router = APIRouter(prefix="/wealth", tags=["Prisma"])


def records(db, user, kind):
    return db.query(WealthRecord).filter_by(user_id=user.id, kind=kind).order_by(WealthRecord.created_at).all()


def owned(db, user, record_id, kind):
    record = db.query(WealthRecord).filter_by(id=record_id, user_id=user.id, kind=kind).first()
    if not record:
        raise HTTPException(404, "Registro não encontrado.")
    return record


def pack(record):
    return {"id": record.id, **record.data, "updated_at": record.updated_at.isoformat()}


def audit(db, user, action, data=None):
    db.add(AuditEvent(user_id=user.id, action=action, data=data or {}))


def planning_snapshot(db, user):
    profile = db.get(FinancialProfile, user.id)
    data = {"revision": profile.revision if profile else 0,
            "goals": sorted([pack(x) for x in records(db, user, "goal")], key=lambda x: x["id"])}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def validate_goal_budget(db, user, goal, exclude_id=None):
    profile = db.get(FinancialProfile, user.id)
    if not profile or goal.currency != "BRL":
        return
    others = [x.data for x in records(db, user, "goal") if x.id != exclude_id and x.data.get("currency", "BRL") == "BRL"]
    pol = policy(Diagnosis.model_validate(profile.data))
    if round(sum(x["contribution"] for x in others) + goal.contribution, 2) > pol["contribution"]:
        raise HTTPException(409, "Os objetivos ultrapassam o aporte sustentável. Reduza o valor mensal ou revise seu contexto antes de confirmar.")
    if round(sum(x["current"] for x in others) + goal.current, 2) > profile.data["assets"]:
        raise HTTPException(409, "Os valores guardados nos objetivos ultrapassam seu patrimônio. Confira se o mesmo dinheiro foi usado duas vezes.")


def plan_current(plan, profile, holdings):
    if not profile or plan.get("profile_revision") != profile.revision or plan.get("holdings_snapshot", []) != holdings:
        return False
    for slot in plan.get("allocation", []):
        for item in slot.get("products", []):
            try:
                age = (date.today() - date.fromisoformat(item["product"]["as_of"][:10])).days
                if age < 0 or age > 7:
                    return False
            except (ValueError, KeyError):
                return False
    return True


@router.get("/draft")
def draft(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = records(db, user, "draft")
    return rows[0].data if rows else None


@router.put("/draft")
def save_draft(body: Draft, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = records(db, user, "draft")
    if rows:
        rows[0].data = body.model_dump()
    else:
        db.add(WealthRecord(user_id=user.id, kind="draft", external_id="onboarding", data=body.model_dump()))
    db.commit()
    return body


@router.get("/state")
def state(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.get(FinancialProfile, user.id)
    plans = records(db, user, "recommendation")
    transactions = records(db, user, "transaction")
    goals = records(db, user, "goal")
    holdings = records(db, user, "holding")
    warnings = []
    if profile:
        brl_goals = [row.data for row in goals if row.data.get("currency", "BRL") == "BRL"]
        pol = policy(Diagnosis.model_validate(profile.data))
        if sum(g["contribution"] for g in brl_goals) > pol["contribution"]:
            warnings.append("Os aportes das metas em reais ultrapassam seu aporte sustentável. Priorize ou ajuste as metas.")
        if sum(g["current"] for g in brl_goals) > profile.data["assets"]:
            warnings.append("Os saldos reservados nas metas ultrapassam o patrimônio informado. Confira se o mesmo dinheiro foi contado mais de uma vez.")
    cashflow = {}
    for row in transactions:
        month = row.data["date"][:7]
        cashflow[month] = round(cashflow.get(month, 0) + row.data["amount"], 2)
    return {"profile": profile.data if profile else None, "revision": profile.revision if profile else 0,
            "goals": [pack(x) for x in goals], "planning_warnings": warnings,
            "holdings": [pack(x) for x in holdings],
            "conversations": [pack(x) for x in records(db, user, "conversation")],
            "recommendation": pack(plans[-1]) if plans else None,
            "recommendation_stale": bool(plans and not plan_current(plans[-1].data, profile, [x.data for x in holdings])),
            "transactions": [pack(x) for x in transactions[-100:]], "cashflow": cashflow,
            "policy": policy(Diagnosis.model_validate(profile.data)) if profile else None}


@router.put("/profile")
def save_profile(body: Diagnosis, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.get(FinancialProfile, user.id)
    if record:
        record.data = body.model_dump()
        record.revision += 1
    else:
        record = FinancialProfile(user_id=user.id, data=body.model_dump(), revision=1)
        db.add(record)
    audit(db, user, "profile.updated", {"revision": record.revision})
    for draft in records(db, user, "draft"):
        db.delete(draft)
    db.commit()
    return {"profile": record.data, "revision": record.revision, "policy": policy(body)}


@router.post("/recommendations")
def make_recommendation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.get(FinancialProfile, user.id)
    if not profile:
        raise HTTPException(409, "Complete o diagnóstico antes de gerar a carteira.")
    investment_classes = ["liquidez", "inflacao", "brasil", "global", "imobiliario"]
    catalog = db.query(Product).filter(Product.data["asset_class"].as_string().in_(investment_classes)).all()
    result = recommend(Diagnosis.model_validate(profile.data), [x.data for x in catalog],
                       [x.data for x in records(db, user, "holding")])
    result["profile_revision"] = profile.revision
    result["profile_snapshot"] = profile.data
    result["holdings_snapshot"] = [x.data for x in records(db, user, "holding")]
    record = WealthRecord(user_id=user.id, kind="recommendation", data=result)
    db.add(record)
    audit(db, user, "recommendation.created", {"version": result["policy"]["version"], "revision": profile.revision})
    db.commit()
    return pack(record)


@router.get("/recommendations")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [pack(x) for x in records(db, user, "recommendation")]


@router.post("/simulate")
@limiter.limit("15/minute")
def scenario(request: Request, body: Simulation, user: User = Depends(get_current_user)):
    return simulate(body)


@router.post("/goals")
def create_goal(body: Goal, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    validate_goal_budget(db, user, body)
    record = WealthRecord(user_id=user.id, kind="goal", data=body.model_dump())
    db.add(record)
    audit(db, user, "goal.created")
    db.commit()
    return pack(record)


@router.put("/goals/{record_id}")
def edit_goal(record_id: str, body: Goal, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = owned(db, user, record_id, "goal")
    validate_goal_budget(db, user, body, record_id)
    record.data = body.model_dump()
    audit(db, user, "goal.updated", {"id": record_id})
    db.commit()
    return pack(record)


@router.post("/goals/{record_id}/contributions")
def add_contribution(record_id: str, body: Contribution, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = owned(db, user, record_id, "goal")
    key = f"{record_id}:{body.request_id}"[:100]
    old = db.query(WealthRecord).filter_by(user_id=user.id, kind="contribution", external_id=key).first()
    if old:
        return pack(record)
    db.add(WealthRecord(user_id=user.id, kind="contribution", external_id=key,
                       data={**body.model_dump(mode="json"), "goal_id": record_id}))
    record.data = {**record.data, "current": round(record.data["current"] + body.amount, 2)}
    audit(db, user, "goal.contribution", {"goal_id": record_id})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.refresh(record)
    return pack(record)


@router.get("/goals/{record_id}/history")
def goal_history(record_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned(db, user, record_id, "goal")
    return [pack(x) for x in records(db, user, "contribution") if x.data["goal_id"] == record_id]


@router.post("/holdings")
def holding(body: Holding, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = WealthRecord(user_id=user.id, kind="holding", data=body.model_dump())
    db.add(record)
    db.commit()
    return pack(record)


@router.put("/holdings/{record_id}")
def edit_holding(record_id: str, body: Holding, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = owned(db, user, record_id, "holding")
    record.data = body.model_dump()
    db.commit()
    return pack(record)


@router.post("/imports")
def import_statement(body: ImportRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        parsed = parse_statement(body.content, body.format, body.account)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    existing = {x.external_id for x in records(db, user, "transaction")}
    fresh = []
    for row in parsed:
        if row["external_id"] not in existing:
            fresh.append(row)
            existing.add(row["external_id"])
    if body.confirm:
        for row in fresh:
            db.add(WealthRecord(user_id=user.id, kind="transaction", external_id=row["external_id"], data=row))
        audit(db, user, "statement.imported", {"count": len(fresh)})
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "O extrato já foi importado em outra solicitação. Atualize a prévia.")
    return {"rows": fresh[:100], "new_count": len(fresh), "duplicates": len(parsed) - len(fresh), "confirmed": body.confirm}


@router.post("/conversations")
def conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = WealthRecord(user_id=user.id, kind="conversation", data={"title": "Conversa com o Prisma"})
    db.add(record)
    db.commit()
    return pack(record)


@router.get("/conversations/{record_id}/messages")
def messages(record_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned(db, user, record_id, "conversation")
    return [pack(x) for x in records(db, user, "message") if x.data["conversation_id"] == record_id]


@router.post("/conversations/{record_id}/messages")
def message(record_id: str, body: Message, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned(db, user, record_id, "conversation")
    old = db.query(WealthRecord).filter_by(user_id=user.id, kind="message", external_id=body.request_id).first()
    if old:
        if old.data["conversation_id"] != record_id:
            raise HTTPException(409, "Identificador de mensagem já utilizado.")
        return pack(old)
    profile = db.get(FinancialProfile, user.id)
    plans = records(db, user, "recommendation")
    latest = plans[-1].data if plans and plan_current(plans[-1].data, profile, [x.data for x in records(db, user, "holding")]) else None
    history = [x.data for x in records(db, user, "message") if x.data["conversation_id"] == record_id]
    answer = respond(body.text, profile.data if profile else None,
                     [x.data for x in records(db, user, "goal")], latest, history)
    if answer.get("proposal"):
        answer["planning_snapshot"] = planning_snapshot(db, user)
    record = WealthRecord(user_id=user.id, kind="message", external_id=body.request_id,
                         data={"conversation_id": record_id, "user_text": body.text, **answer})
    db.add(record)
    audit(db, user, "conversation.message", {"agent": answer["agent"], "tools": answer["tools"]})
    db.commit()
    return pack(record)


@router.post("/messages/{record_id}/confirm-goal")
def confirm_goal(record_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    message = owned(db, user, record_id, "message")
    key = f"proposal:{record_id}"
    existing = db.query(WealthRecord).filter_by(user_id=user.id, kind="goal", external_id=key).first()
    if existing:
        return pack(existing)
    if not message.data.get("proposal"):
        raise HTTPException(409, "Esta mensagem não contém uma proposta.")
    if message.data.get("planning_snapshot") != planning_snapshot(db, user):
        raise HTTPException(409, "Seu plano mudou desde esta proposta. Inicie um novo objetivo para revisar os valores antes de confirmar.")
    later = [x for x in records(db, user, "message") if x.data["conversation_id"] == message.data["conversation_id"] and x.created_at > message.created_at]
    if any(x.data.get("proposal") or x.data.get("intake") is None or x.data.get("intake", {}).get("field") == "name" for x in later):
        raise HTTPException(409, "Esta proposta foi substituída ou cancelada. Inicie um novo objetivo.")
    body = Goal.model_validate(message.data["proposal"])
    validate_goal_budget(db, user, body)
    record = WealthRecord(user_id=user.id, kind="goal", external_id=key, data=body.model_dump())
    db.add(record)
    audit(db, user, "goal.confirmed", {"message_id": record_id})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        record = db.query(WealthRecord).filter_by(user_id=user.id, kind="goal", external_id=key).first()
        if not record:
            raise HTTPException(409, "O plano mudou. Recarregue antes de confirmar.")
    return pack(record)


@router.get("/products")
def products(source: str = "", q: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Product)
    if source:
        query = query.filter(Product.id.startswith(source, autoescape=True))
    if q:
        query = query.filter(Product.data["name"].as_string().icontains(q[:200], autoescape=True))
    return {"total": query.count(), "products": [x.data for x in query.order_by(Product.id).limit(100)], "sources": ["Tesouro Transparente", "CVM"]}


@router.post("/products/sync/{source}")
@limiter.limit("2/hour")
def sync(request: Request, source: Literal["tesouro", "cvm"], user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        fetched = fetch_products(source)
    except Exception:
        raise HTTPException(503, "Fonte pública indisponível ou formato alterado. Os dados anteriores foram preservados.") from None
    # Retira elegibilidade dos itens que desapareceram da fonte.
    prefix = "td-" if source == "tesouro" else "cvm-"
    for row in db.query(Product).filter(Product.id.startswith(prefix)):
        row.data = {**row.data, "eligible": False}
    existing = {row.id: row for row in db.query(Product).all()}
    for item in {x["id"]:x for x in fetched}.values():
        row = existing.get(item["id"])
        if row:
            row.data = item
        else:
            db.add(Product(id=item["id"], data=item))
    audit(db, user, "catalog.synced", {"source": source, "count": len(fetched)})
    db.commit()
    return {"count": len(fetched), "source": source}


@router.get("/audit")
def events(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": x.id, "action": x.action, "data": x.data, "created_at": x.created_at.isoformat()}
            for x in db.query(AuditEvent).filter_by(user_id=user.id).order_by(AuditEvent.created_at.desc()).limit(100)]


@router.get("/integrations")
def integrations(user: User = Depends(get_current_user)):
    return [{"name": "Tesouro Transparente / CVM", "status": "Sincronização pública sob demanda"},
            {"name": "Open Finance", "status": "Requer parceiro participante e consentimento; não conectado"},
            {"name": "B3 / corretoras", "status": "Requer fonte contratada e catálogo de ofertas; não conectado"}]
