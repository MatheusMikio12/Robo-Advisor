import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Goal, SimulationInput, SimulationResult } from "@/types/wealth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatCurrency } from "@/utils/format";

export default function WealthScenarios({ goals, save, run, contribute, busy }: {
  goals: Goal[]; save: (goal: Goal) => Promise<void>; run: (data: SimulationInput) => Promise<SimulationResult>;
  contribute: (id: string, amount: number) => Promise<void>; busy: boolean;
}) {
  const [goal, setGoal] = useState<Goal>({name: "", target: 100000, current: 0, contribution: 500, years: 10, priority: "media", currency: "BRL"});
  const [input, setInput] = useState<SimulationInput>({initial: 0, contribution: 500, years: 10, target: 100000, annual_return: 6, volatility: 10, inflation: 4, fees: .5, tax: 15, pause_start: 0, pause_months: 0, withdrawal_start: 0, monthly_withdrawal: 0, shock_month: 0, shock_amount: 0});
  const [results, setResults] = useState<SimulationResult[]>([]);
  const [amount, setAmount] = useState<Record<string, number>>({});
  const [simError, setSimError] = useState("");
  const calculate = async (next: SimulationInput) => {setSimError(""); try {const result = await run(next);setInput(next);setResults(previous => [...previous.slice(-1),result]);} catch(error) {setSimError(error instanceof Error ? error.message : "Não foi possível simular.");}};
  const basicKeys: (keyof SimulationInput)[] = ["target", "initial", "contribution", "years"];
  const inputField = (key: keyof SimulationInput) => <label key={key} className="text-sm">{labels[key]}<Input required type="number" step={["years", "pause_start", "pause_months", "withdrawal_start", "shock_month"].includes(key) ? 1 : .01} min={key === "annual_return" ? -50 : key === "years" ? 1 : 0} max={key === "years" ? 50 : undefined} value={input[key]} onChange={e => setInput({...input,[key]:Number(e.target.value)})}/></label>;
  const labels: Record<keyof SimulationInput, string> = {initial: "Valor inicial (R$)", contribution: "Aporte mensal (R$)", years: "Prazo (anos)", target: "Meta em reais de hoje", annual_return: "Retorno nominal esperado (% a.a.)", volatility: "Volatilidade (% a.a.)", inflation: "Inflação (% a.a.)", fees: "Custos (% a.a.)", tax: "Imposto estimado sobre ganhos (%)", pause_start: "Mês inicial da pausa (0 desliga)", pause_months: "Meses sem aporte", withdrawal_start: "Mês inicial das retiradas (0 desliga)", monthly_withdrawal: "Retirada mensal em reais de hoje", shock_month: "Mês do imprevisto (0 desliga)", shock_amount: "Custo do imprevisto em reais de hoje"};
  return <div className="space-y-6">
    <section className="wealth-panel"><h2 className="text-2xl font-semibold">Seus objetivos, acompanhados</h2><p className="text-muted-foreground mt-2">As metas compartilham sua capacidade de aporte. Evite comprometer o mesmo dinheiro em mais de uma.</p>
      <div className="divide-y mt-5">{goals.map(g => <div className="py-4" key={g.id}><div className="flex justify-between gap-3"><h3 className="font-semibold">{g.name}</h3><span>{g.priority === "alta" ? "Prioridade alta" : g.priority === "media" ? "Prioridade média" : "Prioridade baixa"}</span></div>
        <p className="my-2">{new Intl.NumberFormat("pt-BR", {style: "currency", currency: g.currency}).format(g.current)} de {new Intl.NumberFormat("pt-BR", {style: "currency", currency: g.currency}).format(g.target)} · {g.years} anos</p>
        <progress className="w-full h-2" max={g.target} value={Math.min(g.current, g.target)} aria-label={`Progresso de ${g.name}`} />
        <div className="flex flex-wrap items-end gap-2 mt-3"><Button variant="outline" onClick={() => setGoal({name:g.name, target:g.target,current:g.current,contribution:g.contribution,years:g.years,priority:g.priority,currency:g.currency,id:g.id})}>Editar meta</Button>
          <Button variant="outline" disabled={g.currency !== "BRL"} onClick={() => setInput(current => ({...current, initial: g.current, contribution: g.contribution, years: g.years, target: g.target}))}>Usar no cenário</Button>
          <label className="text-sm">Aporte realizado ({g.currency})<Input aria-label={`Aporte para ${g.name}`} type="number" min={.01} step={.01} className="w-36" value={amount[g.id!] ?? ""} onChange={e => setAmount({...amount, [g.id!]: Number(e.target.value)})} /></label>
          <Button disabled={busy || !(amount[g.id!] > 0)} onClick={() => void contribute(g.id!, amount[g.id!])}>Registrar aporte</Button></div></div>)}</div>
      <details open={!!goal.id} className="mt-6 border-t pt-4"><summary className="cursor-pointer font-semibold">{goal.id ? "Editar objetivo" : "Adicionar objetivo"}</summary><p className="text-sm text-muted-foreground mt-2">Você também pode criar um objetivo pela Conversa, uma pergunta por vez.</p><form className="grid gap-4 sm:grid-cols-2 mt-4" onSubmit={async e => {e.preventDefault(); await save(goal);}}>
        <label>Nome<Input required maxLength={120} value={goal.name} onChange={e => setGoal({...goal, name:e.target.value})}/></label>
        {([["target", "Valor desejado"], ["current", "Valor já reservado"], ["contribution", "Aporte mensal"], ["years", "Prazo em anos"]] as const).map(([key,label]) => <label key={key}>{label}<Input required type="number" min={key === "years" || key === "target" ? 1 : 0} max={key === "years" ? 50 : 1e12} step={key === "years" ? 1 : .01} value={goal[key]} onChange={e => setGoal({...goal,[key]:Number(e.target.value)})}/></label>)}
        <label>Prioridade<select className="wealth-select" value={goal.priority} onChange={e => setGoal({...goal,priority:e.target.value})}><option value="alta">Alta</option><option value="media">Média</option><option value="baixa">Baixa</option></select></label>
        <label>Moeda<select className="wealth-select" value={goal.currency} onChange={e => setGoal({...goal,currency:e.target.value})}><option>BRL</option><option>USD</option><option>EUR</option></select></label>
        <div className="flex gap-2 items-end"><Button disabled={busy} type="submit">Salvar meta</Button>{goal.id && <Button type="button" variant="ghost" onClick={() => setGoal({...goal,id:undefined,name:""})}>Nova meta</Button>}</div>
      </form></details>
    </section>
    <section className="wealth-panel"><h2 className="text-2xl font-semibold">Quanto guardar para chegar lá?</h2><p className="mt-2 text-muted-foreground">Comece pelo valor e pelo prazo. Depois compare o efeito de guardar mais ou esperar um pouco. Os resultados consideram o poder de compra de hoje e não são garantias.</p>
      {!!goals.length && <p className="text-sm mt-3">Para usar os valores de um objetivo salvo, selecione “Usar no cenário” no objetivo acima. Alterar um cenário não modifica suas metas.</p>}
      <form className="mt-5" onSubmit={async e => {e.preventDefault(); setSimError(""); try {const r = await run(input); setResults(previous => [...previous.slice(-1), r]);} catch(error) {setSimError(error instanceof Error ? error.message : "Não foi possível simular.");}}}>
        <div className="grid gap-4 sm:grid-cols-2">{basicKeys.map(inputField)}</div>
        <details className="mt-5 border-t pt-4"><summary className="cursor-pointer font-medium">Como calculamos · ajustes avançados</summary><p className="text-sm text-muted-foreground my-3">Hipóteses ilustrativas, não taxas atuais nem previsão: retorno de {input.annual_return}% ao ano, inflação de {input.inflation}%, custos de {input.fees}% e imposto aproximado de {input.tax}% sobre ganhos. A oscilação assumida é de {input.volatility}% ao ano.</p><div className="grid gap-4 sm:grid-cols-2">{(Object.keys(labels) as (keyof SimulationInput)[]).filter(key => !basicKeys.includes(key)).map(inputField)}</div></details>
        <Button className="mt-4" disabled={busy} type="submit">Calcular cenário</Button>
        {!!results.length && <div className="flex flex-wrap gap-2 mt-3"><Button type="button" variant="outline" disabled={busy || input.contribution > 999999900} onClick={() => void calculate({...input,contribution:input.contribution+100})}>E se eu guardar mais R$ 100 por mês?</Button><Button type="button" variant="outline" disabled={busy || input.years >= 50} onClick={() => void calculate({...input,years:input.years+1})}>E se eu esperar mais um ano?</Button></div>}
      </form>
      {simError && <p role="alert" className="text-destructive mt-3">{simError}</p>}
      <div className="grid gap-5 mt-6 lg:grid-cols-2">{results.map((result,index) => <div key={index} className="border-t pt-4 min-w-0"><h3 className="font-semibold">Cenário {index + 1}</h3><p className="text-sm">{result.assumptions.years} anos · aporte {formatCurrency(result.assumptions.contribution)} · retorno {result.assumptions.annual_return}% · inflação {result.assumptions.inflation}%</p>
        <p className="mt-3 text-lg">Valor central projetado: <strong>{formatCurrency(result.series.at(-1)?.p50 ?? 0)}</strong></p><p className="text-sm">Em poder de compra de hoje. O resultado real pode ser menor ou maior.</p>
        <p className="mt-3">Chance estimada de atingir a meta: <strong>{result.success_probability === null ? "Meta não informada" : `${result.success_probability}%`}</strong></p>{result.assumptions.monthly_withdrawal > 0 && <p className="text-sm">Risco estimado de insuficiência nas retiradas: {result.depletion_probability}%</p>}
        <div className="h-64 mt-4"><ResponsiveContainer width="100%" height="100%"><LineChart data={result.series}><XAxis dataKey="year"/><YAxis width={65} tickFormatter={v => `${Math.round(v/1000)} mil`}/><Tooltip formatter={(v: number) => formatCurrency(v)}/><Legend/><Line dataKey="p10" name="Pessimista (P10)" stroke="#65758B" dot={false}/><Line dataKey="p50" name="Mediano (P50)" stroke="#3855EF" dot={false}/><Line dataKey="p90" name="Otimista (P90)" stroke="#137B76" dot={false}/></LineChart></ResponsiveContainer></div>
        <details><summary className="cursor-pointer">Premissas e limites</summary><ul className="list-disc pl-5 text-sm mt-2">{result.limitations.map(x => <li key={x}>{x}</li>)}</ul></details>
      </div>)}</div>
    </section>
  </div>;
}
