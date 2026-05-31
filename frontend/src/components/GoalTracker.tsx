/**
 * 📌 GoalTracker.tsx — Componente de Metas Financeiras
 *
 * CONCEITOS IMPORTANTES:
 *
 * 1. COMPONENTE CONTROLADO (Controlled Component):
 *    O estado do formulário vive no React (useState), não no DOM.
 *    Cada mudança no input atualiza o state → React re-renderiza → input reflete o state.
 *    Isso nos dá controle total: podemos validar, transformar, etc.
 *
 * 2. TABS PARA DIFERENTES MODOS:
 *    Usamos Tabs do Radix UI para criar uma UX clara:
 *    - "Calcular Aporte": Usuário informa prazo, sistema calcula o aporte
 *    - "Calcular Prazo": Usuário informa aporte, sistema calcula o prazo
 *    Isso evita confusão com campos opcionais.
 *
 * 3. PROGRESS BAR ANIMADA:
 *    O progresso visual (patrimônio atual / meta) cria engajamento emocional.
 *    Usamos transição CSS para animar suavemente.
 *
 * 4. FETCH API:
 *    Chamamos o backend com fetch() — mesma técnica usada no Index.tsx.
 *    POST com body JSON, headers Content-Type, e tratamento de erro.
 */

import { useState } from "react";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
    MetaFinanceiraInput,
    MetaFinanceiraResponse,
    EvolucaoPatrimonio,
} from "@/types/roboAdvisor";
import { useAuth } from "@/contexts/AuthContext";
import {
    Target,
    Loader2,
    TrendingUp,
    Calendar,
    DollarSign,
    CheckCircle2,
    XCircle,
    Sparkles,
    ArrowRight,
    Wallet,
    Clock,
    Percent,
    BarChart3,
} from "lucide-react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { API_URL } from "@/config";
import { apiFetch, ApiError, authHeaders } from "@/utils/api";
import { formatCurrency, formatCurrencyShort } from "@/utils/format";
import type { TooltipProps } from "recharts";
import type { ValueType, NameType } from "recharts/types/component/DefaultTooltipContent";

// ─── COMPONENTE PRINCIPAL ────────────────────────────────────────────
const GoalTracker = () => {
    // Estado do modo selecionado na tab
    const [modo, setModo] = useState<"calcular_aporte" | "calcular_prazo">(
        "calcular_aporte"
    );

    // Estado do formulário — espelha MetaFinanceiraInput do backend
    const [formData, setFormData] = useState({
        valor_alvo: 1_000_000,
        patrimonio_atual: 50_000,
        aporte_mensal: 2_000,
        prazo_desejado: 15,
        objetivo: "crescimento" as MetaFinanceiraInput["objetivo"],
    });

    // Estados de loading, erro e resultado
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [resultado, setResultado] = useState<MetaFinanceiraResponse | null>(
        null
    );
    const { token } = useAuth();

    // ─── HANDLER DE SUBMIT ──────────────────────────────────────────
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); // Previne reload da página (comportamento padrão de forms)
        setIsLoading(true);
        setError(null);

        try {
            // Monta o payload com base no modo selecionado
            // Se modo é "calcular_aporte", NÃO envia aporte_mensal (backend calcula)
            // Se modo é "calcular_prazo", NÃO envia prazo_desejado (backend calcula)
            const payload: MetaFinanceiraInput = {
                valor_alvo: formData.valor_alvo,
                patrimonio_atual: formData.patrimonio_atual,
                objetivo: formData.objetivo,
                ...(modo === "calcular_aporte"
                    ? { prazo_desejado: formData.prazo_desejado }
                    : { aporte_mensal: formData.aporte_mensal }),
            };

            const result = await apiFetch<MetaFinanceiraResponse>(
                `${API_URL}/meta`,
                { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }
            );
            setResultado(result);
        } catch (err) {
            setError(
                err instanceof ApiError || err instanceof Error
                    ? err.message
                    : "Erro ao conectar com o servidor."
            );
        } finally {
            setIsLoading(false);
        }
    };

    // ─── HANDLER GENÉRICO DE MUDANÇA ──────────────────────────────────
    // Reutiliza lógica para todos os inputs numéricos.
    // O `field` é tipado com keyof para garantir que só aceita campos válidos.
    const handleChange = (
        field: keyof typeof formData,
        value: string | number
    ) => {
        setFormData((prev) => ({
            ...prev,
            [field]:
                typeof value === "string" && field !== "objetivo"
                    ? Number(value)
                    : value,
        }));
    };

    // ─── TOOLTIP CUSTOMIZADO PARA O GRÁFICO ────────────────────────────
    const CustomTooltip = ({ active, payload, label }: TooltipProps<ValueType, NameType>) => {
        if (active && payload?.length) {
            return (
                <div className="rounded-lg border bg-card p-3 shadow-lg">
                    <p className="text-sm font-medium text-muted-foreground">
                        Ano {label}
                    </p>
                    <p className="text-lg font-bold text-primary">
                        {formatCurrency(Number(payload[0].value))}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6">
            {/* ═══ CARD DO FORMULÁRIO ═══ */}
            <Card className="w-full shadow-lg border-primary/20">
                <CardHeader className="space-y-1">
                    <div className="flex items-center gap-2">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 text-white">
                            <Target className="h-5 w-5" />
                        </div>
                        <div>
                            <CardTitle className="text-xl">🎯 Metas Financeiras</CardTitle>
                            <CardDescription>
                                Defina seu objetivo e descubra o caminho para alcançá-lo
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>

                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Campos comuns a ambos os modos */}
                        <div className="grid gap-5 sm:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="goal-valor_alvo">
                                    <Target className="inline h-4 w-4 mr-1" />
                                    Valor-Alvo
                                </Label>
                                <Input
                                    id="goal-valor_alvo"
                                    type="number"
                                    min={1000}
                                    step="any"
                                    value={formData.valor_alvo}
                                    onChange={(e) => handleChange("valor_alvo", e.target.value)}
                                    placeholder="1000000"
                                />
                                <p className="text-xs text-muted-foreground">
                                    {formatCurrency(formData.valor_alvo)}
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="goal-patrimonio_atual">
                                    <Wallet className="inline h-4 w-4 mr-1" />
                                    Patrimônio Atual
                                </Label>
                                <Input
                                    id="goal-patrimonio_atual"
                                    type="number"
                                    min={0}
                                    step="any"
                                    value={formData.patrimonio_atual}
                                    onChange={(e) =>
                                        handleChange("patrimonio_atual", e.target.value)
                                    }
                                    placeholder="50000"
                                />
                                <p className="text-xs text-muted-foreground">
                                    {formatCurrency(formData.patrimonio_atual)}
                                </p>
                            </div>

                            <div className="space-y-2 sm:col-span-2">
                                <Label htmlFor="goal-objetivo">Objetivo</Label>
                                <Select
                                    value={formData.objetivo}
                                    onValueChange={(value) => handleChange("objetivo", value)}
                                >
                                    <SelectTrigger id="goal-objetivo">
                                        <SelectValue placeholder="Selecione o objetivo" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="aposentadoria">
                                            🏖️ Aposentadoria
                                        </SelectItem>
                                        <SelectItem value="imovel">🏠 Imóvel</SelectItem>
                                        <SelectItem value="reserva">
                                            🛡️ Reserva de Emergência
                                        </SelectItem>
                                        <SelectItem value="crescimento">
                                            📈 Crescimento Patrimonial
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        {/* ─── TABS: escolher o que calcular ─── */}
                        {/*
              CONCEITO: Tabs controlam qual campo aparece.
              Ao trocar de tab, mudamos o "modo" — isso determina qual
              campo é enviado ao backend e qual é calculado.
            */}
                        <Tabs
                            value={modo}
                            onValueChange={(v) =>
                                setModo(v as "calcular_aporte" | "calcular_prazo")
                            }
                            className="w-full"
                        >
                            <TabsList className="grid w-full grid-cols-2">
                                <TabsTrigger value="calcular_aporte">
                                    <DollarSign className="h-4 w-4 mr-1" />
                                    Calcular Aporte
                                </TabsTrigger>
                                <TabsTrigger value="calcular_prazo">
                                    <Calendar className="h-4 w-4 mr-1" />
                                    Calcular Prazo
                                </TabsTrigger>
                            </TabsList>

                            {/* Tab 1: Informar prazo → backend calcula aporte */}
                            <TabsContent value="calcular_aporte" className="space-y-3 pt-2">
                                <p className="text-sm text-muted-foreground">
                                    Informe o prazo desejado e descubra quanto precisa aportar por
                                    mês.
                                </p>
                                <div className="space-y-2">
                                    <Label htmlFor="goal-prazo">
                                        <Clock className="inline h-4 w-4 mr-1" />
                                        Prazo (anos)
                                    </Label>
                                    <Input
                                        id="goal-prazo"
                                        type="number"
                                        min={1}
                                        max={50}
                                        value={formData.prazo_desejado}
                                        onChange={(e) =>
                                            handleChange("prazo_desejado", e.target.value)
                                        }
                                        placeholder="15"
                                    />
                                </div>
                            </TabsContent>

                            {/* Tab 2: Informar aporte → backend calcula prazo */}
                            <TabsContent value="calcular_prazo" className="space-y-3 pt-2">
                                <p className="text-sm text-muted-foreground">
                                    Informe quanto pode investir por mês e descubra quando
                                    atingirá sua meta.
                                </p>
                                <div className="space-y-2">
                                    <Label htmlFor="goal-aporte">
                                        <DollarSign className="inline h-4 w-4 mr-1" />
                                        Aporte Mensal
                                    </Label>
                                    <Input
                                        id="goal-aporte"
                                        type="number"
                                        min={50}
                                        step="any"
                                        value={formData.aporte_mensal}
                                        onChange={(e) =>
                                            handleChange("aporte_mensal", e.target.value)
                                        }
                                        placeholder="2000"
                                    />
                                    <p className="text-xs text-muted-foreground">
                                        {formatCurrency(formData.aporte_mensal)}
                                    </p>
                                </div>
                            </TabsContent>
                        </Tabs>

                        {/* Botão de submit */}
                        <Button
                            type="submit"
                            className="w-full"
                            size="lg"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Calculando...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="mr-2 h-4 w-4" />
                                    Calcular Meta
                                </>
                            )}
                        </Button>
                    </form>

                    {/* ─── ERROS ─── */}
                    {error && (
                        <div className="mt-4 rounded-lg border border-destructive/50 bg-destructive/10 p-4">
                            <div className="flex items-center gap-2">
                                <XCircle className="h-5 w-5 text-destructive" />
                                <p className="text-sm font-medium text-destructive">{error}</p>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* ═══ RESULTADO ═══ */}
            {resultado && <GoalResult resultado={resultado} />}
        </div>
    );
};

// ─── SUBCOMPONENTE: GoalResult ─────────────────────────────────────
/**
 * CONCEITO: Separar em subcomponente melhora:
 * 1. Legibilidade — cada componente tem uma responsabilidade
 * 2. Performance — React só re-renderiza se as props mudarem
 * 3. Testabilidade — pode testar o resultado isoladamente
 */
interface GoalResultProps {
    resultado: MetaFinanceiraResponse;
}

const GoalResult = ({ resultado }: GoalResultProps) => {
    const {
        modo,
        aporte_mensal,
        prazo_anos,
        retorno_anual_estimado,
        simulacao,
        meta_atingida,
        progresso_atual,
        valor_alvo,
        mensagem,
        aporte_sugerido,
    } = resultado;

    // Labels amigáveis para o modo
    const modoLabels = {
        calcular_aporte: "Aporte Calculado",
        calcular_prazo: "Prazo Calculado",
        verificar_viabilidade: "Verificação de Viabilidade",
        meta_ja_atingida: "Meta Já Atingida",
    };

    return (
        <div className="space-y-6 animate-in fade-in-50 slide-in-from-bottom-4 duration-500">
            {/* ─── Status Badge + Título ─── */}
            <Card className="shadow-lg overflow-hidden">
                <div
                    className={`h-1.5 w-full ${meta_atingida
                        ? "bg-gradient-to-r from-emerald-400 to-emerald-600"
                        : "bg-gradient-to-r from-amber-400 to-red-500"
                        }`}
                />
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            {meta_atingida ? (
                                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-950">
                                    <CheckCircle2 className="h-7 w-7 text-emerald-600" />
                                </div>
                            ) : (
                                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-950">
                                    <XCircle className="h-7 w-7 text-amber-600" />
                                </div>
                            )}
                            <div>
                                <CardTitle className="text-xl">
                                    {meta_atingida ? "Meta Alcançável! 🎉" : "Meta Desafiadora"}
                                </CardTitle>
                                <p className="text-sm text-muted-foreground">
                                    {modoLabels[modo]}
                                </p>
                            </div>
                        </div>
                        <Badge
                            variant={meta_atingida ? "default" : "destructive"}
                            className="text-sm px-3 py-1"
                        >
                            {meta_atingida ? "Viável" : "Ajustes Necessários"}
                        </Badge>
                    </div>
                </CardHeader>

                <CardContent className="space-y-6">
                    {/* ─── Barra de Progresso ─── */}
                    {/*
            CONCEITO: O Progress usa CSS transform: translateX(-X%)
            para criar a barra preenchida. O valor 0-100 controla a posição.
            A classe "transition-all" anima a mudança automaticamente.
          */}
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Progresso Atual</span>
                            <span className="font-bold text-foreground">
                                {Math.min(progresso_atual, 100).toFixed(1)}%
                            </span>
                        </div>
                        <Progress
                            value={Math.min(progresso_atual, 100)}
                            className="h-4"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>R$ 0</span>
                            <span>{formatCurrencyShort(valor_alvo)}</span>
                        </div>
                    </div>

                    {/* ─── Métricas Principais ─── */}
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <MetricCard
                            icon={<DollarSign className="h-5 w-5" />}
                            label="Aporte Mensal"
                            value={formatCurrency(aporte_mensal)}
                            color="from-blue-500 to-blue-600"
                            highlight={modo === "calcular_aporte"}
                        />
                        <MetricCard
                            icon={<Clock className="h-5 w-5" />}
                            label="Prazo"
                            value={
                                prazo_anos === -1 ? "> 50 anos" : `${prazo_anos} anos`
                            }
                            color="from-violet-500 to-violet-600"
                            highlight={modo === "calcular_prazo"}
                        />
                        <MetricCard
                            icon={<Target className="h-5 w-5" />}
                            label="Valor Projetado"
                            value={formatCurrency(simulacao.valor_final)}
                            color="from-emerald-500 to-emerald-600"
                        />
                        <MetricCard
                            icon={<Percent className="h-5 w-5" />}
                            label="Retorno Estimado"
                            value={`${retorno_anual_estimado}% a.a.`}
                            color="from-amber-500 to-amber-600"
                        />
                    </div>

                    {/* ─── Detalhes da Simulação ─── */}
                    <div className="grid gap-4 sm:grid-cols-3">
                        <div className="rounded-xl border bg-card/50 p-4 text-center">
                            <p className="text-xs text-muted-foreground mb-1">
                                Total Aportado
                            </p>
                            <p className="text-lg font-bold text-foreground">
                                {formatCurrency(simulacao.total_aportado)}
                            </p>
                        </div>
                        <div className="rounded-xl border bg-card/50 p-4 text-center">
                            <p className="text-xs text-muted-foreground mb-1">
                                Rendimento (juros compostos)
                            </p>
                            <p className="text-lg font-bold text-emerald-600">
                                +{formatCurrency(simulacao.rendimento)}
                            </p>
                        </div>
                        <div className="rounded-xl border bg-card/50 p-4 text-center">
                            <p className="text-xs text-muted-foreground mb-1">
                                Meta
                            </p>
                            <p className="text-lg font-bold text-primary">
                                {formatCurrency(valor_alvo)}
                            </p>
                        </div>
                    </div>

                    {/* ─── Mensagem do Backend ─── */}
                    {mensagem && (
                        <div
                            className={`rounded-lg p-4 ${meta_atingida
                                ? "bg-emerald-50 border border-emerald-200 dark:bg-emerald-950/30 dark:border-emerald-800"
                                : "bg-amber-50 border border-amber-200 dark:bg-amber-950/30 dark:border-amber-800"
                                }`}
                        >
                            <div className="flex items-start gap-2">
                                {meta_atingida ? (
                                    <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600 mt-0.5" />
                                ) : (
                                    <Sparkles className="h-5 w-5 shrink-0 text-amber-600 mt-0.5" />
                                )}
                                <div>
                                    <p
                                        className={`text-sm ${meta_atingida
                                            ? "text-emerald-800 dark:text-emerald-200"
                                            : "text-amber-800 dark:text-amber-200"
                                            }`}
                                    >
                                        {mensagem}
                                    </p>
                                    {aporte_sugerido && (
                                        <p className="mt-2 text-sm font-semibold text-primary">
                                            <ArrowRight className="inline h-4 w-4 mr-1" />
                                            Aporte sugerido: {formatCurrency(aporte_sugerido)}/mês
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* ─── Gráfico de Evolução ─── */}
            {simulacao.evolucao_anual.length > 0 && (
                <Card className="shadow-lg">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-primary" />
                            <CardTitle>Projeção de Crescimento</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <GoalChart
                            evolucao={simulacao.evolucao_anual}
                            valorAlvo={valor_alvo}
                        />
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

// ─── SUBCOMPONENTE: MetricCard ──────────────────────────────────────
/**
 * CONCEITO: Componente reutilizável para cards de métricas.
 * Recebe icon, label, value, color via props.
 * O `highlight` adiciona destaque visual quando o campo foi CALCULADO.
 */
interface MetricCardProps {
    icon: React.ReactNode; // Qualquer JSX válido (ícone Lucide)
    label: string;
    value: string;
    color: string; // Classes Tailwind de gradiente (ex: "from-blue-500 to-blue-600")
    highlight?: boolean;
}

const MetricCard = ({
    icon,
    label,
    value,
    color,
    highlight,
}: MetricCardProps) => (
    <div
        className={`relative overflow-hidden rounded-xl border p-4 transition-all ${highlight
            ? "border-primary/50 bg-primary/5 ring-2 ring-primary/20"
            : "bg-card"
            }`}
    >
        {highlight && (
            <div className="absolute -top-1 -right-1">
                <Badge className="text-[10px] px-1.5 py-0 rounded-bl-lg rounded-tr-lg">
                    Calculado
                </Badge>
            </div>
        )}
        <div
            className={`mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${color} text-white`}
        >
            {icon}
        </div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p
            className={`mt-1 text-lg font-bold ${highlight ? "text-primary" : "text-foreground"
                }`}
        >
            {value}
        </p>
    </div>
);

// ─── SUBCOMPONENTE: GoalChart ───────────────────────────────────────
/**
 * CONCEITO: Gráfico de área com linha de meta (reference line visual).
 * Usamos Recharts (mesma lib do EvolutionChart.tsx).
 * A "área" preenchida com gradiente cria uma visualização profissional.
 */
interface GoalChartProps {
    evolucao: EvolucaoPatrimonio[];
    valorAlvo: number;
}

const GoalChart = ({ evolucao, valorAlvo }: GoalChartProps) => {
    // Adiciona a linha de meta como dado extra no gráfico
    const dataWithGoal = evolucao.map((item) => ({
        ...item,
        meta: valorAlvo,
    }));

    const CustomChartTooltip = ({ active, payload, label }: TooltipProps<ValueType, NameType>) => {
        if (active && payload?.length) {
            return (
                <div className="rounded-lg border bg-card p-3 shadow-lg">
                    <p className="text-sm font-medium text-muted-foreground">
                        Ano {label}
                    </p>
                    <p className="text-lg font-bold text-primary">
                        {formatCurrency(Number(payload[0].value))}
                    </p>
                    <p className="text-xs text-muted-foreground">
                        Meta: {formatCurrency(valorAlvo)}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                    data={dataWithGoal}
                    margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
                >
                    <defs>
                        <linearGradient id="colorGoalValor" x1="0" y1="0" x2="0" y2="1">
                            <stop
                                offset="5%"
                                stopColor="hsl(var(--primary))"
                                stopOpacity={0.3}
                            />
                            <stop
                                offset="95%"
                                stopColor="hsl(var(--primary))"
                                stopOpacity={0}
                            />
                        </linearGradient>
                    </defs>
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="hsl(var(--border))"
                    />
                    <XAxis
                        dataKey="ano"
                        axisLine={false}
                        tickLine={false}
                        tick={{
                            fill: "hsl(var(--muted-foreground))",
                            fontSize: 12,
                        }}
                        tickFormatter={(value) => `Ano ${value}`}
                    />
                    <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{
                            fill: "hsl(var(--muted-foreground))",
                            fontSize: 12,
                        }}
                        tickFormatter={formatCurrencyShort}
                        width={80}
                    />
                    <Tooltip content={<CustomChartTooltip />} />

                    {/* Linha tracejada da meta */}
                    <Area
                        type="monotone"
                        dataKey="meta"
                        stroke="hsl(var(--destructive))"
                        strokeWidth={2}
                        strokeDasharray="8 4"
                        fill="none"
                        name="Meta"
                    />

                    {/* Área preenchida do patrimônio projetado */}
                    <Area
                        type="monotone"
                        dataKey="valor"
                        stroke="hsl(var(--primary))"
                        strokeWidth={3}
                        fill="url(#colorGoalValor)"
                        name="Patrimônio"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default GoalTracker;
