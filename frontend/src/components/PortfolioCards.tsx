import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CarteiraItem } from "@/types/roboAdvisor";
import { PieChart, Wallet, TrendingUp, Shield, Landmark, Coins } from "lucide-react";

interface PortfolioCardsProps {
  carteira: CarteiraItem[];
}

const assetIcons: Record<string, React.ReactNode> = {
  acoes: <TrendingUp className="h-5 w-5" />,
  fiis: <Landmark className="h-5 w-5" />,
  renda_fixa: <Shield className="h-5 w-5" />,
  tesouro: <Coins className="h-5 w-5" />,
  default: <Wallet className="h-5 w-5" />,
};

const assetColors: Record<string, string> = {
  acoes: "from-blue-500 to-blue-600",
  fiis: "from-violet-500 to-violet-600",
  renda_fixa: "from-emerald-500 to-emerald-600",
  tesouro: "from-amber-500 to-amber-600",
  default: "from-slate-500 to-slate-600",
};

const getAssetKey = (ativo: string): string => {
  const normalized = ativo.toLowerCase().replace(/[^a-z]/g, "_");
  if (normalized.includes("aco") || normalized.includes("equity")) return "acoes";
  if (normalized.includes("fii") || normalized.includes("imobil")) return "fiis";
  if (normalized.includes("fixa") || normalized.includes("cdb") || normalized.includes("lci")) return "renda_fixa";
  if (normalized.includes("tesouro") || normalized.includes("selic")) return "tesouro";
  return "default";
};

const PortfolioCards = ({ carteira }: PortfolioCardsProps) => {
  return (
    <Card className="shadow-lg">
      <CardHeader>
        <div className="flex items-center gap-2">
          <PieChart className="h-5 w-5 text-primary" />
          <CardTitle>Carteira Recomendada</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {carteira.map((item, index) => {
            const assetKey = getAssetKey(item.ativo);
            const icon = assetIcons[assetKey] || assetIcons.default;
            const colorClass = assetColors[assetKey] || assetColors.default;

            return (
              <div
                key={index}
                className="group relative overflow-hidden rounded-xl border bg-card p-4 transition-all hover:shadow-md"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${colorClass} opacity-5 transition-opacity group-hover:opacity-10`} />
                <div className="relative">
                  <div className="flex items-center justify-between">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${colorClass} text-primary-foreground`}>
                      {icon}
                    </div>
                    <span className="text-2xl font-bold text-foreground">
                      {item.percentual}%
                    </span>
                  </div>
                  <h4 className="mt-3 font-medium text-foreground">{item.ativo}</h4>
                  {item.descricao && (
                    <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                      {item.descricao}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default PortfolioCards;
