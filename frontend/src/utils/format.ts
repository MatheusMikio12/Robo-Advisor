/**
 * Funções utilitárias de formatação — reutilizáveis em todo o frontend.
 * Centraliza a lógica que antes estava duplicada em 4+ componentes.
 */

/** Formata um número como moeda brasileira (R$ 1.234,56) */
export const formatCurrency = (value: number): string =>
    new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
        minimumFractionDigits: 2,
    }).format(value);

/** Formata moeda de forma abreviada (R$ 1.2M, R$ 500K) — para eixos de gráficos */
export const formatCurrencyShort = (value: number): string => {
    if (value >= 1_000_000) return `R$ ${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `R$ ${(value / 1_000).toFixed(0)}K`;
    return `R$ ${value.toFixed(0)}`;
};

/** Formata um número como percentual (ex: 12.34%) */
export const formatPercent = (value: number): string => `${value.toFixed(2)}%`;
