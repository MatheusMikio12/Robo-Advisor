# Executar e verificar o Prisma

## Windows

O ambiente antigo `backend/venv` foi preservado. O novo ambiente está em
`backend/.venv`, com Python 3.12 e as dependências de desenvolvimento.

Em dois terminais na raiz do projeto:

```powershell
.\scripts\start-prisma.ps1 -BackendOnly
.\scripts\start-prisma.ps1 -FrontendOnly
```

Frontend: http://localhost:8080. API: http://localhost:8000/docs.
Se já estiverem rodando, não inicie outra cópia na mesma porta.

Para preparar outra máquina com Python instalado:

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
```

Copie `backend/.env.example` para `backend/.env` e configure `DEBUG=True`.
Mantenha uma `SECRET_KEY` fixa se usar MFA. Em desenvolvimento, a ausência da
chave invalida tokens e impede decifrar os segredos MFA após reiniciar.
Nunca use a chave de CI em produção.
Nesta instalação, uma chave local persistente foi configurada no `.env`
ignorado pelo Git. O valor não é exibido na interface nem na documentação.

## Fluxo funcional

1. Entre ou crie uma conta. O acesso padrão aparece apenas no frontend de desenvolvimento.
2. Complete Diagnóstico. Respostas intermediárias são salvas como rascunho no servidor.
3. Em Carteira, sincronize Tesouro/CVM e gere uma análise.
4. Abra cada produto para consultar motivos, alternativas, fonte, data e riscos.
5. Crie metas e compare dois cenários. Registre aportes realizados.
6. Cadastre posições e importe extratos com prévia em Minha vida financeira.
7. Converse sobre reserva, dívidas, carteira ou metas.

## LLM local opcional

Instale/execute o Ollama, baixe o modelo e configure o backend:

```text
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Nesta versão o modelo classifica o assunto da mensagem. Respostas financeiras
usam ferramentas determinísticas e contexto salvo. Se Ollama falhar ou retornar
JSON inválido, o roteador por palavras-chave continua atendendo. Não é ainda
um agente CFP de conversa livre, pesquisa e execução de ferramentas arbitrárias.

## Fontes reais

- Tesouro Transparente: importa a última data do CSV oficial. Não é cotação executável.
- CVM: importa identificação e situação cadastral; não habilita indicação sem custos, risco e disponibilidade.
- Referências com mais de sete dias não participam de novas seleções.
- B3, corretoras e Open Finance não estão conectados. Exigem contrato/credenciais de parceiro.
- Não há taxas, ofertas ou produtos de demonstração misturados ao catálogo público.

Custódia e mínimo do Tesouro são referências aproximadas; confirme na instituição.
O ranking inicial usa custos, liquidez e risco. Não considera previsão de retorno
por título, tributação completa, tracking difference ou análise fundamentalista.
Posições declaradas integram o patrimônio informado e não são somadas novamente.
O limite por emissor privado considera saldo atual e dinheiro novo; Tesouro
Nacional pode ter 100%. A cobertura FGC não é presumida para produtos sem metadados.

## Simulação

Monte Carlo lognormal, semente fixa 42, 400 trajetórias por padrão. Alíquota única
aproximada sobre ganho positivo em resgates e saldo final. Retorno nominal, inflação,
volatilidade e custos são premissas do usuário, não projeções de mercado.
Valores finais e metas em poder de compra atual; aportes nominais constantes.
Não substitui cálculo fiscal por lote, IOF, come-cotas ou modelo de correlações.

## Segurança e operação

MFA TOTP opcional com segredo cifrado; redefinição de senha por token de uso único
de 30 minutos e SMTP STARTTLS. Ativação/desativação de MFA e reset invalidam sessões
anteriores. Configure SMTP_HOST/PORT/USERNAME/PASSWORD/SENDER e FRONTEND_URL.
Sem SMTP, o botão informa indisponibilidade; não revela tokens na tela ou em logs.

Produção não cria usuário administrador padrão nem tabelas automaticamente.
Execute `alembic upgrade head`; a migração inicial preserva tabelas preexistentes.
Antes de migrar uma instalação relevante, faça backup do SQLite ou `pg_dump`.
A migração inicial não permite downgrade destrutivo: use backup para reversão.
PostgreSQL pode ser iniciado com `docker compose -f docker-compose.postgres.yml up --build`
após configurar SECRET_KEY e POSTGRES_PASSWORD. Isso não migra dados do SQLite.

Saúde: `/` e `/health/ready`. Auditoria por usuário: `/wealth/audit`.
Logs de requisição contêm ID, método, status e duração, sem corpo ou credenciais.
Defina retenção, backup e alertas do provedor antes do deploy público.

## Verificação

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m alembic check
cd ../frontend
npx tsc -p tsconfig.app.json --noEmit
npm run lint
npm run build
npx playwright install chromium
npm run test:e2e
```

CI inclui migração, teste de schema, testes de backend, tipos, lint e build.
O E2E usa as portas 8002/8082 e `backend/prisma-e2e.db`, sem tocar nos dados
da aplicação principal. A conta `prisma.qa.20260913@example.com` foi criada
na base local apenas para a verificação visual manual; não altera seu cadastro.
Capturas de teste ficam em `frontend/test-results` e não são versionadas.
