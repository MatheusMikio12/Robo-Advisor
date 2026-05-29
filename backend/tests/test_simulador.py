import pytest
from app.services.simulador import simular_carteira, RETORNOS_ANUAIS


CARTEIRA_CONSERVADORA = [
    {"ativo": "Renda Fixa", "percentual": 70},
    {"ativo": "ETFs", "percentual": 15},
    {"ativo": "Ações", "percentual": 5},
    {"ativo": "FIIs", "percentual": 10},
]

CARTEIRA_ARROJADA = [
    {"ativo": "Ações", "percentual": 60},
    {"ativo": "ETFs", "percentual": 25},
    {"ativo": "FIIs", "percentual": 10},
    {"ativo": "Renda Fixa", "percentual": 5},
]


class TestSimularCarteira:
    def test_retorna_campos_obrigatorios(self):
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, 5)
        campos = {"valor_final", "total_investido", "retorno_absoluto", "retorno_percentual", "cagr", "evolucao"}
        assert campos.issubset(resultado.keys())

    def test_valor_final_maior_que_total_investido(self):
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, 10)
        assert resultado["valor_final"] > resultado["total_investido"]

    def test_retorno_absoluto_correto(self):
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, 10)
        esperado = resultado["valor_final"] - resultado["total_investido"]
        assert abs(resultado["retorno_absoluto"] - esperado) < 0.01

    def test_total_investido_correto(self):
        aporte_inicial = 10000
        aporte_mensal = 500
        anos = 5
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, aporte_inicial, aporte_mensal, anos)
        esperado = aporte_inicial + aporte_mensal * anos * 12
        assert abs(resultado["total_investido"] - esperado) < 0.01

    def test_evolucao_tem_snapshot_por_ano(self):
        anos = 10
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, anos)
        assert len(resultado["evolucao"]) == anos

    def test_evolucao_ano_crescente(self):
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, 10)
        anos = [item["ano"] for item in resultado["evolucao"]]
        assert anos == list(range(1, 11))

    def test_carteira_arrojada_rende_mais_que_conservadora(self):
        r_cons = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, 20)
        r_arroj = simular_carteira(CARTEIRA_ARROJADA, 10000, 500, 20)
        assert r_arroj["valor_final"] > r_cons["valor_final"]

    def test_sem_aporte_mensal_cresce_apenas_com_juros(self):
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 0, 5)
        assert resultado["valor_final"] > 10000
        assert resultado["total_investido"] == 10000

    def test_zero_division_protegida(self):
        # aporte_inicial=0 e aporte_mensal=0 → total_investido=0, não deve estourar
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 0, 0, 5)
        assert resultado["retorno_percentual"] == 0.0
        assert resultado["cagr"] == 0.0

    def test_cagr_positivo_com_rendimento(self):
        resultado = simular_carteira(CARTEIRA_CONSERVADORA, 10000, 500, 10)
        assert resultado["cagr"] > 0

    def test_ativo_desconhecido_usa_retorno_zero(self):
        # Carteira com ativo fora do mapa → sem rendimento mas não estoura
        carteira = [{"ativo": "CriptoExotica", "percentual": 100}]
        resultado = simular_carteira(carteira, 10000, 0, 5)
        # Com retorno 0, valor final = aporte inicial + aportes mensais (sem juros)
        assert resultado["valor_final"] == pytest.approx(10000.0, abs=1.0)
