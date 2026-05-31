import { useState } from "react";
import Header from "@/components/Header";
import InvestorForm from "@/components/InvestorForm";
import InvestorProfile from "@/components/InvestorProfile";
import PortfolioCards from "@/components/PortfolioCards";
import FinancialSummary from "@/components/FinancialSummary";
import EvolutionChart from "@/components/EvolutionChart";
import GoalTracker from "@/components/GoalTracker";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { InvestorFormData, PlanejamentoResponse } from "@/types/roboAdvisor";
import { AlertCircle, RotateCcw } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { API_URL } from "@/config";
import { apiFetch, ApiError, authHeaders } from "@/utils/api";

const ResultsSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    {/* Profile skeleton */}
    <div className="rounded-xl border p-6 space-y-3">
      <Skeleton className="h-6 w-40" />
      <Skeleton className="h-4 w-64" />
    </div>
    {/* Portfolio cards skeleton */}
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="rounded-xl border p-4 space-y-3">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-6 w-16" />
        </div>
      ))}
    </div>
    {/* Summary skeleton */}
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="rounded-xl border p-4 space-y-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-7 w-32" />
        </div>
      ))}
    </div>
    {/* Chart skeleton */}
    <div className="rounded-xl border p-6">
      <Skeleton className="h-[350px] w-full" />
    </div>
  </div>
);

const Index = () => {
  const { token } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<PlanejamentoResponse | null>(null);

  const handleSubmit = async (data: InvestorFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiFetch<PlanejamentoResponse>(
        `${API_URL}/planejamento`,
        { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) }
      );
      setResultado(result);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Erro ao conectar com o servidor. Verifique se a API está rodando."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-6xl space-y-8">
          {/* Hero Section */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-foreground sm:text-4xl">
              Planeje seu futuro financeiro
            </h2>
            <p className="mt-3 text-lg text-muted-foreground">
              Receba recomendações personalizadas baseadas no seu perfil de investidor
            </p>
          </div>

          {/* Form */}
          <div className="mx-auto max-w-2xl">
            <InvestorForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>

          {/* Error State */}
          {error && (
            <Alert variant="destructive" className="mx-auto max-w-2xl">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Erro</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Loading skeleton */}
          {isLoading && <ResultsSkeleton />}

          {/* Results */}
          {!isLoading && resultado && (
            <div className="space-y-6 animate-in fade-in-50 slide-in-from-bottom-4 duration-500">
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setResultado(null)}
                  className="gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Nova Análise
                </Button>
              </div>
              <InvestorProfile perfil={resultado.perfil} />
              <PortfolioCards carteira={resultado.carteira} />
              <FinancialSummary resumo={resultado.resumo} />
              <EvolutionChart evolucao={resultado.evolucao} />
            </div>
          )}

          {/* ─── Seção de Metas Financeiras ─── */}
          <Separator className="my-8" />

          <div className="text-center">
            <h2 className="text-3xl font-bold text-foreground sm:text-4xl">
              🎯 Metas Financeiras
            </h2>
            <p className="mt-3 text-lg text-muted-foreground">
              Defina um valor-alvo e descubra o aporte ideal ou prazo necessário
            </p>
          </div>

          <div className="mx-auto max-w-4xl">
            <GoalTracker />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-card/50 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2024 Robo Advisor. Planejamento financeiro inteligente.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
