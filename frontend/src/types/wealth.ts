export type Diagnosis = {
  age: number; income: number; expenses: number; assets: number; reserve: number; debt: number;
  debt_rate: number; contribution: number; horizon: number; goal: string; stability: string;
  experience: string; loss_tolerance: string; liquidity_months: number; currency: string;
  institutions: string[]; excluded_classes: string[]; max_issuer_pct: number;
};
export type Policy = {
  version: string; profile: string; reserve_months: number; reserve_target: number; reserve_gap: number;
  monthly_surplus: number; contribution: number; savings_rate: number | null; investable: number;
  reasons: string[]; assumptions: string[]; selection_blocked: boolean;
};
export type Product = {
  id: string; name: string; issuer: string; asset_class: string; source: string; as_of: string;
  quote_type: string; price?: number; rate_pct?: number; indexer?: string; minimum?: number;
  liquidity_days?: number; fee_pct?: number; maturity?: string; risks?: string; tax?: string; cost_note?: string;
};
export type Recommendation = {
  id: string; policy: Policy; profile_revision: number; generated_at: string; method: string;
  allocation: { key: string; name: string; percent: number; unallocated_percent: number; message: string;
    products: { product: Product; percent: number; amount: number; why: string; alternatives: {id: string; name: string; score: number}[] }[] }[];
  excluded: {id: string; name: string; reasons: string[]}[];
  drift: {name: string; actual: number; target: number; delta: number; review: boolean}[];
};
export type Goal = { id?: string; name: string; target: number; current: number; contribution: number; years: number; priority: string; currency: string };
export type Holding = { id?: string; name: string; institution: string; issuer: string; asset_class: string; value: number; currency: string };
export type ChatMessage = {id: string; user_text: string; text: string; agent: string; provider?: string; explanation?: string; proposal?: Goal; monthly_reference?: number};
export type WealthState = {
  recommendation_stale: boolean;
  planning_warnings: string[];
  profile: Diagnosis | null; revision: number; policy: Policy | null; goals: Goal[]; holdings: Holding[];
  conversations: {id: string; title: string}[]; recommendation: Recommendation | null;
  transactions: {id: string; date: string; description: string; amount: number; account: string}[]; cashflow: Record<string, number>;
};
export type SimulationInput = {initial: number; contribution: number; years: number; target: number; annual_return: number; volatility: number;
  inflation: number; fees: number; tax: number; pause_start: number; pause_months: number; withdrawal_start: number; monthly_withdrawal: number;
  shock_month: number; shock_amount: number};
export type SimulationResult = {series: {year: number; p10: number; p50: number; p90: number}[]; success_probability: number | null;
  depletion_probability: number; units: string; limitations: string[]; assumptions: SimulationInput};
