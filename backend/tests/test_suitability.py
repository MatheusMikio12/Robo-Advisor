import pytest
from app.models.perfil import PerfilInvestidor
from app.services.suitability import classificar_perfil


def _perfil(**kwargs) -> PerfilInvestidor:
    defaults = {
        "idade": 35,
        "renda": 5000,
        "patrimonio": 50000,
        "horizonte_anos": 10,
        "objetivo": "aposentadoria",
    }
    return PerfilInvestidor(**{**defaults, **kwargs})


class TestClassificarPerfil:
    def test_jovem_longo_prazo_rico_crescimento_e_arrojado(self):
        perfil = _perfil(idade=25, horizonte_anos=15, patrimonio=150000, objetivo="crescimento")
        assert classificar_perfil(perfil) == "Arrojado"

    def test_idoso_curto_prazo_sem_patrimonio_reserva_e_conservador(self):
        perfil = _perfil(idade=60, horizonte_anos=3, patrimonio=10000, objetivo="reserva")
        assert classificar_perfil(perfil) == "Conservador"

    def test_perfil_moderado_tipico(self):
        # Idade 40 (+1), horizonte 7 anos (+1), patrimônio 50k (+1), aposentadoria (+1) = 4 → Moderado
        perfil = _perfil(idade=40, horizonte_anos=7, patrimonio=50000, objetivo="aposentadoria")
        assert classificar_perfil(perfil) == "Moderado"

    def test_objetivo_reserva_penaliza_score(self):
        # Mesmo perfil moderado com objetivo "reserva" em vez de "aposentadoria" → mais conservador
        perfil_apos = _perfil(idade=40, horizonte_anos=7, patrimonio=50000, objetivo="aposentadoria")
        perfil_res = _perfil(idade=40, horizonte_anos=7, patrimonio=50000, objetivo="reserva")
        score_apos = classificar_perfil(perfil_apos)
        score_res = classificar_perfil(perfil_res)
        # reserva deve resultar em perfil igual ou mais conservador
        perfis = ["Conservador", "Moderado", "Arrojado"]
        assert perfis.index(score_apos) >= perfis.index(score_res)

    def test_objetivo_crescimento_aumenta_score(self):
        # crescimento deve resultar em perfil igual ou mais arrojado que imovel
        perfil_cresc = _perfil(objetivo="crescimento")
        perfil_imovel = _perfil(objetivo="imovel")
        perfis = ["Conservador", "Moderado", "Arrojado"]
        assert perfis.index(classificar_perfil(perfil_cresc)) >= perfis.index(classificar_perfil(perfil_imovel))

    def test_retorna_apenas_valores_validos(self):
        for objetivo in ("aposentadoria", "imovel", "reserva", "crescimento"):
            perfil = _perfil(objetivo=objetivo)
            resultado = classificar_perfil(perfil)
            assert resultado in ("Conservador", "Moderado", "Arrojado")

    def test_fronteira_idade_30(self):
        # Exatamente 30 anos não pontua (< 30 pontua)
        jovem = _perfil(idade=29)
        trinta = _perfil(idade=30)
        perfis = ["Conservador", "Moderado", "Arrojado"]
        assert perfis.index(classificar_perfil(jovem)) >= perfis.index(classificar_perfil(trinta))

    def test_fronteira_horizonte_10_anos(self):
        # >= 10 anos pontua 2; >= 5 pontua 1
        longo = _perfil(horizonte_anos=10)
        medio = _perfil(horizonte_anos=5)
        curto = _perfil(horizonte_anos=4)
        perfis = ["Conservador", "Moderado", "Arrojado"]
        assert perfis.index(classificar_perfil(longo)) >= perfis.index(classificar_perfil(medio))
        assert perfis.index(classificar_perfil(medio)) >= perfis.index(classificar_perfil(curto))
