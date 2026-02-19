from app.models.perfil import PerfilInvestidor


CARTEIRAS = {
    "Conservador": {
        "Renda Fixa": 70,
        "ETFs": 15,
        "Ações": 5,
        "FIIs": 10,
    },
    "Moderado": {
        "Renda Fixa": 45,
        "ETFs": 30,
        "Ações": 15,
        "FIIs": 10,
    },
    "Arrojado": {
        "Renda Fixa": 25,
        "ETFs": 40,
        "Ações": 25,
        "FIIs": 10,
    },
}

DESCRICOES_ATIVOS = {
    "Renda Fixa": "CDBs, LCIs, LCAs e Tesouro Direto — segurança e previsibilidade",
    "ETFs": "Fundos de índice — diversificação com baixo custo",
    "Ações": "Ações de empresas listadas na B3 — maior potencial de retorno",
    "FIIs": "Fundos imobiliários — renda passiva com dividendos mensais",
}


def gerar_carteira(perfil_classificado: str) -> list[dict]:
    """Gera a carteira recomendada com base no perfil classificado."""
    if perfil_classificado not in CARTEIRAS:
        raise ValueError(f"Perfil desconhecido: {perfil_classificado}")

    carteira_dict = CARTEIRAS[perfil_classificado]
    return [
        {
            "ativo": ativo,
            "percentual": percentual,
            "descricao": DESCRICOES_ATIVOS.get(ativo, ""),
        }
        for ativo, percentual in carteira_dict.items()
    ]


def explicar_recomendacao(perfil_classificado: str, perfil: PerfilInvestidor) -> str:
    """Gera uma explicação textual da recomendação para o usuário."""
    objetivos_label = {
        "aposentadoria": "aposentadoria",
        "imovel": "compra de imóvel",
        "reserva": "reserva de emergência",
        "crescimento": "crescimento patrimonial",
    }
    objetivo_texto = objetivos_label.get(perfil.objetivo, perfil.objetivo)

    return (
        f"Seu perfil foi classificado como {perfil_classificado} "
        f"considerando sua idade ({perfil.idade} anos), "
        f"horizonte de investimento de {perfil.horizonte_anos} anos "
        f"e objetivo de {objetivo_texto}. "
        f"A alocação proposta busca equilibrar risco e retorno "
        f"de acordo com esse perfil."
    )
