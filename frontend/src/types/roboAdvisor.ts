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
