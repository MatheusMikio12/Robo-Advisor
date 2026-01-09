import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PlanejamentoResponse } from "@/types/roboAdvisor";
import { DollarSign, TrendingUp, Percent, BarChart3 } from "lucide-react";

interface FinancialSummaryProps {
  resumo: PlanejamentoResponse["resumo"];
}

const FinancialSummary = ({ resumo }: FinancialSummaryProps) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const metrics = [
    {
      label: "Valor Final Projetado",
      value: formatCurrency(resumo.valor_final),
      icon: <DollarSign className="h-5 w-5" />,
      color: "from-emerald-500 to-emerald-600",
      highlight: true,
    },
    {
      label: "Total Investido",
      value: formatCurrency(resumo.total_investido),
      icon: <BarChart3 className="h-5 w-5" />,
      color: "from-blue-500 to-blue-600",
    },
    {
      label: "Retorno Absoluto",
      value: formatCurrency(resumo.retorno_absoluto),
      icon: <TrendingUp className="h-5 w-5" />,
      color: "from-violet-500 to-violet-600",
    },
    {
      label: "Retorno Percentual",
      value: formatPercent(resumo.retorno_percentual),
      icon: <Percent className="h-5 w-5" />,
      color: "from-amber-500 to-amber-600",
    },
    {
      label: "CAGR",
      value: formatPercent(resumo.cagr),
      icon: <TrendingUp className="h-5 w-5" />,
      color: "from-rose-500 to-rose-600",
    },
  ];

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          <CardTitle>Resumo Financeiro</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {metrics.map((metric, index) => (
            <div
              key={index}
              className={`relative overflow-hidden rounded-xl border p-4 ${
                metric.highlight ? "border-accent/50 bg-accent/5" : "bg-card"
              }`}
            >
              <div className={`mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${metric.color} text-primary-foreground`}>
                {metric.icon}
              </div>
              <p className="text-sm text-muted-foreground">{metric.label}</p>
              <p className={`mt-1 text-lg font-bold ${metric.highlight ? "text-accent-foreground" : "text-foreground"}`}>
                {metric.value}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default FinancialSummary;
