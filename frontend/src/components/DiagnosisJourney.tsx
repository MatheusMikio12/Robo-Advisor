import { useEffect, useState } from "react";
import { Diagnosis } from "@/types/wealth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Field = { key: keyof Diagnosis; label: string; hint: string; min?: number; max?: number; choices?: [string, string][] };
const fields: Field[] = [
  { key: "goal", label: "O que você gostaria de conquistar primeiro?", hint: "Depois podemos acrescentar outros objetivos.", choices: [["reserva", "Criar uma reserva"], ["imovel", "Comprar um imóvel"], ["aposentadoria", "Planejar a aposentadoria"], ["crescimento", "Construir patrimônio"], ["educacao", "Educação"], ["viagem", "Viajar"]] },
  { key: "age", label: "Qual é a sua idade?", hint: "Você poderá revisar todo o contexto antes de salvar.", min: 18, max: 100 },
  { key: "income", label: "Quanto você recebe por mês?", hint: "Informe a renda líquida média, em reais.", min: 0 },
  { key: "expenses", label: "Quanto custa sua rotina mensal?", hint: "Inclua despesas essenciais e parcelas de dívidas, em reais.", min: 0 },
  { key: "assets", label: "Quanto você tem em recursos financeiros?", hint: "Inclua investimentos e reserva, mas não imóveis ou veículos.", min: 0 },
  { key: "reserve", label: "Desse valor, quanto está reservado para emergências?", hint: "É uma parte do patrimônio que você acabou de informar, em reais.", min: 0 },
  { key: "debt", label: "Qual é o saldo total das suas dívidas?", hint: "Informe zero se não tiver dívidas, em reais.", min: 0 },
  { key: "debt_rate", label: "Qual é o custo anual da dívida mais cara?", hint: "Use o CET anual em %. Consulte seu contrato se não souber; não estime para baixo.", min: 0, max: 1000 },
  { key: "contribution", label: "Quanto pretende investir por mês?", hint: "Vamos conferir se o aporte cabe na sobra mensal.", min: 0 },
  { key: "horizon", label: "Em quantos anos pretende usar esse dinheiro?", hint: "O prazo orienta a exposição a oscilações.", min: 1, max: 50 },
  { key: "liquidity_months", label: "Em quantos meses pode precisar resgatar?", hint: "Considere a primeira necessidade possível. Zero significa necessidade imediata.", min: 0, max: 600 },
  { key: "stability", label: "Como é a previsibilidade da sua renda?", hint: "Uma renda variável pede uma reserva maior.", choices: [["estavel", "Estável"], ["variavel", "Varia entre os meses"], ["incerta", "Incerta no momento"]] },
  { key: "experience", label: "Como você avalia sua experiência?", hint: "Isso limita o risco e a complexidade da carteira inicial.", choices: [["nenhuma", "Estou começando"], ["basica", "Conheço o básico"], ["avancada", "Conheço riscos e produtos"]] },
  { key: "loss_tolerance", label: "Como reagiria a uma queda relevante no investimento?", hint: "Sua disposição para perdas será combinada com sua capacidade financeira.", choices: [["nenhuma", "Não posso aceitar perdas"], ["baixa", "Precisaria reduzir o risco"], ["media", "Manteria parte do plano"], ["alta", "Manteria o plano, mesmo com quedas fortes"]] },
  { key: "currency", label: "Em qual moeda será seu objetivo?", hint: "A seleção inicial de produtos atende objetivos em reais. Outras moedas exigem cobertura específica.", choices: [["BRL", "Real"], ["USD", "Dólar"], ["EUR", "Euro"]] },
];
const defaults: Diagnosis = {age: 30, income: 0, expenses: 0, assets: 0, reserve: 0, debt: 0, debt_rate: 0, contribution: 0, horizon: 5,
  goal: "reserva", stability: "estavel", experience: "nenhuma", loss_tolerance: "nenhuma", liquidity_months: 12,
  currency: "BRL", institutions: [], excluded_classes: [], max_issuer_pct: 25};

export default function DiagnosisJourney({ initial, onSave, busy, draft, onDraft }: {initial: Diagnosis | null; onSave: (data: Diagnosis) => Promise<void>; busy: boolean; draft: {answers:Diagnosis;step:number} | null; onDraft:(data:Diagnosis,step:number)=>Promise<void>}) {
  const [data, setData] = useState<Diagnosis>(initial ?? defaults);
  const [step, setStep] = useState(initial ? fields.length : 0);
  const field = fields[step];
  const [draftError,setDraftError] = useState("");
  const [ready,setReady] = useState(false);
  useEffect(() => {if(!ready) {if(draft) {setData(draft.answers);setStep(draft.step);} setReady(true);}},[draft,ready]);
  const advance = async (next: Diagnosis) => {const skipDebt = field?.key === "debt" && next.debt === 0; const nextStep = step + (skipDebt ? 2 : 1); const answers = skipDebt ? {...next,debt_rate:0} : next; setData(answers);setDraftError(""); try {await onDraft(answers,nextStep);setStep(nextStep);} catch(error) {setDraftError(error instanceof Error ? error.message : "Não foi possível salvar a resposta.");}};
  const set = (key: keyof Diagnosis, value: string | number | string[]) => setData(current => ({...current, [key]: value}));
  return <section className="wealth-panel" aria-labelledby="diagnosis-heading">
    <div className="wealth-section-heading"><h2 id="diagnosis-heading">Seu diagnóstico</h2><span>{Math.min(step, fields.length)} de {fields.length}</span></div>
    <progress className="w-full h-1" value={step} max={fields.length} aria-label="Progresso do diagnóstico" />
    <p className="text-sm text-muted-foreground mt-3">Este contexto é necessário para avaliar investimentos. Para começar apenas um objetivo, você pode usar a Conversa ou Meu plano e voltar aqui depois.</p>
    <form className="space-y-5 mt-6" onSubmit={async e => {e.preventDefault(); if (step < fields.length) await advance(data); else await onSave(data);}}>
      {draftError && <p role="alert" className="text-destructive">{draftError}</p>}
      {field ? <>
        <label className="block text-xl font-semibold" htmlFor="diagnosis-answer">{field.label}</label><p className="text-muted-foreground">{field.hint}</p>
        {field.choices ? <div className="grid gap-2 sm:grid-cols-2">{field.choices.map(([value, label]) => <button disabled={busy} className="wealth-choice" aria-pressed={data[field.key] === value} key={value} type="button" onClick={() => void advance({...data,[field.key]:value})}>{label}</button>)}</div>
          : <Input key={field.key} id="diagnosis-answer" type="number" min={field.min} max={field.key === "reserve" ? data.assets : field.max ?? 1e12} step={["age", "horizon", "liquidity_months"].includes(field.key) ? 1 : .01} required value={String(data[field.key])} onChange={e => set(field.key, Number(e.target.value))} />}
        {!field.choices && <Button disabled={busy} type="submit">Continuar</Button>}
      </> : <>
        <p>Revise suas respostas. Elas serão salvas na sua conta e orientarão as próximas conversas.</p>
        <dl className="wealth-review">{fields.map((f, i) => <div key={f.key}><dt>{f.label}</dt><dd><button type="button" onClick={() => setStep(i)} title="Editar resposta">{f.choices?.find(([v]) => v === data[f.key])?.[1] ?? String(data[f.key])} <span className="text-primary text-xs">Editar</span></button></dd></div>)}</dl>
        <label className="block">Bancos e corretoras <Input value={data.institutions.join(", ")} onChange={e => set("institutions", e.target.value.split(",").map(x => x.trim()).filter(Boolean))} placeholder="Separe por vírgula" /></label>
        <fieldset><legend>Classes que prefere excluir</legend><div className="flex flex-wrap gap-3 mt-2">{[["brasil", "Ações Brasil"], ["global", "Ações globais"], ["imobiliario", "FIIs"], ["inflacao", "Inflação"]].map(([key, label]) => <label key={key} className="flex gap-2"><input type="checkbox" checked={data.excluded_classes.includes(key)} onChange={e => set("excluded_classes", e.target.checked ? [...data.excluded_classes, key] : data.excluded_classes.filter(x => x !== key))} />{label}</label>)}</div></fieldset>
        <label className="block">Limite por emissor privado (%)<Input type="number" min={5} max={100} value={data.max_issuer_pct} onChange={e => set("max_issuer_pct", Number(e.target.value))} /></label>
        <Button type="submit" disabled={busy}>{busy ? "Salvando…" : "Salvar diagnóstico"}</Button>
      </>}
      {step > 0 && <Button type="button" variant="ghost" disabled={busy} onClick={() => setStep(step - 1)}>Voltar</Button>}
    </form>
  </section>;
}
