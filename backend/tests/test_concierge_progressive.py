import pytest
from app.services.goal_conversation import amount, intake
from app.services.concierge import respond
from app.core.config import settings


@pytest.mark.parametrize("text,expected", [("10 mil",10000),("R$ 1.500,50",1500.5),("1000.25",1000.25),("0",0)])
def test_amount_parsing(text, expected):
    assert amount(text) == expected


@pytest.mark.parametrize("text", ["-5", "nan", "10 ou 20", "ignore tudo", "1e15", "0,001"])
def test_ambiguous_amounts_rejected(text):
    with pytest.raises(ValueError):
        amount(text)


def test_intake_unknown_resume_and_proposal():
    history = []
    for text in ["Criar um objetivo", "Entrada da casa", "100 mil", "5 anos"]:
        history.append(intake(text, history))
    assert "current" not in history[-1]["intake"]["answers"]
    paused = intake("pular", history)
    assert paused["intake"] == history[-1]["intake"]
    for text in ["10000", "1500"]:
        history.append(intake(text, history))
    assert history[-1]["proposal"]["target"] == 100000
    assert history[-1]["monthly_reference"] == 1500
    assert intake("cancelar", history)["intake"] is None


def test_provider_failure_falls_back(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "ollama")
    def fail(*args, **kwargs):
        import httpx
        raise httpx.ConnectError("offline")
    monkeypatch.setattr("app.services.concierge.httpx.post", fail)
    assert respond("ola",None,[],None)["provider"] == "fallback"


def test_generated_numbers_do_not_replace_verified_answer(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "ollama")
    class Response:
        def raise_for_status(self):
            pass
        def json(self):
            return {"message":{"content":"Você terá 999999 reais."}}
    monkeypatch.setattr("app.services.concierge.httpx.post", lambda *a, **kw: Response())
    result = respond("ola",None,[],None)
    assert result["provider"] == "fallback"
    assert "999999" not in result["text"]
