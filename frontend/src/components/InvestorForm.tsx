import { useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { InvestorFormData } from "@/types/roboAdvisor";
import { formatCurrency } from "@/utils/format";

interface InvestorFormProps { onSubmit: (data: InvestorFormData) => void; isLoading: boolean; }

const objectiveOptions: Array<{ value: InvestorFormData["objetivo"]; label: string; hint: string }> = [
  { value: "crescimento", label: "Construir patrimônio", hint: "Quero fazer meu dinheiro crescer" },
  { value: "reserva", label: "Criar uma reserva", hint: "Quero ter mais tranquilidade" },
  { value: "imovel", label: "Comprar um imóvel", hint: "Quero planejar uma entrada ou compra" },
  { value: "aposentadoria", label: "Planejar a aposentadoria", hint: "Quero cuidar do meu futuro" },
];

const steps = ["objetivo", "idade", "renda_mensal", "patrimonio_atual", "aporte_mensal", "prazo_anos"] as const;
type StepField = (typeof steps)[number];

const questions: Record<Exclude<StepField, "objetivo">, { title: string; helper: string; suffix?: string }> = {
  idade: { title: "Para começar, qual é a sua idade?", helper: "Isso me ajuda a equilibrar prazo e tolerância a oscilações.", suffix: "anos" },
  renda_mensal: { title: "Qual é a sua renda mensal hoje?", helper: "Use uma média aproximada se sua renda variar." },
  patrimonio_atual: { title: "Quanto você já construiu até aqui?", helper: "Considere o valor que já está disponível para investir." },
  aporte_mensal: { title: "Quanto consegue investir por mês?", helper: "Escolha um valor sustentável para a sua rotina." },
  prazo_anos: { title: "Em quanto tempo gostaria de ver esse plano acontecer?", helper: "Depois poderemos comparar prazos diferentes.", suffix: "anos" },
};

const answerLabel = (field: StepField, data: InvestorFormData) => {
  if (field === "objetivo") return objectiveOptions.find((item) => item.value === data.objetivo)?.label ?? "";
  if (field === "idade" || field === "prazo_anos") return `${data[field]} anos`;
  return formatCurrency(data[field]);
};

const InvestorForm = ({ onSubmit, isLoading }: InvestorFormProps) => {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState<InvestorFormData>({ idade: 30, renda_mensal: 5000, patrimonio_atual: 10000, aporte_mensal: 500, prazo_anos: 10, objetivo: "crescimento" });
  const currentField = steps[step];
  const isReview = step === steps.length;
  const progress = Math.round((Math.min(step, steps.length) / steps.length) * 100);
  const completed = useMemo(() => steps.slice(0, step), [step]);
  const advance = () => setStep((current) => Math.min(current + 1, steps.length));
  const goBack = () => setStep((current) => Math.max(current - 1, 0));

  const chooseObjective = (objective: InvestorFormData["objetivo"]) => {
    setFormData((current) => ({ ...current, objetivo: objective }));
    window.setTimeout(advance, 120);
  };

  const handleNumber = (value: string) => {
    if (currentField === "objetivo" || currentField === undefined) return;
    setFormData((current) => ({ ...current, [currentField]: Number(value) }));
  };

  const submitCurrent = (event: React.FormEvent) => {
    event.preventDefault();
    if (isReview) onSubmit(formData); else advance();
  };

  return (
    <section className="concierge-shell" aria-labelledby="concierge-title">
      <div className="concierge-progress" aria-hidden="true"><span style={{ width: `${progress}%` }} /></div>
      <div className="concierge-layout">
        <div className="conversation-pane">
          <div className="conversation-heading">
            <div className="prisma-orb" aria-hidden="true"><span /></div>
            <div><p className="text-sm font-semibold text-foreground">Prisma</p><p className="text-xs text-muted-foreground">Seu concierge financeiro</p></div>
          </div>
          <div className="conversation-history" aria-live="polite">
            {completed.map((field) => <div className="history-row" key={field}><span>{answerLabel(field, formData)}</span></div>)}
          </div>
          <form onSubmit={submitCurrent} className="conversation-current">
            {!isReview && currentField === "objetivo" && <>
              <h2 id="concierge-title">O que você gostaria de conquistar primeiro?</h2>
              <p>Não precisa ter todas as respostas agora. Vamos construir esse plano juntos.</p>
              <div className="objective-grid">
                {objectiveOptions.map((option) => <button key={option.value} type="button" onClick={() => chooseObjective(option.value)}>
                  <strong>{option.label}</strong><span>{option.hint}</span><ArrowRight className="h-4 w-4" />
                </button>)}
              </div>
            </>}
            {!isReview && currentField !== "objetivo" && currentField !== undefined && <>
              <h2 id="concierge-title">{questions[currentField].title}</h2>
              <p>{questions[currentField].helper}</p>
              <div className="answer-composer">
                {currentField !== "idade" && currentField !== "prazo_anos" && <span>R$</span>}
                <Input autoFocus aria-label={questions[currentField].title} type="number"
                  min={currentField === "idade" ? 18 : currentField === "prazo_anos" ? 1 : 0}
                  max={currentField === "idade" ? 100 : currentField === "prazo_anos" ? 50 : undefined}
                  step={currentField === "idade" || currentField === "prazo_anos" ? 1 : 100}
                  value={formData[currentField]} onChange={(event) => handleNumber(event.target.value)} required />
                {questions[currentField].suffix && <span>{questions[currentField].suffix}</span>}
                <Button type="submit" size="icon" aria-label="Continuar"><ArrowRight className="h-5 w-5" /></Button>
              </div>
            </>}
            {isReview && <>
              <div className="review-kicker"><Check className="h-4 w-4" /> Já consigo traçar um primeiro caminho</div>
              <h2 id="concierge-title">Quer que eu monte seu plano?</h2>
              <p>Vou combinar seu objetivo, prazo e capacidade de aporte para apresentar uma carteira e uma projeção inicial.</p>
              <div className="review-summary">
                <div><span>Objetivo</span><strong>{answerLabel("objetivo", formData)}</strong></div>
                <div><span>Horizonte</span><strong>{formData.prazo_anos} anos</strong></div>
                <div><span>Aporte</span><strong>{formatCurrency(formData.aporte_mensal)}/mês</strong></div>
              </div>
              <Button type="submit" size="lg" className="prisma-cta" disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                {isLoading ? "Analisando seu cenário..." : "Criar meu primeiro plano"}
              </Button>
            </>}
            {step > 0 && !isLoading && <button type="button" onClick={goBack} className="back-button"><ArrowLeft className="h-4 w-4" /> Voltar</button>}
          </form>
        </div>
        <aside className="context-pane">
          <div className="context-heading">
            <p className="context-title">Seu contexto</p>
            <span>{step} de {steps.length} respostas</span>
          </div>
          <div className="context-goal">
            <span>Objetivo principal</span>
            <strong>{step > 0 ? answerLabel("objetivo", formData) : "Vamos descobrir juntos"}</strong>
          </div>
          <dl>
            <div><dt>Patrimônio</dt><dd>{step > 3 ? formatCurrency(formData.patrimonio_atual) : "Ainda não informado"}</dd></div>
            <div><dt>Aporte mensal</dt><dd>{step > 4 ? formatCurrency(formData.aporte_mensal) : "Ainda não informado"}</dd></div>
            <div><dt>Prazo</dt><dd>{step > 5 ? `${formData.prazo_anos} anos` : "Ainda não informado"}</dd></div>
          </dl>
          <p className="privacy-note">Você revisa as informações antes de criar o plano.</p>
        </aside>
      </div>
    </section>
  );
};

export default InvestorForm;
