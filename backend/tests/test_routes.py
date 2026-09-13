"""
Testes de integração HTTP — cobrem os endpoints reais via TestClient do FastAPI.
Usam banco SQLite em memória para isolamento total entre testes.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.limiter import limiter
from app.database import Base, get_db

# Desabilita rate limiting nos testes — TestClient usa sempre o mesmo IP,
# o que estouraria os limites de /login e /register entre testes.
limiter.enabled = False
# Garante que todos os models SQLAlchemy estejam registrados no Base.metadata
from app.auth.models.user import User as _User  # noqa: F401
from app.models.suitability_db import PerfilSalvo as _PerfilSalvo  # noqa: F401
from app.models.revoked_token import RevokedToken as _RevokedToken  # noqa: F401

# ─── Banco em memória com conexão compartilhada (StaticPool) ─────────────────
# StaticPool garante que create_all e TestClient usam a mesma conexão SQLite.
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Recria o schema antes de cada teste — isolamento total, sem estado vazado."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ─── Helpers ─────────────────────────────────────────────────────────────────

USUARIO = {"email": "teste@example.com", "password": "Senha@123", "name": "Testador"}


class TestWealth:
    def test_conversational_goal_requires_confirmation_and_is_idempotent(self):
        from uuid import uuid4
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        conv = client.post("/wealth/conversations",headers=headers).json()["id"]
        for text in ["Criar um objetivo", "Viagem", "12000", "2", "0", "500"]:
            result = client.post(f"/wealth/conversations/{conv}/messages",headers=headers,json={"text":text,"request_id":str(uuid4())})
            assert result.status_code == 200
        message = result.json()
        assert client.get("/wealth/state",headers=headers).json()["goals"] == []
        first = client.post(f"/wealth/messages/{message['id']}/confirm-goal",headers=headers)
        second = client.post(f"/wealth/messages/{message['id']}/confirm-goal",headers=headers)
        assert first.status_code == second.status_code == 200
        assert first.json()["id"] == second.json()["id"]
        assert client.get("/wealth/state",headers=headers).json()["profile"] is None
        assert client.post("/wealth/recommendations",headers=headers).status_code == 409

    def test_goal_budget_conflict_is_rejected(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        client.put("/wealth/profile",headers=headers,json=self.diagnosis())
        goal = dict(name="Casa",target=100000,current=0,contribution=1500,years=10)
        assert client.post("/wealth/goals",headers=headers,json=goal).status_code == 200
        assert client.post("/wealth/goals",headers=headers,json=goal).status_code == 409

    @pytest.mark.parametrize("change", ["cancelar", "novo objetivo", "profile"])
    def test_outdated_conversational_proposals_cannot_be_confirmed(self, change):
        from uuid import uuid4
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        conv = client.post("/wealth/conversations",headers=headers).json()["id"]
        for text in ["Criar um objetivo", "Viagem", "12000", "2", "0", "500"]:
            result = client.post(f"/wealth/conversations/{conv}/messages",headers=headers,json={"text":text,"request_id":str(uuid4())})
        proposal = result.json()["id"]
        if change == "profile":
            client.put("/wealth/profile",headers=headers,json=self.diagnosis())
        else:
            client.post(f"/wealth/conversations/{conv}/messages",headers=headers,json={"text":change,"request_id":str(uuid4())})
        assert client.post(f"/wealth/messages/{proposal}/confirm-goal",headers=headers).status_code == 409
        assert client.get("/wealth/state",headers=headers).json()["goals"] == []


    @staticmethod
    def diagnosis():
        return dict(age=35,income=10000,expenses=4000,assets=150000,reserve=24000,debt=0,debt_rate=0,
                    contribution=2000,horizon=15,goal="crescimento",stability="estavel",experience="avancada",
                    loss_tolerance="alta",liquidity_months=120)

    def test_profile_persistence_and_recommendation_audit(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        assert client.post("/wealth/recommendations",headers=headers).status_code == 409
        assert client.put("/wealth/profile",json=self.diagnosis(),headers=headers).status_code == 200
        result = client.post("/wealth/recommendations",headers=headers)
        assert result.status_code == 200
        assert result.json()["profile_revision"] == 1
        state = client.get("/wealth/state",headers=headers).json()
        assert state["profile"]["expenses"] == 4000
        assert state["recommendation"]["id"] == result.json()["id"]
        assert len(client.get("/wealth/audit",headers=headers).json()) == 2
        assert client.put("/wealth/profile",json={**self.diagnosis(),"expenses":5000},headers=headers).json()["revision"] == 2

    def test_private_records_are_not_visible_to_other_user(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        goal = client.post("/wealth/goals",headers=headers,json=dict(name="Casa",target=100000,current=0,contribution=500,years=10)).json()
        conv = client.post("/wealth/conversations",headers=headers).json()
        client.post("/auth/register",json={"email":"other@example.com","password":"Senha@123"})
        token = client.post("/auth/login",data={"username":"other@example.com","password":"Senha@123"}).json()["access_token"]
        other = {"Authorization":f"Bearer {token}"}
        assert client.get("/wealth/state",headers=other).json()["goals"] == []
        assert client.get(f"/wealth/conversations/{conv['id']}/messages",headers=other).status_code == 404
        assert client.get(f"/wealth/goals/{goal['id']}/history",headers=other).status_code == 404
        assert client.get("/wealth/state").status_code == 401

    def test_conversation_tools_and_idempotency(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        client.put("/wealth/profile",json=self.diagnosis(),headers=headers)
        conv = client.post("/wealth/conversations",headers=headers).json()
        path = f"/wealth/conversations/{conv['id']}/messages"
        payload = {"text":"Como está minha reserva?","request_id":"one"}
        first = client.post(path,headers=headers,json=payload).json()
        assert first["agent"] == "orcamento"
        assert client.post(path,headers=headers,json=payload).json()["id"] == first["id"]
        assert len(client.get(path,headers=headers).json()) == 1

    def test_import_requires_confirmation_and_deduplicates(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        body = dict(format="csv",content="date,description,amount,id\n2026-09-01,Compra,-20,abc",account="A",confirm=False)
        assert client.post("/wealth/imports",json=body,headers=headers).json()["new_count"] == 1
        assert client.get("/wealth/state",headers=headers).json()["transactions"] == []
        body["confirm"] = True
        assert client.post("/wealth/imports",json=body,headers=headers).json()["new_count"] == 1
        assert client.post("/wealth/imports",json=body,headers=headers).json()["duplicates"] == 1
        assert client.get("/wealth/state",headers=headers).json()["cashflow"]["2026-09"] == -20

    def test_contribution_retries_do_not_duplicate_balance(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        goal = client.post("/wealth/goals",headers=headers,json=dict(name="Casa",target=100000,current=100,contribution=500,years=10)).json()
        path = f"/wealth/goals/{goal['id']}/contributions"
        body = dict(amount=500,date="2026-09-01",request_id="same")
        for _ in range(2):
            assert client.post(path,headers=headers,json=body).json()["current"] == 600

    def test_mfa_requires_code_and_invalidates_old_sessions(self):
        import pyotp
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        setup = client.post("/auth/mfa/setup",headers=headers,json={"password":"Senha@123"}).json()
        code = pyotp.TOTP(setup["secret"]).now()
        enabled = client.post("/auth/mfa/enable",headers=headers,json={"password":"Senha@123","code":code})
        assert enabled.status_code == 200
        assert client.get("/auth/me",headers=headers).status_code == 401
        creds = {"username":USUARIO["email"],"password":"Senha@123"}
        assert client.post("/auth/login",data=creds).status_code == 401
        assert client.post("/auth/login",data={**creds,"otp":code}).status_code == 200
        assert client.post("/auth/login",data={**creds,"otp":code}).status_code == 401

    def test_draft_is_not_a_confirmed_profile(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        body = {"answers":self.diagnosis(),"step":8}
        assert client.put("/wealth/draft",headers=headers,json=body).status_code == 200
        assert client.get("/wealth/draft",headers=headers).json()["step"] == 8
        assert client.get("/wealth/state",headers=headers).json()["profile"] is None
        client.put("/wealth/profile",headers=headers,json=self.diagnosis())
        assert client.get("/wealth/draft",headers=headers).json() is None

    def test_password_reset_is_single_use_and_invalidates_session(self):
        import hashlib
        from datetime import datetime, timedelta, timezone
        from app.models.wealth import WealthRecord
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        user_id = client.get("/auth/me",headers=headers).json()["id"]
        raw = "test-recovery-token-12345678901234567890"
        with TestingSessionLocal() as db:
            db.add(WealthRecord(user_id=user_id,kind="reset",external_id=hashlib.sha256(raw.encode()).hexdigest(),data={"expires":(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat(),"used":False}))
            db.commit()
        body={"token":raw,"password":"SenhaNova@456"}
        assert client.post("/auth/password/reset",json=body).status_code == 200
        assert client.post("/auth/password/reset",json=body).status_code == 400
        assert client.get("/auth/me",headers=headers).status_code == 401
        assert client.post("/auth/login",data={"username":USUARIO["email"],"password":"SenhaNova@456"}).status_code == 200

    def test_holdings_change_marks_recommendation_stale(self):
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        client.put("/wealth/profile",headers=headers,json=self.diagnosis())
        client.post("/wealth/recommendations",headers=headers)
        assert not client.get("/wealth/state",headers=headers).json()["recommendation_stale"]
        client.post("/wealth/holdings",headers=headers,json={"name":"ETF","institution":"Banco","issuer":"Emissor","asset_class":"global","value":10000,"currency":"BRL"})
        assert client.get("/wealth/state",headers=headers).json()["recommendation_stale"]

    def test_catalog_search_uses_literal_wildcards(self):
        from app.models.wealth import Product
        headers = {"Authorization": f"Bearer {registrar_e_logar()}"}
        with TestingSessionLocal() as db:
            db.add_all([Product(id="a",data={"id":"a","name":"Fundo 100%"}),Product(id="b",data={"id":"b","name":"Outro"})])
            db.commit()
        found = client.get("/wealth/products",params={"q":"%"},headers=headers).json()
        assert found["total"] == 1
        assert found["products"][0]["id"] == "a"


def registrar_e_logar() -> str:
    """Registra usuário e retorna token JWT."""
    client.post("/auth/register", json=USUARIO)
    resp = client.post(
        "/auth/login",
        data={"username": USUARIO["email"], "password": USUARIO["password"]},
    )
    return resp.json()["access_token"]


# ─── Auth ─────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_registro_cria_usuario(self):
        resp = client.post("/auth/register", json=USUARIO)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == USUARIO["email"]
        assert "id" in body
        assert "hashed_password" not in body

    def test_registro_email_duplicado_retorna_400(self):
        client.post("/auth/register", json=USUARIO)
        resp = client.post("/auth/register", json=USUARIO)
        assert resp.status_code == 400

    def test_login_valido_retorna_token(self):
        client.post("/auth/register", json=USUARIO)
        resp = client.post(
            "/auth/login",
            data={"username": USUARIO["email"], "password": USUARIO["password"]},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_login_senha_errada_retorna_401(self):
        resp = client.post(
            "/auth/login",
            data={"username": USUARIO["email"], "password": "errada"},
        )
        assert resp.status_code == 401

    def test_me_sem_token_retorna_401(self):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_com_token_retorna_usuario(self):
        token = registrar_e_logar()
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == USUARIO["email"]

    def test_login_retorna_refresh_token(self):
        client.post("/auth/register", json=USUARIO)
        resp = client.post(
            "/auth/login",
            data={"username": USUARIO["email"], "password": USUARIO["password"]},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "refresh_token" in body
        assert "access_token" in body

    def test_refresh_retorna_novo_access_token(self):
        client.post("/auth/register", json=USUARIO)
        login = client.post(
            "/auth/login",
            data={"username": USUARIO["email"], "password": USUARIO["password"]},
        )
        refresh_token = login.json()["refresh_token"]
        resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body

    def test_access_token_nao_serve_como_refresh(self):
        token = registrar_e_logar()
        resp = client.post("/auth/refresh", json={"refresh_token": token})
        assert resp.status_code == 401

    def test_refresh_token_invalido_retorna_401(self):
        resp = client.post("/auth/refresh", json={"refresh_token": "token.invalido.aqui"})
        assert resp.status_code == 401

    def test_token_malformado_retorna_401(self):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer nao.e.um.jwt"})
        assert resp.status_code == 401

    def test_token_alg_none_retorna_401(self):
        # Tentativa de bypass com algoritmo "none" (sem assinatura) deve ser rejeitada
        import base64
        import json

        def b64(d: dict) -> str:
            return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")

        forjado = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64({'sub': 'hacker@example.com'})}."
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {forjado}"})
        assert resp.status_code == 401

    def test_senha_fraca_sem_maiuscula_retorna_422(self):
        resp = client.post("/auth/register", json={"email": "fraca@example.com", "password": "senha1234"})
        assert resp.status_code == 422

    def test_senha_fraca_sem_numero_retorna_422(self):
        resp = client.post("/auth/register", json={"email": "fraca2@example.com", "password": "SenhaForte"})
        assert resp.status_code == 422

    def test_logout_revoga_refresh_token(self):
        client.post("/auth/register", json=USUARIO)
        login = client.post(
            "/auth/login",
            data={"username": USUARIO["email"], "password": USUARIO["password"]},
        )
        refresh_token = login.json()["refresh_token"]
        # Logout revoga o token
        logout = client.post("/auth/logout", json={"refresh_token": refresh_token})
        assert logout.status_code == 200
        # Token revogado não pode mais renovar a sessão
        resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 401

    def test_logout_token_invalido_nao_estoura(self):
        resp = client.post("/auth/logout", json={"refresh_token": "token.invalido"})
        assert resp.status_code == 200

    def test_refresh_rotaciona_e_invalida_token_anterior(self):
        client.post("/auth/register", json=USUARIO)
        login = client.post(
            "/auth/login",
            data={"username": USUARIO["email"], "password": USUARIO["password"]},
        )
        refresh_token = login.json()["refresh_token"]
        # Primeiro refresh: sucesso, retorna novo par
        primeiro = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert primeiro.status_code == 200
        # Reusar o token antigo (rotação) deve falhar
        replay = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert replay.status_code == 401
        # O novo token funciona
        novo = primeiro.json()["refresh_token"]
        terceiro = client.post("/auth/refresh", json={"refresh_token": novo})
        assert terceiro.status_code == 200


# ─── Planejamento ─────────────────────────────────────────────────────────────

PLANEJAMENTO_PAYLOAD = {
    "idade": 30,
    "renda_mensal": 5000,
    "patrimonio_atual": 20000,
    "aporte_mensal": 1000,
    "prazo_anos": 10,
    "objetivo": "crescimento",
}


class TestPlanejamento:
    def test_sem_auth_retorna_401(self):
        resp = client.post("/planejamento", json=PLANEJAMENTO_PAYLOAD)
        assert resp.status_code == 401

    def test_planejamento_completo_retorna_estrutura_correta(self):
        token = registrar_e_logar()
        resp = client.post(
            "/planejamento",
            json=PLANEJAMENTO_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "perfil" in body
        assert body["perfil"] in ("Conservador", "Moderado", "Arrojado")
        assert "carteira" in body
        assert "resumo" in body
        assert "evolucao" in body

    def test_planejamento_retorna_evolucao_anual(self):
        token = registrar_e_logar()
        resp = client.post(
            "/planejamento",
            json=PLANEJAMENTO_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        evolucao = resp.json()["evolucao"]
        assert len(evolucao) == PLANEJAMENTO_PAYLOAD["prazo_anos"]
        assert evolucao[-1]["ano"] == PLANEJAMENTO_PAYLOAD["prazo_anos"]

    def test_planejamento_valor_final_maior_que_investido(self):
        token = registrar_e_logar()
        resp = client.post(
            "/planejamento",
            json=PLANEJAMENTO_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        resumo = resp.json()["resumo"]
        assert resumo["valor_final"] > resumo["total_investido"]


# ─── Simulação ────────────────────────────────────────────────────────────────

SIMULACAO_VALIDA = {
    "carteira": [
        {"ativo": "Renda Fixa", "percentual": 60},
        {"ativo": "Ações", "percentual": 40},
    ],
    "aporte_inicial": 10000,
    "aporte_mensal": 500,
    "anos": 5,
}


class TestSimulacao:
    def test_sem_auth_retorna_401(self):
        resp = client.post("/simulacao", json=SIMULACAO_VALIDA)
        assert resp.status_code == 401

    def test_simulacao_valida_retorna_resultado(self):
        token = registrar_e_logar()
        resp = client.post(
            "/simulacao",
            json=SIMULACAO_VALIDA,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["valor_final"] > 0
        assert len(body["evolucao"]) == SIMULACAO_VALIDA["anos"]

    def test_carteira_percentuais_nao_somam_100_retorna_422(self):
        token = registrar_e_logar()
        payload = {**SIMULACAO_VALIDA, "carteira": [
            {"ativo": "Renda Fixa", "percentual": 60},
            {"ativo": "Ações", "percentual": 30},  # soma = 90, não 100
        ]}
        resp = client.post(
            "/simulacao",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_carteira_vazia_retorna_422(self):
        token = registrar_e_logar()
        payload = {**SIMULACAO_VALIDA, "carteira": []}
        resp = client.post(
            "/simulacao",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422


# ─── Recomendação ─────────────────────────────────────────────────────────────

PERFIL_ARROJADO = {
    "idade": 25,
    "renda": 8000,
    "patrimonio": 150000,
    "horizonte_anos": 15,
    "objetivo": "crescimento",
}

PERFIL_CONSERVADOR = {
    "idade": 60,
    "renda": 3000,
    "patrimonio": 5000,
    "horizonte_anos": 3,
    "objetivo": "reserva",
}


class TestRecomendacao:
    def test_sem_auth_retorna_401(self):
        resp = client.post("/recomendacao", json=PERFIL_ARROJADO)
        assert resp.status_code == 401

    def test_perfil_arrojado_retorna_mais_acoes(self):
        token = registrar_e_logar()
        resp = client.post(
            "/recomendacao",
            json=PERFIL_ARROJADO,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["perfil_classificado"] == "Arrojado"
        acoes = next(i for i in body["carteira_recomendada"] if i["ativo"] == "Ações")
        assert acoes["percentual"] >= 20

    def test_perfil_conservador_retorna_mais_renda_fixa(self):
        token = registrar_e_logar()
        resp = client.post(
            "/recomendacao",
            json=PERFIL_CONSERVADOR,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["perfil_classificado"] == "Conservador"
        rf = next(i for i in body["carteira_recomendada"] if i["ativo"] == "Renda Fixa")
        assert rf["percentual"] >= 60

    def test_recomendacao_retorna_explicacao_textual(self):
        token = registrar_e_logar()
        resp = client.post(
            "/recomendacao",
            json=PERFIL_ARROJADO,
            headers={"Authorization": f"Bearer {token}"},
        )
        body = resp.json()
        assert "explicacao" in body
        assert len(body["explicacao"]) > 20


# ─── Suitability (persistência) ───────────────────────────────────────────────

PERFIL_SUITABILITY = {
    "idade": 35,
    "renda": 6000,
    "patrimonio": 50000,
    "horizonte_anos": 10,
    "objetivo": "aposentadoria",
}


class TestSuitability:
    def test_sem_auth_retorna_401(self):
        resp = client.post("/suitability", json=PERFIL_SUITABILITY)
        assert resp.status_code == 401

    def test_get_me_sem_perfil_retorna_404(self):
        token = registrar_e_logar()
        resp = client.get("/suitability/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_salvar_perfil_retorna_classificacao(self):
        token = registrar_e_logar()
        resp = client.post(
            "/suitability",
            json=PERFIL_SUITABILITY,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "perfil_classificado" in body
        assert body["perfil_classificado"] in ("Conservador", "Moderado", "Arrojado")
        assert "id" in body

    def test_get_me_retorna_perfil_salvo(self):
        token = registrar_e_logar()
        client.post("/suitability", json=PERFIL_SUITABILITY, headers={"Authorization": f"Bearer {token}"})
        resp = client.get("/suitability/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["idade"] == PERFIL_SUITABILITY["idade"]
        assert body["objetivo"] == PERFIL_SUITABILITY["objetivo"]

    def test_segundo_post_atualiza_perfil(self):
        token = registrar_e_logar()
        client.post("/suitability", json=PERFIL_SUITABILITY, headers={"Authorization": f"Bearer {token}"})
        perfil_novo = {**PERFIL_SUITABILITY, "objetivo": "crescimento", "patrimonio": 200000}
        client.post("/suitability", json=perfil_novo, headers={"Authorization": f"Bearer {token}"})
        resp = client.get("/suitability/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.json()["objetivo"] == "crescimento"
        assert resp.json()["perfil_classificado"] == "Arrojado"
