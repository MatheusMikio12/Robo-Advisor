import pytest
from app.services.planejador import (
    calcular_meta,
    calcular_aporte_necessario,
    calcular_prazo_necessario,
    RETORNOS_POR_OBJETIVO,
)


class TestCalcularAporteNecessario:
    def test_retorna_float_positivo(self):
        aporte = calcular_aporte_necessario(1_000_000, 50_000, 20, 0.09)
        assert isinstance(aporte, float)
        assert aporte > 0

    def test_aporte_maior_meta_menor(self):
        # Meta menor exige aporte menor
        a1 = calcular_aporte_necessario(500_000, 0, 10, 0.09)
        a2 = calcular_aporte_necessario(1_000_000, 0, 10, 0.09)
        assert a2 > a1

    def test_aporte_menor_com_patrimonio_inicial(self):
        sem_patrimonio = calcular_aporte_necessario(1_000_000, 0, 20, 0.09)
        com_patrimonio = calcular_aporte_necessario(1_000_000, 100_000, 20, 0.09)
        assert com_patrimonio < sem_patrimonio

    def test_tolerancia_convergencia(self):
        meta = 1_000_000
        aporte = calcular_aporte_necessario(meta, 0, 20, 0.09)
        from app.services.planejador import _simular_valor_futuro
        resultado = _simular_valor_futuro(0, aporte, 20, 0.09)
        # Deve chegar a ±1% da meta
        assert abs(resultado["valor_final"] - meta) / meta < 0.01


class TestCalcularPrazoNecessario:
    def test_retorna_inteiro(self):
        prazo = calcular_prazo_necessario(1_000_000, 50_000, 3000, 0.09)
        assert isinstance(prazo, int)

    def test_meta_alcancavel(self):
        prazo = calcular_prazo_necessario(100_000, 50_000, 2000, 0.09)
        assert prazo > 0

    def test_meta_inalcancavel_retorna_menos_um(self):
        # Aporte ínfimo para meta enorme → inalcançável em 50 anos
        prazo = calcular_prazo_necessario(10_000_000_000, 0, 1, 0.05)
        assert prazo == -1

    def test_prazo_menor_com_aporte_maior(self):
        p1 = calcular_prazo_necessario(1_000_000, 0, 1000, 0.09)
        p2 = calcular_prazo_necessario(1_000_000, 0, 5000, 0.09)
        assert p1 > p2


class TestCalcularMeta:
    def test_modo_calcular_aporte_sem_aporte_mensal(self):
        resultado = calcular_meta(
            valor_alvo=1_000_000,
            patrimonio_atual=50_000,
            objetivo="aposentadoria",
            prazo_desejado=20,
        )
        assert resultado["modo"] == "calcular_aporte"
        assert resultado["aporte_mensal"] > 0
        assert resultado["prazo_anos"] == 20

    def test_modo_calcular_prazo_sem_prazo_desejado(self):
        resultado = calcular_meta(
            valor_alvo=500_000,
            patrimonio_atual=10_000,
            objetivo="crescimento",
            aporte_mensal=2000,
        )
        assert resultado["modo"] == "calcular_prazo"
        assert resultado["prazo_anos"] > 0

    def test_modo_meta_ja_atingida(self):
        resultado = calcular_meta(
            valor_alvo=50_000,
            patrimonio_atual=100_000,
            objetivo="reserva",
        )
        assert resultado["modo"] == "meta_ja_atingida"
        assert resultado["meta_atingida"] is True
        assert resultado["progresso_atual"] >= 100

    def test_retornos_por_objetivo_usados(self):
        for objetivo, taxa in RETORNOS_POR_OBJETIVO.items():
            resultado = calcular_meta(
                valor_alvo=500_000,
                patrimonio_atual=0,
                objetivo=objetivo,
                aporte_mensal=2000,
            )
            assert resultado["retorno_anual_estimado"] == pytest.approx(taxa * 100, abs=0.01)

    def test_meta_inalcancavel_em_50_anos(self):
        resultado = calcular_meta(
            valor_alvo=10_000_000_000,
            patrimonio_atual=0,
            objetivo="reserva",
            aporte_mensal=1,
        )
        assert resultado["prazo_anos"] == -1
        assert resultado["meta_atingida"] is False
        assert "mensagem" in resultado

    def test_progresso_atual_percentual(self):
        resultado = calcular_meta(
            valor_alvo=100_000,
            patrimonio_atual=25_000,
            objetivo="imovel",
            aporte_mensal=1000,
        )
        assert resultado["progresso_atual"] == pytest.approx(25.0, abs=0.01)

    def test_simulacao_contem_campos_obrigatorios(self):
        resultado = calcular_meta(
            valor_alvo=200_000,
            patrimonio_atual=0,
            objetivo="crescimento",
            aporte_mensal=1500,
        )
        sim = resultado["simulacao"]
        assert "valor_final" in sim
        assert "total_aportado" in sim
        assert "rendimento" in sim
        assert "evolucao_anual" in sim

    def test_verificar_viabilidade_com_ambos_informados(self):
        resultado = calcular_meta(
            valor_alvo=1_000_000,
            patrimonio_atual=100_000,
            objetivo="aposentadoria",
            aporte_mensal=3000,
            prazo_desejado=25,
        )
        assert resultado["modo"] == "verificar_viabilidade"
        assert "meta_atingida" in resultado
        assert "mensagem" in resultado
