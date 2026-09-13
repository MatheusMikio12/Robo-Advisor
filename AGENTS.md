# Robo-Advisor — Contexto para Codex

## Visão Geral

Aplicação de planejamento financeiro inteligente (trabalho acadêmico FIAP). Permite ao usuário definir metas financeiras, receber recomendações de investimento baseadas em perfil de risco (suitability), e simular cenários de rentabilidade.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT via `python-jose`, senhas com `passlib[bcrypt]` |
| Frontend | React 18 + TypeScript + Vite + Tailwind + shadcn/ui |
| Charts | Recharts |
| Forms | React Hook Form + Zod |
| State | TanStack Query |

## Estrutura do Projeto

```
Robo-Advisor/
├── backend/
│   ├── app/
│   │   ├── auth/routes/auth.py   # Login, registro, /me
│   │   ├── core/config.py        # Settings via pydantic-settings (.env)
│   │   ├── models/               # SQLAlchemy models
│   │   ├── routes/
│   │   │   ├── meta.py           # GET /meta — dados de referência
│   │   │   ├── planejamento.py   # CRUD de metas financeiras
│   │   │   ├── recomendacao.py   # Recomendações por perfil de risco
│   │   │   └── simulacao.py      # Simulação de aportes e retorno
│   │   ├── services/             # Lógica de negócio
│   │   └── database.py           # Engine + SessionLocal
│   ├── tests/                    # pytest
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # shadcn/ui + componentes customizados
│   │   ├── pages/                # Páginas roteadas via react-router-dom
│   │   ├── contexts/             # AuthContext, etc.
│   │   ├── hooks/                # Custom hooks
│   │   └── config.ts             # API_URL (VITE_API_URL env var)
│   └── package.json
├── docker-compose.yml
└── PRD.md
```

## Como Rodar Localmente

### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env          # edite SECRET_KEY se quiser
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Docs interativas em: http://localhost:8000/docs

### Frontend
```powershell
cd frontend
npm install
npm run dev
```
Abre em: http://localhost:5173

### Com Docker (recomendado para testes integrados)
```powershell
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Testes

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

Suítes existentes:
- `test_planejador.py` — CRUD de metas
- `test_simulador.py` — cálculos de simulação
- `test_suitability.py` — lógica de perfil de risco

## Variáveis de Ambiente

### Backend (`backend/.env`)
| Variável | Padrão | Descrição |
|---------|--------|-----------|
| `DEBUG` | `True` | Dev mode — gera SECRET_KEY automaticamente |
| `SECRET_KEY` | *(auto em dev)* | Obrigatória em produção |
| `DATABASE_URL` | `sqlite:///./sql_app.db` | Conexão com banco |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Expiração do JWT |
| `API_HOST` | `0.0.0.0` | Host do servidor |
| `API_PORT` | `8000` | Porta do servidor |

### Frontend (`frontend/.env`)
| Variável | Padrão | Descrição |
|---------|--------|-----------|
| `VITE_API_URL` | `http://localhost:8000` | URL da API |

## Decisões Arquiteturais

- **SQLite em dev** para zero-config; `.env` troca para PostgreSQL em produção sem mudar código.
- **SECRET_KEY auto-gerada** no modo DEBUG — tokens invalidados a cada restart. Intencional.
- **CORS** configurado em `core/config.py`, origens em lista. Adicionar produção via env var.
- **Global exception handler** em `main.py` retorna 500 genérico — stack trace nunca vaza para o cliente.
- **`VITE_API_URL` obrigatória em produção** — frontend lança erro explícito no build se ausente.

## Guias de Trabalho para o /loop

Quando estiver em loop de desenvolvimento, priorize nessa ordem:
1. **Bugs abertos** — ver PRD.md seção 9 🔴
2. **Testes passando** — nunca commitar com `pytest` falhando (35 testes devem passar)
3. **Segurança** — validação de input, auth em todos os endpoints protegidos
4. **Qualidade de código** — DRY, sem duplicação desnecessária

### Todos os itens do backlog concluídos ✅
- ~~#1~~ validação percentuais carteira (já existia)
- ~~#2~~ `POST /suitability` + `GET /suitability/me` — model `PerfilSalvo` + 5 testes
- ~~#3~~ `frontend/.env` criado
- ~~#4~~ rate limiting via `slowapi` — 60 req/min por IP global
- ~~#5~~ fallback simulador corrigido
- ~~#6~~ CAGR documentado como aproximação; XIRR fora do escopo MVP
- ~~#7~~ refresh token stateless — `POST /auth/refresh` (JWT 7 dias) + 4 testes de segurança
- ~~#8~~ 28 testes de integração HTTP (total: **62 testes passando**)

### Comandos úteis no loop
```powershell
# Checar tipos no frontend
cd frontend && npx tsc --noEmit

# Lint frontend
cd frontend && npm run lint

# Rodar testes backend
cd backend && .\venv\Scripts\Activate.ps1 && pytest tests/ -v

# Build de produção do frontend
cd frontend && npm run build
```
