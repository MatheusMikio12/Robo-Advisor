def simular_carteira(
    carteira: dict,
    aporte_inicial: float,
    aporte_mensal: float,
    anos: int
):
    retornos_anuais = {
        "Renda Fixa": 0.08,
        "ETFs": 0.10,
        "Ações": 0.12,
        "FIIs": 0.09
    }

    meses = anos * 12
    saldo = aporte_inicial
    historico = []

    for mes in range(1, meses + 1):
        saldo += aporte_mensal

        retorno_mensal = 0
        for classe, percentual in carteira.items():
            retorno_ano = retornos_anuais.get(classe, 0)
            retorno_mensal += (percentual / 100) * (retorno_ano / 12)

        saldo *= (1 + retorno_mensal)

        historico.append({
            "mes": mes,
            "saldo": round(saldo, 2)
        })

    return {
        "valor_final": round(saldo, 2),
        "historico": historico
    }
