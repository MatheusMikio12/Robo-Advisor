import { Recommendation } from "@/types/wealth";
import { formatCurrency } from "@/utils/format";

export default function WealthPortfolio({ plan, stale }: {plan: Recommendation; stale: boolean}) {
  return <section className="space-y-6">
    {stale && <p role="status" className="wealth-notice">Seu contexto mudou ou as referências venceram. Gere uma nova carteira para atualizar a análise.</p>}
    <div className="wealth-panel"><h2 className="text-2xl font-semibold">Uma função para cada parte do seu dinheiro</h2>
      <p className="mt-2 text-muted-foreground">{plan.policy.profile} · Análise de {new Date(plan.generated_at).toLocaleString("pt-BR")}</p>
      <ul className="list-disc pl-5 mt-4 space-y-2">{plan.policy.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>
      {plan.policy.selection_blocked && <p className="wealth-notice mt-4">Seleção de produtos suspensa pelas restrições do diagnóstico.</p>}
      <div className="mt-6 space-y-6">{plan.allocation.map(slot => <div className="border-t pt-5" key={slot.key}>
        <div className="flex justify-between gap-3"><h3 className="font-semibold text-lg">{slot.name}</h3><strong className="text-xl tabular-nums">{slot.percent}%</strong></div>
        {slot.products.map(choice => <details className="wealth-product" key={choice.product.id}>
          <summary><span><strong>{choice.product.name}</strong><small>{choice.percent}% · {formatCurrency(choice.amount)}</small></span><span>Ver motivos e custos</span></summary>
          <div className="space-y-3 pt-4"><p>{choice.why}</p><p className="text-sm text-muted-foreground">{choice.product.quote_type}</p>
            <dl className="wealth-review"><div><dt>Taxa de referência</dt><dd>{choice.product.indexer} {choice.product.rate_pct}% a.a.</dd></div>
              <div><dt>Liquidação de referência</dt><dd>{choice.product.liquidity_days} dia útil</dd></div>
              <div><dt>Vencimento</dt><dd>{choice.product.maturity}</dd></div>
              <div><dt>Mínimo de referência</dt><dd>{formatCurrency(choice.product.minimum ?? 0)}</dd></div>
              <div><dt>Custódia de referência</dt><dd>{choice.product.fee_pct}% a.a.</dd></div>
              <div><dt>Data da informação</dt><dd>{choice.product.as_of}</dd></div></dl>
            <p>{choice.product.risks}</p><p>{choice.product.tax}</p><p>{choice.product.cost_note}</p>
            <a className="text-primary underline" href={choice.product.source} target="_blank" rel="noreferrer">Consultar fonte oficial</a>
            {!!choice.alternatives.length && <div><h4 className="font-medium">Alternativas avaliadas</h4><ul>{choice.alternatives.map(a => <li key={a.id}>{a.name} · pontuação {a.score}</li>)}</ul></div>}
          </div>
        </details>)}
        {slot.unallocated_percent > 0 && <p className="mt-3 text-muted-foreground">{slot.unallocated_percent}% aguardando produtos elegíveis. {slot.message}</p>}
      </div>)}</div>
    </div>
    {!!plan.drift.length && <div className="wealth-panel"><h3 className="text-lg font-semibold">Sua carteira atual e o plano</h3><p className="text-muted-foreground mt-1">Desvios a partir de 5 pontos percentuais pedem revisão; não geram ordens.</p><div className="overflow-x-auto"><table className="wealth-table"><thead><tr><th>Classe</th><th>Atual</th><th>Plano</th><th>Revisão</th></tr></thead><tbody>{plan.drift.map(x => <tr key={x.name}><td>{x.name}</td><td>{x.actual}%</td><td>{x.target}%</td><td>{x.review ? "Revisar exposição" : "Dentro do limite"}</td></tr>)}</tbody></table></div></div>}
    <details className="wealth-panel"><summary className="cursor-pointer font-medium">Como esta análise foi construída</summary><p className="mt-4">{plan.method}</p><ul className="list-disc pl-5 mt-3">{plan.policy.assumptions.map(x => <li key={x}>{x}</li>)}</ul><p className="mt-3 text-sm">Política {plan.policy.version} · Revisão do perfil {plan.profile_revision}</p>
      {!!plan.excluded.length && <div className="mt-4"><h4>Produtos excluídos</h4>{plan.excluded.map((p, i) => <p key={`${p.id}-${i}`} className="text-sm mt-2">{p.name}: {p.reasons.join("; ")}.</p>)}</div>}
    </details>
  </section>;
}
