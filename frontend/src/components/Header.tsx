import { TrendingUp } from "lucide-react";

const Header = () => {
  return (
    <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground">Robo Advisor</h1>
            <p className="text-xs text-muted-foreground">Planejamento financeiro inteligente</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
