from datetime import date, timedelta
import pytest
from pydantic import ValidationError
from app.models.wealth_schemas import Diagnosis, Simulation
from app.services.wealth_engine import policy, recommend, simulate
from app.services.statement_import import parse_statement
from app.services.catalog import treasury_csv


def diagnosis(**overrides):
    return Diagnosis(**{**dict(age=35, income=10000, expenses=4000, assets=150000, reserve=24000,
        debt=0, debt_rate=0, contribution=2000, horizon=15, goal="crescimento", stability="estavel",
        experience="avancada", loss_tolerance="alta", liquidity_months=120), **overrides})


@pytest.mark.parametrize("change", [{"reserve":0}, {"debt":10000,"debt_rate":50}, {"horizon":1}, {"liquidity_months":1}, {"loss_tolerance":"nenhuma"}, {"experience":"nenhuma"}])
def test_constraints_override_declared_high_risk(change):
    result = policy(diagnosis(**change))
    assert result["risk_score"] == 0
    assert result["allocation"] == [{"key":"liquidez","name":"Liquidez e reserva","percent":100}]


def test_budget_reserve_and_exclusions():
    result = policy(diagnosis(contribution=9000, stability="variavel", reserve=40000, excluded_classes=["brasil","global"]))
    assert result["contribution"] == 6000
    assert result["reserve_target"] == 36000
    assert sum(x["percent"] for x in result["allocation"]) == 100
    assert not any(x["key"] in ("brasil","global") for x in result["allocation"])


def test_reserve_not_counted_twice():
    assert policy(diagnosis())["investable"] == 126000
    with pytest.raises(ValidationError):
        diagnosis(reserve=200000)
    with pytest.raises(ValidationError):
        diagnosis(income=float("nan"))


def test_products_missing_stale_or_incompatible_never_selected():
    p = diagnosis()
    products = [{"id":"expired","name":"Antigo","asset_class":"liquidez","as_of":(date.today()-timedelta(days=8)).isoformat(),"eligible":True,"risk":0,"currency":"BRL","platform":"Tesouro Direto","minimum":1,"liquidity_days":1}]
    result = recommend(p,products,[])
    assert not any(slot["products"] for slot in result["allocation"])
    assert "validade" in result["excluded"][0]["reasons"][0]
    assert sum(x["unallocated_percent"] for x in result["allocation"]) == 100


def test_issuer_limit_and_no_double_count_holdings():
    product = {"id":"one","name":"Produto","asset_class":"liquidez","as_of":date.today().isoformat(),"eligible":True,"risk":0,"currency":"BRL","platform":"Banco A","issuer":"Banco A","minimum":1,"liquidity_days":1}
    p = diagnosis(loss_tolerance="nenhuma", institutions=["Banco A"])
    r = recommend(p,[product],[])
    assert r["allocation"][0]["products"][0]["amount"] == 38000
    assert r["allocation"][0]["products"][0]["amount"] <= (p.assets+p.contribution)*.25


def test_simulation_zero_return_closed_form_and_reproducibility():
    s = Simulation(initial=1000,contribution=100,years=2,annual_return=0,volatility=0,inflation=0,fees=0,tax=0,target=3400,paths=100)
    r = simulate(s)
    assert r == simulate(s)
    assert r["series"][-1]["p50"] == 3400
    assert r["success_probability"] == 100


def test_pause_and_withdrawals_are_not_contributions():
    s = Simulation(initial=1000,contribution=100,years=1,annual_return=0,volatility=0,inflation=0,fees=0,tax=0,pause_start=1,pause_months=6,paths=100)
    assert simulate(s)["series"][-1]["p50"] == 1600
    r = simulate(s.model_copy(update={"withdrawal_start":7,"monthly_withdrawal":300}))
    assert r["series"][-1]["p50"] == 0
    assert r["depletion_probability"] == 100


def test_tax_only_on_gains_and_inflation_reduces_purchasing_power():
    s = Simulation(initial=1000,contribution=0,years=1,annual_return=10,volatility=0,inflation=0,fees=0,tax=20,paths=100)
    assert simulate(s)["series"][-1]["p50"] == 1080
    assert simulate(s.model_copy(update={"inflation":10}))["series"][-1]["p50"] == 981.82
    assert simulate(s.model_copy(update={"annual_return":-10}))["series"][-1]["p50"] == 900


def test_statement_dedup_identity_and_account_scope():
    csv = "date,description,amount,id\n2026-09-01,Salario,5000,a\n2026-09-02,Compra,-20,b"
    first = parse_statement(csv,"csv","Conta A")
    assert first == parse_statement(csv,"csv","Conta A")
    assert first[0]["external_id"] != parse_statement(csv,"csv","Conta B")[0]["external_id"]
    assert first[1]["amount"] == -20
    with pytest.raises(ValueError): parse_statement(csv.replace("5000","NaN"),"csv","A")


def test_ofx_sgml_and_xml_external_entities():
    source = "<OFX><STMTTRN><DTPOSTED>20260901<TRNAMT>-15.50<FITID>x<NAME>Compra</STMTTRN></OFX>"
    assert parse_statement(source,"ofx","A")[0]["amount"] == -15.5
    with pytest.raises(ValueError): parse_statement("<!ENTITY x SYSTEM 'file:///secret'>"+source,"ofx","A")


def test_treasury_selects_latest_date_even_if_input_unsorted():
    csv = "Tipo Titulo;Data Vencimento;Data Base;PU Compra Manha;Taxa Compra Manha\nTesouro Selic;01/01/2040;01/09/2026;1000,00;0,1\nTesouro Selic;01/01/2040;02/09/2026;1010,00;0,2\nTesouro Selic;01/01/2040;01/09/2026;1000,00;0,1"
    result = treasury_csv(csv.encode())
    assert len(result) == 1 and result[0]["price"] == 1010
    assert result[0]["as_of"] == "2026-09-02"
    assert result[0]["minimum"] == 10.1


def test_cvm_preserves_portuguese_and_does_not_enable_incomplete_products():
    import io
    import zipfile
    from app.services.catalog import cvm_zip
    archive = io.BytesIO()
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("registro_fundo.csv", "CNPJ_Fundo;Denominacao_Social;Situacao\n12345678900001;Fundo Ações;Em funcionamento\n".encode("latin-1"))
    result = cvm_zip(archive.getvalue())
    assert result[0]["name"] == "Fundo Ações"
    assert result[0]["eligible"] is False
