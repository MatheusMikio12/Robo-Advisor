from app.models.perfil import PerfilInvestidor


def classificar_perfil(perfil: PerfilInvestidor) -> str:
    """
    Classifica o perfil de risco do investidor com base em 4 dimensões:
    idade, horizonte de investimento, patrimônio e objetivo financeiro.

    Retorna: "Conservador", "Moderado" ou "Arrojado"
    """
    score = 0

    # 1️⃣ Idade — jovens podem assumir mais risco
    if perfil.idade < 30:
        score += 2
    elif perfil.idade < 45:
        score += 1
    # 45+ não pontua (mais conservador)

    # 2️⃣ Horizonte de investimento — prazos longos diluem risco
    if perfil.horizonte_anos >= 10:
        score += 2
    elif perfil.horizonte_anos >= 5:
        score += 1

    # 3️⃣ Patrimônio — maior colchão financeiro = mais tolerância a risco
    if perfil.patrimonio > 100000:
        score += 2
    elif perfil.patrimonio > 30000:
        score += 1

    # 4️⃣ Objetivo — influencia a tolerância a risco
    if perfil.objetivo == "crescimento":
        score += 2  # busca retorno agressivo
    elif perfil.objetivo == "aposentadoria":
        score += 1  # longo prazo, pode arriscar moderadamente
    elif perfil.objetivo == "imovel":
        score += 0  # prazo definido, risco equilibrado
    elif perfil.objetivo == "reserva":
        score -= 1  # reserva de emergência = conservador

    # Classificação final
    if score <= 2:
        return "Conservador"
    elif score <= 4:
        return "Moderado"
    else:
        return "Arrojado"
