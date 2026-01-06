def classificar_perfil(perfil):
    score = 0

    # Horizonte de investimento
    if perfil.horizonte_anos >= 10:
        score += 2
    elif perfil.horizonte_anos >= 5:
        score += 1

    # Tolerância ao risco
    score += perfil.tolerancia_risco

    # Idade (quanto mais jovem, mais risco)
    if perfil.idade < 35:
        score += 2
    elif perfil.idade < 50:
        score += 1

    if score <= 5:
        return "Conservador"
    elif score <= 8:
        return "Moderado"
    else:
        return "Arrojado"
