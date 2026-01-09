import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, Shield, TrendingUp, Zap } from "lucide-react";

interface InvestorProfileProps {
  perfil: string;
}

const profileConfig: Record<string, { icon: React.ReactNode; color: string; description: string }> = {
  conservador: {
    icon: <Shield className="h-6 w-6" />,
    color: "bg-blue-500/10 text-blue-600 border-blue-200",
    description: "Prioriza segurança e preservação do capital",
  },
  moderado: {
    icon: <User className="h-6 w-6" />,
    color: "bg-amber-500/10 text-amber-600 border-amber-200",
    description: "Equilibra risco e retorno de forma balanceada",
  },
  arrojado: {
    icon: <TrendingUp className="h-6 w-6" />,
    color: "bg-emerald-500/10 text-emerald-600 border-emerald-200",
    description: "Busca maiores retornos aceitando mais volatilidade",
  },
  agressivo: {
    icon: <Zap className="h-6 w-6" />,
    color: "bg-rose-500/10 text-rose-600 border-rose-200",
    description: "Foco em maximizar ganhos com alta tolerância a risco",
  },
};

const InvestorProfile = ({ perfil }: InvestorProfileProps) => {
  const config = profileConfig[perfil.toLowerCase()] || profileConfig.moderado;

  return (
    <Card className="overflow-hidden border-2 border-primary/20 shadow-lg">
      <CardContent className="flex items-center gap-4 p-6">
        <div className={`flex h-14 w-14 items-center justify-center rounded-xl ${config.color}`}>
          {config.icon}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Seu Perfil</h3>
            <Badge variant="secondary" className="text-sm font-medium capitalize">
              {perfil}
            </Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{config.description}</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default InvestorProfile;
