# PRD — Robo-Advisor

**Versão:** 2.0  
**Data:** 2026-05-31  
**Projeto:** Trabalho Acadêmico FIAP  
**Equipe:** MatheusMikio12

---

## 1. Problema

Investidores individuais, especialmente iniciantes, não sabem como alocar seu capital de forma eficiente. Faltam ferramentas acessíveis que:
- Identifiquem o perfil de risco do investidor (suitability)
- Traduzam metas financeiras em planos de aporte concretos
- Projetem cenários de rentabilidade de forma transparente

---

## 2. Proposta de Valor

Um assistente financeiro automatizado (Robo-Advisor) que, a partir do perfil e das metas do usuário, recomenda uma carteira de investimentos e simula o crescimento do patrimônio ao longo do tempo.

---

## 3. Usuários-alvo

| Perfil | Descrição |
|--------|-----------|
| Investidor iniciante | Pouco conhecimento de mercado, quer começar a investir com segurança |
| Investidor intermediário | Já investe, quer otimizar alocação baseado em metas específicas |
| Estudante de finanças | Quer explorar simulações e cenários didaticamente |

---

## 4. Status das Funcionalidades

### 4.1 Autenticação ✅ Completo
- Registro e login com JWT (access token 30 min + refresh token 7 dias)
- `POST /auth/refresh` — renova access token sem novo login, stateless
- `GET /auth/me` — retorna usuário autenticado
- Senhas hashed com bcrypt; stack trace nunca exposto ao cliente

### 4.2 Suitability (Perfil de Risco) ✅ Completo
- Classificação por score em: **Conservador**, **Moderado**, **Arrojado**
- `POST /suitability` — classifica e persiste perfil por usuário (upsert)
- `GET /suitability/me` — retorna perfil salvo do usuário autenticado
- 8 testes unitários + 5 testes de integração cobrindo todos os casos

### 4.3 Planejamento Financeiro ✅ Completo
- `POST /planejamento` — orquestra suitability + recomendação + simulação em uma chamada
- Retorna: perfil classificado, carteira recomendada, resumo financeiro, evolução anual
- Cálculo on-demand; persistência de histórico é escopo v2

### 4.4 Recomendação de Carteira ✅ Completo
- `POST /recomendacao` — aceita `PerfilInvestidor`, retorna carteira + explicação textual
- 3 alocações distintas (Conservador / Moderado / Arrojado), percentuais sempre somam 100%
- Ativos: Renda Fixa, ETFs, Ações, FIIs com descrições para o usuário

### 4.5 Simulação Financeira ✅ Completo
- `POST /simulacao` — juros compostos com aporte mensal (taxa anual → mensal corretamente)
- Validação: percentuais da carteira devem somar 100% (retorna 422 se inválido)
- Output: `valor_final`, `total_investido`, `retorno_absoluto`, `retorno_percentual`, `cagr`, `evolucao` (snapshots anuais)

### 4.6 Metas Financeiras ✅ Completo
- `POST /meta` — calcula aporte necessário (dado prazo) ou prazo necessário (dado aporte)
- Retorna: progresso atual, viabilidade, simulação mês a mês, mensagem contextual

### 4.7 Dashboard (Frontend) ✅ Completo
- Login e registro com feedback de erro por toast
- Formulário de perfil do investidor → chama `POST /planejamento`
- Resultado animado: perfil de risco, cards de carteira, resumo financeiro, gráfico de evolução
- Skeleton loading durante chamadas de API
- Botão "Nova Análise" limpa resultado sem apagar o formulário
- GoalTracker: tabs calcular-aporte / calcular-prazo, gráfico com linha de meta
- Empty state no gráfico quando sem dados

---

## 5. Fluxo Principal

```
[Usuário] → Registro / Login
    → Frontend armazena access_token + refresh_token
    → Preenche perfil (idade, renda, patrimônio, aporte, prazo, objetivo)
    → POST /planejamento  ← ponto de entrada principal
        ├── Classifica perfil (Conservador / Moderado / Arrojado)
        ├── Gera carteira recomendada
        └── Simula crescimento patrimonial
    → Visualiza resultados no Dashboard
    → (Opcional) Usa GoalTracker para simular metas específicas
    → (Opcional) POST /suitability para persistir perfil de risco
```

---

## 6. Requisitos Não-Funcionais

| Requisito | Meta | Status |
|-----------|------|--------|
| Segurança | Bcrypt, JWT assinado, sem stack trace exposto, rate limiting | ✅ |
| Performance | Respostas < 200ms para endpoints sem cálculo pesado | ✅ |
| Portabilidade | Rodável com `docker-compose up --build` | ✅ |
| Testabilidade | Cobertura de testes para lógica de negócio e rotas HTTP | ✅ 62 testes |
| Configurabilidade | Toda configuração via variáveis de ambiente (12-factor app) | ✅ |
| Confiabilidade frontend | Timeout em requisições, refresh automático de token | ✅ |

---

## 7. Infraestrutura

| Componente | Detalhe |
|-----------|---------|
| `docker-compose.yml` | Backend `:8000` + Frontend `:5173`; SQLite em volume isolado `/data` |
| `backend/Dockerfile` | `python:3.11-slim` + uvicorn |
| `frontend/Dockerfile` | Build multi-stage: `node:20` → `nginx:alpine` |
| `frontend/nginx.conf` | SPA routing + cache de assets com hash |
| Rate limiting | `slowapi` — 60 req/min por IP (global) |

---

## 8. Cobertura de Testes

| Suite | Quantidade | Cobertura |
|-------|-----------|-----------|
| `test_planejador.py` | 16 testes | Cálculo de aporte, prazo e viabilidade |
| `test_simulador.py` | 11 testes | Juros compostos, CAGR, divisão por zero |
| `test_suitability.py` | 8 testes | Classificação de perfil, fronteiras |
| `test_routes.py` | 27 testes | Auth, Planejamento, Simulação, Recomendação, Suitability, Refresh token |
| **Total** | **62 testes** | **0 falhas** |

---

## 9. Critérios de Aceitação

### Auth
- [x] Usuário consegue se registrar e receber token JWT
- [x] Endpoints protegidos retornam 401 sem token válido
- [x] Token expira conforme configurado
- [x] Refresh token renova sessão sem novo login

### Suitability
- [x] Classifica corretamente nos 3 perfis
- [x] Perfil persiste por usuário e pode ser consultado via `GET /suitability/me`

### Planejamento
- [x] Planejamento completo retornado em uma única chamada autenticada

### Recomendação
- [x] Retorna carteira diferente para cada perfil de risco
- [x] Percentuais somam 100%

### Simulação
- [x] Cálculo de juros compostos com aporte mensal está correto
- [x] Retorna série temporal anual para plotagem
- [x] Rejeita carteira com percentuais que não somam 100%

### Frontend
- [x] Login e registro funcionam end-to-end com feedback de erro
- [x] Dashboard exibe gráfico de evolução patrimonial
- [x] Skeleton loading durante chamadas de API
- [x] Token refresh automático — sessão não expira silenciosamente
- [x] GoalTracker com dois modos (calcular aporte / calcular prazo)

---

## 10. Fora do Escopo (v1.0)

- Integração com corretoras reais ou dados de mercado ao vivo
- Pagamentos ou cobranças
- Notificações push ou e-mail
- App mobile nativo
- Multi-tenancy / múltiplos administradores
- Histórico persistido de planejamentos por usuário

---

## 11. Backlog v2.0

| # | Item | Prioridade | Detalhe |
|---|------|-----------|---------|
| 1 | Migrar para PostgreSQL + Alembic | Alta | SQLite não suporta concorrência em produção |
| 2 | Histórico de planejamentos | Média | Salvar cada `POST /planejamento` para comparação temporal |
| 3 | Testes no frontend (Vitest) | Média | Cobertura das páginas Login e Index |
| 4 | Acessibilidade (WCAG) | Média | `aria-live` em loading, `aria-label` em botões de toggle |
| 5 | Extrair tooltip de gráfico | Baixa | 2 cópias ainda em GoalTracker — refatorar para utilitário |
| 6 | Cache de recomendações | Baixa | Resultado determinístico por perfil — TTL longo |
| 7 | CAGR exato via XIRR | Baixa | Atual usa `total_investido` como proxy — aceitável para MVP acadêmico |

---

## 12. Decisões de Implementação

| Decisão | Motivo |
|---------|--------|
| `POST /planejamento` orquestra tudo em uma chamada | Reduz round-trips do frontend; UX mais fluida |
| Refresh token stateless (JWT com claim `type: refresh`) | Sem armazenamento em banco; suficiente para MVP |
| Snapshots anuais na simulação, não mensais | Otimização de payload — gráficos de longo prazo não precisam de granularidade mensal |
| SQLite em dev, PostgreSQL em prod via `DATABASE_URL` | Zero-config local; troca sem alterar código |
| `SECRET_KEY` auto-gerada em `DEBUG=True` | Reduz atrito de setup em dev; tokens invalidam no restart (documentado) |
| `apiFetch` com `AbortController` (10s timeout) | Evita requisições penduradas sem feedback ao usuário |
| `ResultsSkeleton` em vez de spinner global | UX mais clara — usuário vê a estrutura do resultado antes de carregar |
