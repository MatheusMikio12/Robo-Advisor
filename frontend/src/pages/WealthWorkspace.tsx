import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import Header from "@/components/Header";
import DiagnosisJourney from "@/components/DiagnosisJourney";
import WealthPortfolio from "@/components/WealthPortfolio";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { API_URL } from "@/config";
import { apiFetch, authHeaders } from "@/utils/api";
import { formatCurrency } from "@/utils/format";
import { ChatMessage, Diagnosis, Goal, Holding, Product, SimulationResult, WealthState } from "@/types/wealth";

const WealthScenarios = lazy(() => import("@/components/WealthScenarios"));
const AccountSecurity = lazy(() => import("@/components/AccountSecurity"));
const tabs = ["Conversa", "Diagnóstico", "Carteira", "Meu plano", "Minha vida financeira", "Conta"];
type Preview = {rows: {date: string; description: string; amount: number}[]; new_count: number; duplicates: number; confirmed: boolean};

export default function WealthWorkspace() {
  const { token } = useAuth();
  const [state, setState] = useState<WealthState | null>(null);
  const [tab, setTab] = useState("Conversa");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [draft,setDraft] = useState<{answers:Diagnosis;step:number} | null>(null);
  const [draftLoaded,setDraftLoaded] = useState(false);
  const [conversationId, setConversationId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  const [catalog, setCatalog] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [history, setHistory] = useState<{id: string; generated_at: string; profile_revision: number}[]>([]);
  const [holding, setHolding] = useState<Holding>({name:"",institution:"",issuer:"",asset_class:"liquidez",value:0,currency:"BRL"});
  const [statement, setStatement] = useState({account:"",format:"csv",content:""});
  const [preview, setPreview] = useState<Preview | null>(null);
  const request = useCallback(<T,>(path: string, method = "GET", body?: unknown) => apiFetch<T>(`${API_URL}/wealth${path}`, {method, headers:authHeaders(token), ...(body === undefined ? {} : {body:JSON.stringify(body)})}, 65000), [token]);
  const refresh = useCallback(async () => {const next = await request<WealthState>("/state"); setState(next); return next;}, [request]);
  useEffect(() => {let active=true; request<{answers:Diagnosis;step:number}|null>("/draft").then(d => {if(active) {setDraft(d);setDraftLoaded(true);}}).catch(e => {if(active) setError(e.message);});return () => {active=false;};},[request]);
  useEffect(() => {let active = true; request<WealthState>("/state").then(next => {if(active) {setState(next); setConversationId(next.conversations.at(-1)?.id ?? "");}}).catch(e => {if(active) setError(e.message);}); return () => {active = false;};}, [request]);
  useEffect(() => {let active = true; setMessages([]); if(conversationId) request<ChatMessage[]>(`/conversations/${conversationId}/messages`).then(rows => {if(active) setMessages(current => [...rows,...current.filter(x => !rows.some(row => row.id === x.id))]);}).catch(e => {if(active) setError(e.message);}); return () => {active = false;};}, [conversationId, request]);
  const act = async (work: () => Promise<void>) => {setBusy(true); setError(""); setNotice(""); try {await work();} catch(e) {setError(e instanceof Error ? e.message : "Não foi possível concluir. Tente novamente.");} finally {setBusy(false);}};
  const send = (value: string) => act(async () => {
    let id = conversationId;
    if(!id) {const created = await request<{id:string}>("/conversations", "POST"); id = created.id; setConversationId(id);}
    const answer = await request<ChatMessage>(`/conversations/${id}/messages`, "POST", {text:value,request_id:crypto.randomUUID()});
    setMessages(current => [...current.filter(x => x.id !== answer.id), answer]); setText(current => current.trim() === value.trim() ? "" : current); await refresh();
  });
  const saveGoal = (goal: Goal) => act(async () => {const {id,...body} = goal; await request(id ? `/goals/${id}` : "/goals", id ? "PUT" : "POST", body); await refresh(); setNotice("Meta salva.");});
  const saveProfile = (profile: Diagnosis) => act(async () => {await request("/profile", "PUT", profile); await refresh(); setTab("Carteira"); setNotice("Diagnóstico salvo. Gere sua carteira para aplicar o novo contexto.");});
  const showCatalog = () => act(async () => {const data = await request<{products:Product[]}>(`/products?q=${encodeURIComponent(search)}`); setCatalog(data.products); if(!data.products.length) setNotice("Nenhum produto encontrado. Sincronize uma fonte pública ou altere a busca.");});
  const changeStatement = (next: typeof statement) => {setStatement(next); setPreview(null);};

  return <div className="min-h-screen bg-background"><Header/><main className="wealth-workspace">
    <div className="wealth-welcome"><h1>Seu dinheiro, com contexto.</h1><p>Um plano que acompanha sua vida, uma conversa de cada vez.</p></div>
    <nav className="wealth-tabs" aria-label="Áreas do Prisma">{tabs.map(name => <button key={name} aria-current={tab === name ? "page" : undefined} onClick={() => {setTab(name);setNotice("");setError("");}}>{name}</button>)}</nav>
    {error && <div className="wealth-notice border-destructive text-destructive" role="alert">{error}<Button variant="ghost" onClick={() => void act(async () => {await refresh();})}>Tentar novamente</Button></div>}
    {notice && <p className="wealth-notice" role="status">{notice}</p>}
    {!state ? <p role="status" className="py-10">Carregando seu contexto…</p> : <>
      {tab === "Meu plano" && state.planning_warnings?.map(warning => <p role="status" className="wealth-notice" key={warning}>{warning}</p>)}
      {tab === "Conversa" && <div className="wealth-conversation-layout"><section className="wealth-panel">
        <div className="wealth-section-heading"><h2 className="text-xl font-semibold">Converse com o Prisma</h2><Button variant="ghost" disabled={busy} onClick={() => void act(async () => {const c = await request<{id:string}>("/conversations","POST"); setConversationId(c.id); await refresh();})}>Nova conversa</Button></div>
        {!!state.conversations.length && <label className="block text-sm mt-3">Histórico<select className="wealth-select" value={conversationId} onChange={e => setConversationId(e.target.value)}>{state.conversations.map((c,i) => <option key={c.id} value={c.id}>Conversa {i+1}</option>)}</select></label>}
        <div className="wealth-messages" aria-live="polite">
          <p className="wealth-reply">{state.profile ? "Podemos revisar sua reserva, criar um objetivo ou entender a carteira. O que gostaria de resolver primeiro?" : "O que você gostaria de resolver primeiro com seu dinheiro? Podemos começar por um objetivo, sem preencher todo o diagnóstico."}</p>
          {messages.map(message => <div className="space-y-3" key={message.id}><p className="wealth-user-message">{message.user_text}</p><div className="wealth-reply"><p>{message.text}</p>
            {message.explanation && <details className="mt-3"><summary>Explicação com IA local</summary><p className="mt-2">{message.explanation}</p><p className="text-xs mt-2">Texto gerado pode conter imprecisões. Os dados verificados estão acima.</p></details>}
            <p className="text-xs text-muted-foreground mt-3">{message.provider === "ollama" ? "Cálculos estruturados · explicação por IA local" : message.provider === "fallback" ? "Resposta estruturada · a IA não retornou uma explicação utilizável" : "Atendimento guiado · sem geração de IA nesta resposta"}</p>
            {message.proposal && <div className="border-t mt-4 pt-4 space-y-2"><h3 className="font-semibold">Proposta: {message.proposal.name}</h3><p>{formatCurrency(message.proposal.current)} guardados de {formatCurrency(message.proposal.target)} · {message.proposal.years} anos</p><p>Você pretende guardar {formatCurrency(message.proposal.contribution)} por mês.</p><p>Referência sem rendimento e sem inflação: {formatCurrency(message.monthly_reference ?? 0)} por mês.</p><Button disabled={busy} onClick={() => void act(async () => {await request(`/messages/${message.id}/confirm-goal`,"POST"); await refresh();setNotice("Objetivo confirmado. Você pode acompanhá-lo em Meu plano.");})}>Confirmar objetivo</Button></div>}
          </div></div>)}
        </div>
        <div className="flex gap-2 flex-wrap mb-4">{["Criar um objetivo", "Como está minha reserva?", "Explique minha carteira"].map(q => <Button key={q} variant="outline" size="sm" disabled={busy} onClick={() => void send(q)}>{q}</Button>)}</div>
        <form className="flex gap-2" onSubmit={e => {e.preventDefault(); if(text.trim()) void send(text.trim());}}><Input required maxLength={3000} aria-label="Mensagem para o Prisma" placeholder="O que você gostaria de entender?" value={text} onChange={e => setText(e.target.value)}/><Button disabled={busy || !text.trim()} type="submit">{busy ? "Pensando…" : "Enviar"}</Button></form>
      </section><aside className="wealth-context"><h2>Seu contexto</h2>{state.policy ? <><dl><div><dt>Reserva-alvo</dt><dd>{formatCurrency(state.policy.reserve_target)}</dd></div><div><dt>Falta para a reserva</dt><dd>{formatCurrency(state.policy.reserve_gap)}</dd></div><div><dt>Sobra mensal</dt><dd>{formatCurrency(state.policy.monthly_surplus)}</dd></div><div><dt>Aporte sustentável</dt><dd>{formatCurrency(state.policy.contribution)}</dd></div><div><dt>Limite de risco</dt><dd>{state.policy.profile}</dd></div></dl><Button variant="outline" onClick={() => setTab("Diagnóstico")}>Editar diagnóstico</Button></> : <><p>Ainda precisamos conhecer sua renda, despesas, objetivos e relação com o risco.</p><Button onClick={() => setTab("Diagnóstico")}>Começar diagnóstico</Button></>}</aside></div>}
      {tab === "Diagnóstico" && (draftLoaded ? <DiagnosisJourney initial={state.profile} draft={draft} onDraft={async (answers,step) => {setBusy(true);try {const d=await request<{answers:Diagnosis;step:number}>("/draft","PUT",{answers,step});setDraft(d);} finally {setBusy(false);}}} onSave={async profile => {await saveProfile(profile);setDraft(null);}} busy={busy}/> : <p>Recuperando suas respostas…</p>)}
      {tab === "Carteira" && <div className="space-y-5"><div className="flex gap-3 flex-wrap"><Button disabled={busy || !state.profile} onClick={() => void act(async () => {await request("/recommendations","POST"); await refresh();})}>Gerar minha carteira</Button><Button variant="outline" disabled={busy} onClick={() => void act(async () => {setHistory(await request("/recommendations"));})}>Histórico de análises</Button></div>
        {!state.profile && <p>Complete seu diagnóstico antes de gerar uma carteira. <button className="text-primary underline" onClick={() => setTab("Diagnóstico")}>Começar</button></p>}
        {!!history.length && <details open className="wealth-panel"><summary>Histórico preservado</summary>{history.map(x => <p key={x.id} className="mt-2">{new Date(x.generated_at).toLocaleString("pt-BR")} · revisão {x.profile_revision}</p>)}</details>}
        {state.recommendation && <WealthPortfolio plan={state.recommendation} stale={state.recommendation_stale}/>}
        <section className="wealth-panel"><h2 className="text-xl font-semibold">Produtos e fontes</h2><p className="mt-2 text-muted-foreground">Dados públicos de referência. Confira preço, custos e disponibilidade na instituição antes de investir.</p>
          <div className="flex flex-wrap gap-2 mt-4">{(["tesouro","cvm"] as const).map(source => <Button key={source} variant="outline" disabled={busy} onClick={() => void act(async () => {const result = await request<{count:number}>(`/products/sync/${source}`,"POST"); setNotice(`${result.count} produtos atualizados. Gere uma nova carteira para usar esses dados.`); const c = await request<{products:Product[]}>("/products"); setCatalog(c.products);})}>Sincronizar {source === "tesouro" ? "Tesouro" : "CVM"}</Button>)}</div>
          <form className="flex gap-2 mt-4" onSubmit={e => {e.preventDefault(); void showCatalog();}}><Input aria-label="Buscar produto" placeholder="Nome do produto" value={search} onChange={e => setSearch(e.target.value)}/><Button variant="outline" disabled={busy}>Buscar</Button></form>
          <div className="divide-y mt-4 max-h-80 overflow-y-auto">{catalog.map(p => <div key={p.id} className="py-3"><a className="font-medium text-primary" href={p.source} target="_blank" rel="noreferrer">{p.name}</a><p className="text-sm text-muted-foreground">{p.as_of} · {p.quote_type}</p></div>)}</div>
        </section>
      </div>}
      {tab === "Meu plano" && <Suspense fallback={<p>Carregando seu plano…</p>}><WealthScenarios goals={state.goals} save={saveGoal} busy={busy} run={async input => {setBusy(true); try{return await request<SimulationResult>("/simulate","POST",input);} finally {setBusy(false);}}} contribute={(id,amount) => act(async () => {await request(`/goals/${id}/contributions`,"POST",{amount,date:new Date().toISOString().slice(0,10),request_id:crypto.randomUUID()}); await refresh(); setNotice("Aporte registrado.");})}/></Suspense>}
      {tab === "Minha vida financeira" && <div className="space-y-6"><section className="wealth-panel"><h2 className="text-2xl font-semibold">Contas e investimentos</h2><p className="text-muted-foreground mt-2">Posições declaradas. Os valores já devem estar incluídos no patrimônio do diagnóstico.</p>
        <div className="overflow-x-auto"><table className="wealth-table"><thead><tr><th>Posição</th><th>Instituição</th><th>Valor</th><th>Ação</th></tr></thead><tbody>{state.holdings.map(h => <tr key={h.id}><td>{h.name}</td><td>{h.institution}</td><td>{new Intl.NumberFormat("pt-BR",{style:"currency",currency:h.currency}).format(h.value)}</td><td><button className="text-primary" onClick={() => setHolding({id:h.id,name:h.name,institution:h.institution,issuer:h.issuer,asset_class:h.asset_class,value:h.value,currency:h.currency})}>Atualizar</button></td></tr>)}</tbody></table></div>
        <form className="grid gap-3 sm:grid-cols-2 mt-4" onSubmit={e => {e.preventDefault(); void act(async () => {const {id,...body} = holding; await request(id ? `/holdings/${id}` : "/holdings",id ? "PUT" : "POST",body); await refresh(); setHolding({...holding,id:undefined,name:"",value:0}); setNotice("Posição salva.");});}}>
          {(["name","institution","issuer"] as const).map((key,i) => <label key={key}>{["Nome do investimento ou conta","Instituição","Emissor"][i]}<Input required maxLength={120} value={holding[key]} onChange={e => setHolding({...holding,[key]:e.target.value})}/></label>)}
          <label>Saldo ou valor atual<Input required type="number" min={0} step={.01} value={holding.value} onChange={e => setHolding({...holding,value:Number(e.target.value)})}/></label>
          <label>Classe<select className="wealth-select" value={holding.asset_class} onChange={e => setHolding({...holding,asset_class:e.target.value})}>{[["liquidez","Liquidez"],["inflacao","Inflação"],["brasil","Ações Brasil"],["global","Ações globais"],["imobiliario","FIIs"],["outros","Outros"]].map(([k,v]) => <option key={k} value={k}>{v}</option>)}</select></label><label>Moeda<select className="wealth-select" value={holding.currency} onChange={e => setHolding({...holding,currency:e.target.value})}><option>BRL</option><option>USD</option><option>EUR</option></select></label><Button disabled={busy} type="submit">Salvar posição</Button>
        </form></section>
        <section className="wealth-panel"><h2 className="text-xl font-semibold">Importar movimentações</h2><p className="mt-2 text-muted-foreground">CSV: date,description,amount,id. Data AAAA-MM-DD, despesas negativas. OFX usa FITID para evitar duplicação. Importação em reais, sem alterar seu diagnóstico automaticamente.</p>
          <label className="block mt-4">Nome da conta<Input value={statement.account} onChange={e => changeStatement({...statement,account:e.target.value})}/></label>
          <label className="block mt-3">Arquivo CSV ou OFX<Input type="file" accept=".csv,.ofx" onChange={e => {const file = e.target.files?.[0]; if(!file) return; if(file.size > 1_000_000) {setError("O arquivo deve ter até 1 MB.");return;} void file.text().then(content => changeStatement({...statement,format:file.name.toLowerCase().endsWith(".ofx") ? "ofx" : "csv",content}));}}/></label>
          <Button className="mt-3" variant="outline" disabled={busy || !statement.content || !statement.account} onClick={() => void act(async () => setPreview(await request<Preview>("/imports","POST",{...statement,confirm:false})))}>Ver prévia</Button>
          {preview && <div className="mt-4"><p>{preview.new_count} novas movimentações · {preview.duplicates} já presentes</p><div className="overflow-auto max-h-64"><table className="wealth-table"><thead><tr><th>Data</th><th>Descrição</th><th>Valor</th></tr></thead><tbody>{preview.rows.map((r,i) => <tr key={i}><td>{r.date}</td><td>{r.description}</td><td>{formatCurrency(r.amount)}</td></tr>)}</tbody></table></div><Button disabled={busy || preview.confirmed || !preview.new_count} onClick={() => void act(async () => {setPreview(await request("/imports","POST",{...statement,confirm:true})); await refresh(); setNotice("Extrato importado.");})}>Confirmar importação</Button></div>}
          {!!Object.keys(state.cashflow).length && <div className="mt-5"><h3 className="font-semibold">Saldo das movimentações importadas por mês</h3>{Object.entries(state.cashflow).sort().map(([month,value]) => <p className="mt-2" key={month}>{month}: {formatCurrency(value)}</p>)}</div>}
        </section>
        <section className="wealth-panel"><h2 className="text-xl font-semibold">Conexões</h2><p className="mt-3">Open Finance: aguardando integração com parceiro participante e consentimento.</p><p className="mt-2">B3 e ofertas de corretoras: aguardando contratação da fonte de dados.</p></section>
      </div>}
      {tab === "Conta" && <Suspense fallback={<p>Carregando conta…</p>}><AccountSecurity/></Suspense>}
    </>}
  </main><footer className="py-8 text-center text-sm text-muted-foreground">Prisma · Planejamento com dados, contexto e escolhas conscientes.</footer></div>;
}
