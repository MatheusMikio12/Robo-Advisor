import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";
import { API_URL } from "@/config";

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
        try {
            if (isRegistering) {
                // Register API Call
                const response = await fetch(`${API_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password }),
                });

                if (response.ok) {
                    toast({ title: "Conta criada com sucesso", description: "Faça login com suas novas credenciais." });
                    setIsRegistering(false);
                } else {
                    const errorData = await response.json();
                    toast({ title: "Erro no registro", description: errorData.detail || "Não foi possível criar a conta.", variant: "destructive" });
                }
            } else {
                // Login API Call
                const formData = new URLSearchParams();
                formData.append("username", email);
                formData.append("password", password);

                const response = await fetch(`${API_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData.toString(),
                });

                if (response.ok) {
                    const data = await response.json();
                    login(data.access_token);
                    toast({ title: "Login realizado com sucesso", description: "Bem-vindo de volta!" });
                    navigate("/");
                } else {
                    const errorData = await response.json();
                    toast({ title: "Erro no login", description: errorData.detail || "Credenciais inválidas.", variant: "destructive" });
                }
            }
        } catch (error) {
            console.error(error);
            toast({ title: "Erro de conexão", description: "Não foi possível se conectar ao servidor.", variant: "destructive" });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <Card className="w-full max-w-md shadow-lg border-primary/20 bg-card/50 backdrop-blur-xl">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center tracking-tight text-primary">
                        {isRegistering ? "Criar Conta" : "Entrar"}
                    </CardTitle>
                    <CardDescription className="text-center">
                        {isRegistering
                            ? "Registre-se para salvar seus planejamentos."
                            : "Entre para acessar sua área de planejamento."}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                E-mail
                            </label>
                            <Input
                                type="email"
                                placeholder="seu@email.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="bg-background/50"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Senha
                            </label>
                            <Input
                                type="password"
                                placeholder="Sua senha"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="bg-background/50"
                            />
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
                            className="text-primary hover:underline font-medium focus:outline-none"
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
