"""
📌 SERVICE planejador.py — Cérebro do Sistema de Metas Financeiras.

CONCEITOS IMPORTANTES:

1. JUROS COMPOSTOS:
   Fórmula: valor_futuro = valor_presente * (1 + taxa_mensal) ^ meses + aporte * [(1+r)^n - 1] / r
   Mas aqui usamos simulação mês a mês (mais didático e flexível).

2. BUSCA BINÁRIA (Binary Search):
   - Problema: "Qual aporte mensal preciso para chegar a R$ 1M em 10 anos?"
   - Solução ingênua: testar aporte=1, aporte=2, ..., aporte=50000 → LENTO (O(n))
   - Busca binária: testa o MEIO, descarta metade, repete → RÁPIDO (O(log n))
   
   Exemplo visual (buscando aporte para R$ 1M):
   [0 ────────── 50000 ────────── 100000]  → meio=50000, resultado=R$2M → muito alto
   [0 ────────── 25000]                    → meio=25000, resultado=R$800K → baixo
   [25000 ────── 37500]                    → meio=37500, resultado=R$1.1M → perto!
   ... até convergir

3. RETORNOS POR OBJETIVO:
   Cada objetivo tem uma rentabilidade esperada diferente porque sugere
   diferentes composições de carteira (conservador vs arrojado).
"""


# ─── Retornos anuais estimados por tipo de objetivo ─────────────────────
# POR QUE variam? Porque cada objetivo implica um perfil de risco diferente.
# "reserva" = conservador (renda fixa ~8%), "crescimento" = arrojado (mix ~11%)
RETORNOS_POR_OBJETIVO = {
    "aposentadoria": 0.09,   # 9% a.a. — mix moderado, longo prazo
    "imovel": 0.085,         # 8.5% a.a. — moderado-conservador, prazo definido
    "reserva": 0.08,         # 8% a.a. — conservador, prioriza segurança
    "crescimento": 0.11,     # 11% a.a. — arrojado, busca retorno máximo
}


def _simular_valor_futuro(
    patrimonio_atual: float,
    aporte_mensal: float,
    anos: int,
    retorno_anual: float,
) -> dict:
    """
    📌 Simula a evolução do patrimônio mês a mês usando juros compostos.

    POR QUE simular mês a mês em vez de usar a fórmula fechada?
    - Mais didático: você vê exatamente o que acontece cada mês
    - Mais flexível: fácil adicionar inflação, aportes variáveis, etc.
    - A fórmula fechada assume aporte constante (limitação)

    Retorna:
    - valor_final: patrimônio acumulado ao final
    - total_aportado: soma de todos os aportes + patrimonio inicial
    - rendimento: quanto os juros compostos geraram
    - evolucao_anual: lista com o valor ao final de cada ano (para gráficos)
    """
    taxa_mensal = (1 + retorno_anual) ** (1 / 12) - 1  # Conversão anual → mensal
    meses = anos * 12
    saldo = patrimonio_atual
    evolucao_anual = []

    for mes in range(1, meses + 1):
        saldo += aporte_mensal          # 1. Deposita o aporte
        saldo *= (1 + taxa_mensal)      # 2. Aplica rendimento do mês

        # Salva snapshot ao final de cada ano (para o gráfico)
        if mes % 12 == 0:
            evolucao_anual.append({
                "ano": mes // 12,
                "valor": round(saldo, 2),
            })

    total_aportado = patrimonio_atual + (aporte_mensal * meses)
    rendimento = saldo - total_aportado

    return {
        "valor_final": round(saldo, 2),
        "total_aportado": round(total_aportado, 2),
        "rendimento": round(rendimento, 2),
        "evolucao_anual": evolucao_anual,
    }


def calcular_aporte_necessario(
    valor_alvo: float,
    patrimonio_atual: float,
    anos: int,
    retorno_anual: float,
    tolerancia: float = 0.01,
    max_iteracoes: int = 100,
) -> float:
    """
    📌 BUSCA BINÁRIA — encontra o aporte mensal necessário para atingir o valor_alvo.

    COMO FUNCIONA:
    1. Define limites: mínimo=0, máximo=valor_alvo (ninguém aportaria mais que a meta)
    2. Testa o valor do MEIO
    3. Se o resultado ficou ABAIXO da meta → precisa aportar MAIS → ajusta mínimo
    4. Se o resultado ficou ACIMA da meta → pode aportar MENOS → ajusta máximo
    5. Repete até a diferença ser menor que a tolerância (1%)

    POR QUE busca binária e não fórmula direta?
    - A fórmula de anuidade existe, mas assume condições simplificadas
    - A busca binária funciona com QUALQUER modelo de simulação
    - Se no futuro adicionarmos inflação, taxas variáveis, etc., continua funcionando

    Complexidade: O(log(valor_alvo / tolerancia) * anos * 12)
    Na prática: ~50 iterações × 120 meses = ~6000 operações (instantâneo)
    """
    low = 0.0
    high = valor_alvo  # Limite superior conservador
    mid = (low + high) / 2  # Inicialização para evitar UnboundLocalError

    for _ in range(max_iteracoes):
        mid = (low + high) / 2  # 📌 Ponto médio — essência da busca binária
        resultado = _simular_valor_futuro(patrimonio_atual, mid, anos, retorno_anual)

        if abs(resultado["valor_final"] - valor_alvo) / valor_alvo < tolerancia:
            return round(mid, 2)  # Convergiu! Diferença < 1%

        if resultado["valor_final"] < valor_alvo:
            low = mid   # Precisa aportar MAIS → move limite inferior pra cima
        else:
            high = mid  # Pode aportar MENOS → move limite superior pra baixo

    return round(mid, 2)  # Retorna melhor aproximação


def calcular_prazo_necessario(
    valor_alvo: float,
    patrimonio_atual: float,
    aporte_mensal: float,
    retorno_anual: float,
    max_anos: int = 50,
) -> int:
    """
    📌 BUSCA LINEAR — encontra em quantos anos o patrimônio atinge o valor_alvo.

    POR QUE busca linear e não binária aqui?
    - O prazo é um número inteiro pequeno (1 a 50 anos)
    - Busca linear é O(50) no pior caso — já é instantâneo
    - Para int, não faz sentido buscar "meio" de 7.5 anos

    Retorna -1 se a meta for inalcançável em 50 anos (aporte muito baixo).
    """
    for anos in range(1, max_anos + 1):
        resultado = _simular_valor_futuro(
            patrimonio_atual, aporte_mensal, anos, retorno_anual
        )
        if resultado["valor_final"] >= valor_alvo:
            return anos

    return -1  # Meta inalcançável no prazo máximo


def calcular_meta(
    valor_alvo: float,
    patrimonio_atual: float,
    objetivo: str,
    aporte_mensal: float | None = None,
    prazo_desejado: int | None = None,
) -> dict:
    """
    📌 ORQUESTRADOR — função principal que decide O QUE calcular.

    Três cenários possíveis:

    1. Usuário informou PRAZO mas não o aporte:
       → Calcula o aporte necessário (busca binária)

    2. Usuário informou APORTE mas não o prazo:
       → Calcula em quantos anos atinge a meta (busca linear)

    3. Usuário informou AMBOS:
       → Simula e verifica se a meta é viável

    Retorna um dicionário completo com:
    - modo: qual cenário foi usado
    - aporte_mensal / prazo_anos: valores (calculados ou informados)
    - simulacao: resultado detalhado da projeção
    - meta_atingida: bool indicando se é viável
    - progresso_atual: % do patrimônio atual em relação à meta
    """
    retorno_anual = RETORNOS_POR_OBJETIVO.get(objetivo, 0.09)

    # Guard clause: se patrimônio já atingiu ou superou a meta
    if patrimonio_atual >= valor_alvo:
        progresso = round((patrimonio_atual / valor_alvo) * 100, 2)
        return {
            "modo": "meta_ja_atingida",
            "aporte_mensal": aporte_mensal or 0,
            "prazo_anos": 0,
            "retorno_anual_estimado": round(retorno_anual * 100, 2),
            "simulacao": {
                "valor_final": round(patrimonio_atual, 2),
                "total_aportado": round(patrimonio_atual, 2),
                "rendimento": 0.0,
                "evolucao_anual": [],
            },
            "meta_atingida": True,
            "progresso_atual": progresso,
            "valor_alvo": valor_alvo,
            "mensagem": (
                f"Parabéns! Seu patrimônio atual de R$ {patrimonio_atual:,.2f} "
                f"já atingiu a meta de R$ {valor_alvo:,.2f}."
            ),
        }

    progresso_atual = round((patrimonio_atual / valor_alvo) * 100, 2)

    # ─── Cenário 1: calcular APORTE necessário ─────────────────────
    if aporte_mensal is None and prazo_desejado is not None:
        aporte_calculado = calcular_aporte_necessario(
            valor_alvo, patrimonio_atual, prazo_desejado, retorno_anual
        )
        simulacao = _simular_valor_futuro(
            patrimonio_atual, aporte_calculado, prazo_desejado, retorno_anual
        )
        return {
            "modo": "calcular_aporte",
            "aporte_mensal": aporte_calculado,
            "prazo_anos": prazo_desejado,
            "retorno_anual_estimado": round(retorno_anual * 100, 2),
            "simulacao": simulacao,
            "meta_atingida": simulacao["valor_final"] >= valor_alvo * 0.99,
            "progresso_atual": progresso_atual,
            "valor_alvo": valor_alvo,
        }

    # ─── Cenário 2: calcular PRAZO necessário ──────────────────────
    if prazo_desejado is None and aporte_mensal is not None:
        prazo_calculado = calcular_prazo_necessario(
            valor_alvo, patrimonio_atual, aporte_mensal, retorno_anual
        )
        if prazo_calculado == -1:
            # Meta inalcançável com esse aporte
            simulacao = _simular_valor_futuro(
                patrimonio_atual, aporte_mensal, 50, retorno_anual
            )
            return {
                "modo": "calcular_prazo",
                "aporte_mensal": aporte_mensal,
                "prazo_anos": -1,
                "retorno_anual_estimado": round(retorno_anual * 100, 2),
                "simulacao": simulacao,
                "meta_atingida": False,
                "progresso_atual": progresso_atual,
                "valor_alvo": valor_alvo,
                "mensagem": (
                    f"Com aporte de R$ {aporte_mensal:.2f}/mês, a meta não é atingível em 50 anos. "
                    f"Considere aumentar o aporte ou reduzir o valor-alvo."
                ),
            }
        simulacao = _simular_valor_futuro(
            patrimonio_atual, aporte_mensal, prazo_calculado, retorno_anual
        )
        return {
            "modo": "calcular_prazo",
            "aporte_mensal": aporte_mensal,
            "prazo_anos": prazo_calculado,
            "retorno_anual_estimado": round(retorno_anual * 100, 2),
            "simulacao": simulacao,
            "meta_atingida": True,
            "progresso_atual": progresso_atual,
            "valor_alvo": valor_alvo,
        }

    # ─── Cenário 3: ambos informados → verificar viabilidade ──────
    # Se chegamos aqui, ambos os valores foram fornecidos (cenários 1 e 2 retornam antes)
    assert aporte_mensal is not None, "aporte_mensal deve estar definido no cenário 3"
    assert prazo_desejado is not None, "prazo_desejado deve estar definido no cenário 3"

    simulacao = _simular_valor_futuro(
        patrimonio_atual, aporte_mensal, prazo_desejado, retorno_anual
    )
    meta_atingida = simulacao["valor_final"] >= valor_alvo * 0.99
    diferenca = simulacao["valor_final"] - valor_alvo

    resultado = {
        "modo": "verificar_viabilidade",
        "aporte_mensal": aporte_mensal,
        "prazo_anos": prazo_desejado,
        "retorno_anual_estimado": round(retorno_anual * 100, 2),
        "simulacao": simulacao,
        "meta_atingida": meta_atingida,
        "progresso_atual": progresso_atual,
        "valor_alvo": valor_alvo,
    }

    if meta_atingida:
        resultado["mensagem"] = (
            f"Meta viável! Você atingirá R$ {simulacao['valor_final']:,.2f}, "
            f"superando a meta em R$ {diferenca:,.2f}."
        )
    else:
        # Calcula o aporte ideal como sugestão
        aporte_ideal = calcular_aporte_necessario(
            valor_alvo, patrimonio_atual, prazo_desejado, retorno_anual
        )
        resultado["mensagem"] = (
            f"Meta não atingída com os parâmetros atuais. "
            f"Valor projetado: R$ {simulacao['valor_final']:,.2f}. "
            f"Aporte sugerido: R$ {aporte_ideal:,.2f}/mês."
        )
        resultado["aporte_sugerido"] = aporte_ideal

    return resultado
