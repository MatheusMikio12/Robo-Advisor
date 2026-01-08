from app.models.perfil import PerfilInvestidor

def classificar_perfil(perfil: PerfilInvestidor) -> str:
    score = 0

    # Idade
    if perfil.idade < 30:
        score += 2
    elif perfil.idade < 45:
        score += 1

    # Horizonte
    if perfil.horizonte_anos >= 10:
        score += 2
    elif perfil.horizonte_anos >= 5:
        score += 1

    # Patrimônio / renda (proxy de risco)
    if perfil.patrimonio > 100000:
        score += 2
    elif perfil.patrimonio > 30000:
        score += 1

    # Classificação final
    if score <= 2:
        return "Conservador"
    elif score <= 4:
        return "Moderado"
    else:
        return "Agressivo"
