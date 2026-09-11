import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Sparkles } from "lucide-react";
import { API_URL } from "@/config";

/** Extrai mensagem legível do corpo de erro da API (string simples ou array de validação 422). */
function extractErrorMessage(body: unknown, fallback: string): string {
    const detail = (body as { detail?: unknown })?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail[0]?.msg ?? fallback;
    return fallback;
}

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isRegistering, setIsRegistering] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const { toast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        const trimmedEmail = email.trim();

        try {
            if (isRegistering) {
                const response = await fetch(`${API_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: trimmedEmail, password }),
                });

                if (response.ok) {
                    toast({ title: "Conta criada com sucesso", description: "Faça login com suas novas credenciais." });
                    setIsRegistering(false);
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    toast({ title: "Erro no registro", description: extractErrorMessage(errorData, "Não foi possível criar a conta."), variant: "destructive" });
                }
            } else {
                const formData = new URLSearchParams();
                formData.append("username", trimmedEmail);
                formData.append("password", password);

                const response = await fetch(`${API_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData.toString(),
                });

                if (response.ok) {
                    const data = await response.json();
                    login(data.access_token, data.refresh_token);
                    toast({ title: "Login realizado com sucesso", description: "Bem-vindo de volta!" });
                    navigate("/");
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    toast({ title: "Erro no login", description: extractErrorMessage(errorData, "Credenciais inválidas."), variant: "destructive" });
                }
            }
        } catch (error) {
            if (import.meta.env.DEV) console.error(error);
            toast({ title: "Erro de conexão", description: "Não foi possível se conectar ao servidor.", variant: "destructive" });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-prisma min-h-screen flex items-center justify-center p-4">
            <Card className="w-full max-w-md shadow-lg border-primary/20 bg-card/50 backdrop-blur-xl">
                <CardHeader className="space-y-1">
                    <div className="prisma-mark mx-auto mb-3"><Sparkles className="h-5 w-5" /></div>
                    <p className="text-center text-sm font-semibold text-primary">Prisma</p>
                    <CardTitle className="text-2xl font-bold text-center tracking-tight text-primary">
                        {isRegistering ? "Vamos começar?" : "Que bom ter você de volta"}
                    </CardTitle>
                    <CardDescription className="text-center">
                        {isRegistering
                            ? "Crie sua conta para construir seu primeiro plano em uma conversa."
                            : "Entre para continuar sua jornada financeira."}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <label htmlFor="email" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                E-mail
                            </label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="seu@email.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                autoComplete="email"
                                className="bg-background/50"
                            />
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Senha
                            </label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Sua senha"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                autoComplete={isRegistering ? "new-password" : "current-password"}
                                className="bg-background/50"
                            />
                            {isRegistering && (
                                <p className="text-xs text-muted-foreground">
                                    Mínimo 8 caracteres, com ao menos uma letra maiúscula e um número.
                                </p>
                            )}
                        </div>
                        <Button
                            type="submit"
                            className="w-full font-bold shadow-md hover:shadow-lg transition-all"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : null}
                            {isRegistering ? "Registrar" : "Entrar"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex flex-col space-y-4 border-t border-primary/10 pt-4 mt-2">
                    <p className="text-sm text-center text-muted-foreground">
                        {isRegistering ? "Já possui uma conta?" : "Ainda não tem cadastro?"}{" "}
                        <button
                            type="button"
                            aria-label={isRegistering ? "Ir para o login" : "Criar uma nova conta"}
                            className="text-primary hover:underline font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded"
                            onClick={() => setIsRegistering(!isRegistering)}
                        >
                            {isRegistering ? "Fazer Login" : "Criar uma agora"}
                        </button>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
