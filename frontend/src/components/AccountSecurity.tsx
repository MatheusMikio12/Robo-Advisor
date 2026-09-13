import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiFetch, authHeaders } from "@/utils/api";
import { API_URL } from "@/config";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function AccountSecurity() {
  const {token,logout} = useAuth();
  const [mfa,setMfa] = useState(false);
  const [secret,setSecret] = useState("");
  const [password,setPassword] = useState("");
  const [code,setCode] = useState("");
  const [error,setError] = useState("");
  const [busy,setBusy] = useState(false);
  useEffect(() => {apiFetch<{mfa:boolean}>(`${API_URL}/auth/security`,{headers:authHeaders(token)}).then(r => setMfa(r.mfa)).catch(e => setError(e.message));},[token]);
  const action = async (name: string) => {setBusy(true);setError("");try {const r = await apiFetch<{secret?:string}>(`${API_URL}/auth/mfa/${name}`,{method:"POST",headers:authHeaders(token),body:JSON.stringify({password,code})}); if(r.secret) setSecret(r.secret); else logout();} catch(e) {setError(e instanceof Error ? e.message : "Não foi possível atualizar a segurança.");} finally {setBusy(false);}};
  return <section className="wealth-panel max-w-xl"><h2 className="text-2xl font-semibold">Proteja sua conta</h2><p className="mt-3">Autenticação em duas etapas: {mfa ? "ativa" : "desativada"}.</p><p className="text-sm text-muted-foreground mt-2">Use um aplicativo autenticador. Alterar esta configuração encerra suas sessões.</p>
    <form className="space-y-4 mt-5" onSubmit={e => {e.preventDefault();void action(mfa ? "disable" : secret ? "enable" : "setup");}}>
      <label className="block">Senha atual<Input required type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)}/></label>
      {secret && <div className="wealth-notice"><p>Adicione esta chave ao autenticador e confirme o código gerado:</p><code className="break-all select-all">{secret}</code></div>}
      {(mfa || secret) && <label className="block">Código do autenticador<Input required inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} value={code} onChange={e => setCode(e.target.value)}/></label>}
      {error && <p role="alert" className="text-destructive">{error}</p>}
      <Button disabled={busy} type="submit">{mfa ? "Desativar e sair" : secret ? "Confirmar e ativar" : "Configurar duas etapas"}</Button>
    </form>
  </section>;
}
