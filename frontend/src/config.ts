/**
 * Configuração centralizada do frontend.
 * Todas as constantes de configuração devem ser importadas daqui.
 */

const apiUrl = import.meta.env.VITE_API_URL as string | undefined;

// Em produção, VITE_API_URL é obrigatória — falha explícita é melhor que silenciosamente
// apontar para localhost (que não existe em produção).
if (!apiUrl && import.meta.env.PROD) {
  throw new Error(
    "VITE_API_URL não está definida. Configure a variável de ambiente antes do build de produção. " +
    "Consulte frontend/.env.example para referência."
  );
}

export const API_URL: string = apiUrl ?? "http://localhost:8000";
