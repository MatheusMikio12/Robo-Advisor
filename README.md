# 🤖 Robo-Advisor

Um sistema inteligente de recomendação de investimentos e planejamento financeiro que personaliza alocações de carteira e traça rotas para alcançar seus objetivos financeiros. O Robo-Advisor automatiza a análise de risco, fornece simulações de crescimento patrimonial e calcula aportes necessários para suas metas.

> ⚠️ Projeto acadêmico (FIAP). Sistema educacional para fins de demonstração — **não é** conselho financeiro profissional.

## 📋 Sumário
- [Características](#-características)
- [Stack Tecnológico](#️-stack-tecnológico)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Testes](#-testes)
- [Docker](#-docker)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [API Endpoints](#-api-endpoints)
- [Perfis de Risco](#-perfis-de-risco)

## ✨ Características

- **Autenticação JWT**: Registro e login com tokens de acesso e *refresh*, com rotação e revogação (logout).
- **Questionário Inteligente**: Coleta informações do investidor (idade, renda, patrimônio, prazo, objetivo).
- **Classificação de Perfil (Suitability)**: Determina automaticamente o perfil de risco (Conservador, Moderado, Arrojado) e persiste por usuário.
- **Recomendação de Carteira**: Aloca investimentos em Ações, ETFs, Renda Fixa e FIIs conforme o perfil.
- **Planejamento de Metas**:
    - **Cálculo de Aporte**: Descubra quanto investir mensalmente para atingir seu objetivo.
    - **Cálculo de Prazo**: Saiba quanto tempo levará para alcançar sua meta com seu aporte atual.
    - **Análise de Viabilidade**: Verifique se sua meta é realista com os parâmetros atuais.
- **Simulação de Crescimento**: Projeta o patrimônio futuro com juros compostos e calcula o CAGR (taxa de retorno anual da carteira).
- **Interface Moderna**: Dashboard responsivo com gráficos de evolução e resumo financeiro.

## 🛠️ Stack Tecnológico

### Frontend
- **React 18** + TypeScript
- **Vite** (build tool)
- **Tailwind CSS** + **shadcn/ui** (componentes acessíveis)
- **Recharts** (gráficos)
- **React Hook Form** + **Zod** (formulários e validação)
- **TanStack Query** (estado de servidor)

### Backend
- **Python 3.10+**
- **FastAPI** + **Uvicorn** (API ASGI de alta performance)
- **SQLAlchemy** + **SQLite** (dev) / **PostgreSQL** (prod)
- **PyJWT** (tokens JWT) + **passlib[bcrypt]** (hash de senhas)
- **slowapi** (rate limiting)
- **Pydantic** + **pydantic-settings** (validação e configuração)
- **pytest** (testes)

## 📦 Pré-requisitos

- Node.js 16+ e npm
- Python 3.10+
- Git
- (Opcional) Docker + Docker Compose

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/Robo-Advisor.git
cd Robo-Advisor
```

### 2. Configure o Backend

```bash
cd backend
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # edite SECRET_KEY se desejar
```

### 3. Configure o Frontend

```bash
cd frontend
npm install
```

## 🎯 Como Usar

### Executar o Backend
```bash
cd backend
# Ative o ambiente virtual se ainda não estiver ativo
.\venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate          # macOS/Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
A API estará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

### Executar o Frontend
```bash
cd frontend
npm run dev
```
O frontend estará disponível em `http://localhost:5173`.

### Acessar a Aplicação
1. Abra o navegador em `http://localhost:5173`.
2. **Crie uma conta** e faça login (a senha exige mínimo de 8 caracteres, com ao menos uma maiúscula e um número), ou use o **login de admin** criado automaticamente: `admin@admin.com` / `Admin@123`.
3. Defina suas **Metas Financeiras** ou responda o **Questionário de Perfil**.
4. Visualize sua carteira recomendada e o plano para atingir seus objetivos.

## 🔐 Variáveis de Ambiente

### Backend (`backend/.env`)
| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DEBUG` | `True` | Modo dev — gera `SECRET_KEY` automaticamente. Use `False` em produção. |
| `SECRET_KEY` | *(auto em dev)* | **Obrigatória em produção.** Gere com `python -c "import secrets; print(secrets.token_urlsafe(32))"`. |
| `DATABASE_URL` | `sqlite:///./sql_app.db` | Conexão com o banco. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Expiração do access token (refresh token expira em 7 dias). |
| `ADMIN_EMAIL` | `admin@admin.com` | E-mail do admin criado automaticamente no startup. |
| `ADMIN_PASSWORD` | `Admin@123` | Senha do admin (≥8 chars, 1 maiúscula, 1 número). |
| `API_HOST` | `0.0.0.0` | Host do servidor. |
| `API_PORT` | `8000` | Porta do servidor. |

### Frontend (`frontend/.env`)
| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `VITE_API_URL` | `http://localhost:8000` | URL base da API. Obrigatória no build de produção. |

## 🧪 Testes

```bash
cd backend
.\venv\Scripts\Activate.ps1        # Windows  (ou: source venv/bin/activate)
pytest tests/ -v
```

Suítes de teste:
- `test_planejador.py` — CRUD e cálculos de metas
- `test_simulador.py` — motor de juros compostos e CAGR
- `test_suitability.py` — classificação de perfil de risco
- `test_routes.py` — testes de integração HTTP (auth, planejamento, simulação, recomendação, suitability)

```bash
# Checagem de tipos e lint no frontend
cd frontend
npx tsc --noEmit
npm run lint
```

## 🐳 Docker

Forma recomendada para subir tudo de uma vez:

```bash
# Defina a SECRET_KEY (obrigatória — não há fallback inseguro)
# PowerShell:
$env:SECRET_KEY = "sua-chave-secreta"
# bash:
# export SECRET_KEY="sua-chave-secreta"

docker-compose up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

Para deploy remoto, sobrescreva a URL da API no build do frontend:
```bash
VITE_API_URL=https://api.seu-dominio.com docker-compose up --build
```

## 📁 Estrutura do Projeto

```
Robo-Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # App principal, CORS, rate limiter, rotas
│   │   ├── database.py             # Engine + SessionLocal + Base
│   │   ├── auth/
│   │   │   ├── models/user.py      # Model User + schemas (Pydantic)
│   │   │   ├── routes/auth.py      # /register, /login, /refresh, /logout, /me
│   │   │   └── services/auth_service.py  # JWT (PyJWT), hash, revogação
│   │   ├── core/
│   │   │   ├── config.py           # Configurações via pydantic-settings
│   │   │   ├── dependencies.py     # get_current_user
│   │   │   └── limiter.py          # Rate limiter (slowapi) compartilhado
│   │   ├── models/
│   │   │   ├── perfil.py           # Perfil do investidor
│   │   │   ├── meta.py             # Metas financeiras
│   │   │   ├── simulacao.py        # Simulação
│   │   │   ├── suitability_db.py   # Perfil persistido (SQLAlchemy)
│   │   │   └── revoked_token.py    # Blocklist de refresh tokens
│   │   ├── routes/
│   │   │   ├── planejamento.py     # Planejamento completo (perfil + carteira)
│   │   │   ├── meta.py             # Metas (aporte vs prazo)
│   │   │   ├── recomendacao.py     # Recomendação isolada
│   │   │   ├── simulacao.py        # Simulação isolada
│   │   │   └── suitability.py      # Persistência de perfil de risco
│   │   └── services/
│   │       ├── suitability.py      # Classificação de perfil
│   │       ├── recomendador.py     # Alocação de ativos
│   │       ├── simulador.py        # Motor de juros compostos + CAGR
│   │       └── planejador.py       # Busca binária para metas
│   ├── tests/                      # pytest
│   ├── Dockerfile
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Componentes React (shadcn/ui + custom)
│   │   ├── pages/                  # Páginas roteadas
│   │   ├── contexts/               # AuthContext (sessão JWT)
│   │   ├── hooks/                  # Hooks customizados
│   │   ├── utils/api.ts            # Wrapper de fetch com timeout
│   │   └── config.ts              # API_URL (VITE_API_URL)
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml
├── PRD.md
└── README.md
```

## 🔌 API Endpoints

> Documentação interativa completa em `http://localhost:8000/docs` (Swagger UI).

### Autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/register` | Cria conta (senha: ≥8 chars, 1 maiúscula, 1 número). |
| `POST` | `/auth/login` | Login (form-urlencoded) → retorna `access_token` + `refresh_token`. |
| `POST` | `/auth/refresh` | Renova a sessão (com rotação do refresh token). |
| `POST` | `/auth/logout` | Revoga o refresh token (blocklist). |
| `GET`  | `/auth/me` | Dados do usuário autenticado. |

As rotas de negócio exigem o header `Authorization: Bearer <access_token>`.

### Planejamento — `POST /planejamento`
Gera um planejamento financeiro completo com classificação de risco e carteira sugerida.

**Request:**
```json
{
  "idade": 30,
  "renda_mensal": 8000,
  "patrimonio_atual": 150000,
  "aporte_mensal": 2000,
  "prazo_anos": 15,
  "objetivo": "crescimento"
}
```

### Metas — `POST /meta`
Calcula o caminho para um objetivo. O sistema decide o que calcular:
- Sem `aporte_mensal` → calcula quanto investir.
- Sem `prazo_desejado` → calcula quando a meta será atingida.
- Com ambos → valida a viabilidade.

### Outros endpoints
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/recomendacao` | Recomendação de carteira por perfil. |
| `POST` | `/simulacao` | Simula a evolução de uma carteira (percentuais devem somar 100%). |
| `POST` | `/suitability` | Classifica e persiste o perfil de risco do usuário. |
| `GET`  | `/suitability/me` | Retorna o perfil de risco salvo. |
| `GET`  | `/meta` | Dados de referência. |

## 🎓 Perfis de Risco

### Conservador
- **Foco**: Preservação de capital e segurança.
- **Alocação**: 70% Renda Fixa, 15% ETFs, 5% Ações, 10% FIIs.

### Moderado
- **Foco**: Equilíbrio entre segurança e crescimento.
- **Alocação**: 45% Renda Fixa, 30% ETFs, 15% Ações, 10% FIIs.

### Arrojado
- **Foco**: Maximização de retorno no longo prazo.
- **Alocação**: 25% Renda Fixa, 40% ETFs, 25% Ações, 10% FIIs.

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou um pull request.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT — veja o arquivo LICENSE para detalhes.

---

**Nota**: Este é um sistema educacional para fins de demonstração. Não é um conselho financeiro profissional.
