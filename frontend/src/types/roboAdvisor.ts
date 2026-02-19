export interface InvestorFormData {
  idade: number;
  renda_mensal: number;
  patrimonio_atual: number;
  aporte_mensal: number;
  prazo_anos: number;
  objetivo: 'aposentadoria' | 'imovel' | 'reserva' | 'crescimento';
}

export interface CarteiraItem {
  ativo: string;
  percentual: number;
  descricao?: string;
}

export interface EvolucaoPatrimonio {
  ano: number;
  valor: number;
}

export interface PlanejamentoResponse {
  perfil: string;
  carteira: CarteiraItem[];
  resumo: {
    valor_final: number;
    total_investido: number;
    retorno_absoluto: number;
    retorno_percentual: number;
    cagr: number;
  };
  evolucao: EvolucaoPatrimonio[];
}

// ─── METAS FINANCEIRAS ──────────────────────────────────────────────
// Espelham o modelo MetaFinanceiraInput do backend (models/meta.py)

export interface MetaFinanceiraInput {
  valor_alvo: number;
  patrimonio_atual: number;
  aporte_mensal?: number;        // Opcional — será calculado se não informado
  prazo_desejado?: number;       // Opcional — será calculado se não informado
  objetivo: 'aposentadoria' | 'imovel' | 'reserva' | 'crescimento';
}

// Resposta do endpoint POST /meta (services/planejador.py -> calcular_meta)
export interface MetaFinanceiraResponse {
  modo: 'calcular_aporte' | 'calcular_prazo' | 'verificar_viabilidade' | 'meta_ja_atingida';
  aporte_mensal: number;
  prazo_anos: number;
  retorno_anual_estimado: number;
  simulacao: {
    valor_final: number;
    total_aportado: number;
    rendimento: number;
    evolucao_anual: EvolucaoPatrimonio[];
  };
  meta_atingida: boolean;
  progresso_atual: number;
  valor_alvo: number;
  mensagem?: string;
  aporte_sugerido?: number;
}
