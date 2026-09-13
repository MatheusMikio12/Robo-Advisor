import { LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

const Header = () => {
  const { user, logout } = useAuth();
  return (
    <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="prisma-mark" aria-hidden="true"><span /></div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-foreground">Prisma</h1>
            <p className="text-xs text-muted-foreground">Seu concierge financeiro</p>
          </div>
        </div>
        {user && (
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-muted-foreground hidden sm:inline-block">
              {user.email}
            </span>
            <Button variant="ghost" size="sm" onClick={logout} className="gap-2">
              <LogOut className="h-4 w-4" />
              Sair
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
