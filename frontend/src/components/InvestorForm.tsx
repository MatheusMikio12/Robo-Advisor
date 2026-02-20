import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { InvestorFormData } from "@/types/roboAdvisor";
import { TrendingUp, Loader2 } from "lucide-react";
import { formatCurrency } from "@/utils/format";

interface InvestorFormProps {
  onSubmit: (data: InvestorFormData) => void;
  isLoading: boolean;
}

const InvestorForm = ({ onSubmit, isLoading }: InvestorFormProps) => {
  const [formData, setFormData] = useState<InvestorFormData>({
    idade: 30,
    renda_mensal: 5000,
    patrimonio_atual: 10000,
    aporte_mensal: 500,
    prazo_anos: 10,
    objetivo: "crescimento",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (field: keyof InvestorFormData, value: string | number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: typeof value === "string" && field !== "objetivo" ? Number(value) : value,
    }));
  };

  return (
    <Card className="w-full shadow-lg">
      <CardHeader className="space-y-1">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-xl">Perfil do Investidor</CardTitle>
            <CardDescription>Preencha seus dados para receber uma recomendação personalizada</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="idade">Idade</Label>
              <Input
                id="idade"
                type="number"
                min={18}
                max={100}
                value={formData.idade}
                onChange={(e) => handleChange("idade", e.target.value)}
                placeholder="30"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="prazo_anos">Prazo (anos)</Label>
              <Input
                id="prazo_anos"
                type="number"
                min={1}
                max={50}
                value={formData.prazo_anos}
                onChange={(e) => handleChange("prazo_anos", e.target.value)}
                placeholder="10"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="renda_mensal">Renda Mensal</Label>
              <Input
                id="renda_mensal"
                type="number"
                min={0}
                step={100}
                value={formData.renda_mensal}
                onChange={(e) => handleChange("renda_mensal", e.target.value)}
                placeholder="5000"
              />
              <p className="text-xs text-muted-foreground">{formatCurrency(formData.renda_mensal)}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="patrimonio_atual">Patrimônio Atual</Label>
              <Input
                id="patrimonio_atual"
                type="number"
                min={0}
                step={1000}
                value={formData.patrimonio_atual}
                onChange={(e) => handleChange("patrimonio_atual", e.target.value)}
                placeholder="10000"
              />
              <p className="text-xs text-muted-foreground">{formatCurrency(formData.patrimonio_atual)}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="aporte_mensal">Aporte Mensal</Label>
              <Input
                id="aporte_mensal"
                type="number"
                min={0}
                step={50}
                value={formData.aporte_mensal}
                onChange={(e) => handleChange("aporte_mensal", e.target.value)}
                placeholder="500"
              />
              <p className="text-xs text-muted-foreground">{formatCurrency(formData.aporte_mensal)}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="objetivo">Objetivo</Label>
              <Select
                value={formData.objetivo}
                onValueChange={(value) => handleChange("objetivo", value)}
              >
                <SelectTrigger id="objetivo">
                  <SelectValue placeholder="Selecione o objetivo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="aposentadoria">Aposentadoria</SelectItem>
                  <SelectItem value="imovel">Imóvel</SelectItem>
                  <SelectItem value="reserva">Reserva de Emergência</SelectItem>
                  <SelectItem value="crescimento">Crescimento Patrimonial</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analisando...
              </>
            ) : (
              <>
                <TrendingUp className="mr-2 h-4 w-4" />
                Gerar Planejamento
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default InvestorForm;
