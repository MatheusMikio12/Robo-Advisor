const DEFAULT_TIMEOUT_MS = 10_000;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Wrapper de fetch com timeout automático e extração de erro do corpo JSON.
 * Lança ApiError em respostas não-ok ou timeout; relança outros erros de rede.
 */
export async function apiFetch<T>(
  url: string,
  options: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { ...options, signal: controller.signal });

    if (!response.ok) {
      let detail = `Erro ${response.status}`;
      try {
        const body = await response.json();
        if (typeof body?.detail === "string") detail = body.detail;
        else if (Array.isArray(body?.detail)) detail = body.detail[0]?.msg ?? detail;
      } catch {
        // corpo não é JSON — mantém mensagem genérica
      }
      throw new ApiError(response.status, detail);
    }

    return response.json() as Promise<T>;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(408, "A requisição demorou demais. Verifique sua conexão e tente novamente.");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

/** Monta headers comuns: Content-Type JSON + Authorization Bearer se houver token. */
export function authHeaders(token: string | null): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}
