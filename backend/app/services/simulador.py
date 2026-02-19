# ─── Retornos anuais estimados por classe de ativo ──────────────────
# Constante no nível do módulo (evita recriação a cada chamada)
RETORNOS_ANUAIS = {
    "Renda Fixa": 0.08,
    "ETFs": 0.10,
    "Ações": 0.12,
    "FIIs": 0.09,
}


def simular_carteira(
    carteira: list,
    aporte_inicial: float,
    aporte_mensal: float,
    anos: int,
):
    """
    Simula a evolução patrimonial de uma carteira diversificada.

    Correções aplicadas:
    - Juros compostos (antes usava juros simples: retorno/12)
    - Proteção contra ZeroDivisionError quando total_investido == 0
    - Histórico salva apenas snapshots anuais (antes salvava todos os meses)
    """
    meses = anos * 12
    saldo = aporte_inicial
    evolucao = []

    # Pré-calcular a taxa mensal ponderada da carteira (juros compostos)
    retorno_mensal_ponderado = 0.0
    for item in carteira:
        classe = item["ativo"]
        percentual = item["percentual"]
        retorno_ano = RETORNOS_ANUAIS.get(classe, 0)
        # Conversão de taxa anual → mensal via juros compostos
        taxa_mensal = (1 + retorno_ano) ** (1 / 12) - 1
        retorno_mensal_ponderado += (percentual / 100) * taxa_mensal

    for mes in range(1, meses + 1):
        saldo += aporte_mensal
        saldo *= (1 + retorno_mensal_ponderado)

        # Salva snapshot apenas ao final de cada ano (otimização)
        if mes % 12 == 0:
            evolucao.append({
                "ano": mes // 12,
                "valor": round(saldo, 2),
            })

    # 📊 MÉTRICAS — com proteção contra divisão por zero
    total_investido = aporte_inicial + (aporte_mensal * meses)

    if total_investido > 0:
        retorno_absoluto = saldo - total_investido
        retorno_percentual = (retorno_absoluto / total_investido) * 100
        cagr = (saldo / total_investido) ** (1 / anos) - 1
    else:
        retorno_absoluto = 0.0
        retorno_percentual = 0.0
        cagr = 0.0

    # Fallback se não houver evolução (prazo < 1 ano)
    if not evolucao:
        evolucao = [{"ano": 0, "valor": aporte_inicial}]

    return {
        "valor_final": round(saldo, 2),
        "total_investido": round(total_investido, 2),
        "retorno_absoluto": round(retorno_absoluto, 2),
        "retorno_percentual": round(retorno_percentual, 2),
        "cagr": round(cagr * 100, 2),  # em %
        "evolucao": evolucao,
    }
