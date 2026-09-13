import React, { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from "react";
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
    login: (accessToken: string, refreshToken: string) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEYS = {
    access: "token",
    refresh: "refresh_token",
} as const;

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem(STORAGE_KEYS.access));
    const [isLoading, setIsLoading] = useState(true);
    const { toast } = useToast();
    const verifiedToken = useRef<string | null>(null);

    const logout = useCallback(() => {
        // Revoga o refresh token no servidor (best-effort — não bloqueia o logout local)
        const refreshToken = localStorage.getItem(STORAGE_KEYS.refresh);
        if (refreshToken) {
            fetch(`${API_URL}/auth/logout`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: refreshToken }),
            }).catch(() => {
                /* falha de rede não impede o logout local */
            });
        }
        localStorage.removeItem(STORAGE_KEYS.access);
        localStorage.removeItem(STORAGE_KEYS.refresh);
        setToken(null);
        setUser(null);
        verifiedToken.current = null;
    }, []);

    const tryRefresh = useCallback(async (): Promise<string | null> => {
        const refreshToken = localStorage.getItem(STORAGE_KEYS.refresh);
        if (!refreshToken) return null;

        try {
            const response = await fetch(`${API_URL}/auth/refresh`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (!response.ok) return null;

            const data = await response.json();
            localStorage.setItem(STORAGE_KEYS.access, data.access_token);
            localStorage.setItem(STORAGE_KEYS.refresh, data.refresh_token);
            setToken(data.access_token);
            return data.access_token;
        } catch {
            return null;
        }
    }, []);

    const fetchMe = useCallback(async (currentToken: string) => {
        try {
            const response = await fetch(`${API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${currentToken}` },
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
                return;
            }

            if (response.status === 401) {
                const newToken = await tryRefresh();
                if (newToken) {
                    const retryResponse = await fetch(`${API_URL}/auth/me`, {
                        headers: { Authorization: `Bearer ${newToken}` },
                    });
                    if (retryResponse.ok) {
                        setUser(await retryResponse.json());
                        return;
                    }
                }
            }

            logout();
            toast({
                title: "Sessão expirada",
                description: "Por favor, faça login novamente.",
                variant: "destructive",
            });
        } catch {
            logout();
        } finally {
            setIsLoading(false);
        }
    }, [logout, toast, tryRefresh]);

    useEffect(() => {
        if (token) {
            if (verifiedToken.current === token) return;
            localStorage.setItem(STORAGE_KEYS.access, token);
            fetchMe(token);
        } else {
            logout();
            setIsLoading(false);
        }
    }, [token, fetchMe, logout]);

    const login = async (accessToken: string, refreshToken: string) => {
        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/auth/me`, {headers:{Authorization:`Bearer ${accessToken}`}});
            if(!response.ok) throw new Error("Não foi possível validar a sessão.");
            const authenticatedUser = await response.json();
            verifiedToken.current = accessToken;
            localStorage.setItem(STORAGE_KEYS.access, accessToken);
            localStorage.setItem(STORAGE_KEYS.refresh, refreshToken);
            setUser(authenticatedUser);
            setToken(accessToken);
        } finally {setIsLoading(false);}
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
