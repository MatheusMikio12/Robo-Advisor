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
import { InvestorFormData, PlanejamentoResponse } from "@/types/roboAdvisor";
import { AlertCircle } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<PlanejamentoResponse | null>(null);

  const handleSubmit = async (data: InvestorFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/planejamento`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }

      const result: PlanejamentoResponse = await response.json();
      setResultado(result);
    } catch (err) {
      setError(
        err instanceof Error
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

          {/* Results */}
          {resultado && (
            <div className="space-y-6 animate-in fade-in-50 slide-in-from-bottom-4 duration-500">
              <InvestorProfile perfil={resultado.perfil} />
              <PortfolioCards carteira={resultado.carteira} />
              <FinancialSummary resumo={resultado.resumo} />
              <EvolutionChart evolucao={resultado.evolucao} />
            </div>
          )}

          {/* ─── Seção de Metas Financeiras ─── */}
          {/*
            CONCEITO: Separator cria uma divisão visual clara entre
            as seções de "Planejamento" (acima) e "Metas" (abaixo).
            O GoalTracker é independente — tem seu próprio formulário
            e faz suas próprias chamadas à API.
          */}
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
