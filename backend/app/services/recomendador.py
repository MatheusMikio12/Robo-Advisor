def gerar_carteira(perfil_classificado):
    carteiras = {
        "Conservador": {
            "Renda Fixa": 70,
            "ETFs": 15,
            "Ações": 5,
            "FIIs": 10
        },
        "Moderado": {
            "Renda Fixa": 45,
            "ETFs": 30,
            "Ações": 15,
            "FIIs": 10
        },
        "Arrojado": {
            "Renda Fixa": 25,
            "ETFs": 40,
            "Ações": 25,
            "FIIs": 10
        }
    }
    return carteiras[perfil_classificado]


def explicar_recomendacao(perfil_classificado, perfil):
    return (
        f"Seu perfil foi classificado como {perfil_classificado} "
        f"considerando sua idade ({perfil.idade} anos), "
        f"horizonte de investimento de {perfil.horizonte_anos} anos "
        f"e tolerância ao risco nível {perfil.tolerancia_risco}. "
        f"A alocação proposta busca equilibrar risco e retorno "
        f"de acordo com esse perfil."
    )
