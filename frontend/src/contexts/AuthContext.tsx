import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useToast } from "@/hooks/use-toast";
import { API_URL } from "@/config";

interface User {
    id: number;
    email: string;
    is_active: boolean;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
    const [isLoading, setIsLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        if (token) {
            localStorage.setItem("token", token);
            fetchMe(token);
        } else {
            localStorage.removeItem("token");
            setUser(null);
            setIsLoading(false);
        }
    }, [token]);

    const fetchMe = async (currentToken: string) => {
        try {
            const response = await fetch(`${API_URL}/auth/me`, {
                headers: {
                    Authorization: `Bearer ${currentToken}`,
                },
            });
            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
            } else {
                logout();
                toast({
                    title: "Sessão expirada",
                    description: "Por favor, faça login novamente.",
                    variant: "destructive",
                });
            }
        } catch (error) {
            console.error("Erro ao buscar usuário:", error);
            logout();
        } finally {
            setIsLoading(false);
        }
    };

    const login = (newToken: string) => {
        setToken(newToken);
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
