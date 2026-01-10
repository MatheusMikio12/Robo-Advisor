# 🤖 Robo-Advisor

Um sistema inteligente de recomendação de investimentos que personaliza alocações de carteira baseado no perfil do investidor, objetivos financeiros e horizonte de tempo. O Robo-Advisor automatiza a análise de risco e fornece simulações de crescimento patrimonial.

## 📋 Sumário
- [Características](#características)
- [Stack Tecnológico](#stack-tecnológico)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)

## ✨ Características

- **Questionário Inteligente**: Coleta informações do investidor (idade, renda, patrimônio, prazo, objetivo)
- **Classificação de Perfil**: Determina automaticamente o perfil de risco (Conservador, Moderado, Arrojado)
- **Recomendação de Carteira**: Aloca investimentos em Ações, ETFs, Renda Fixa e FIIs conforme o perfil
- **Simulação de Crescimento**: Projeta o patrimônio futuro com base em aportes mensais e retornos esperados
- **Interface Moderna**: Dashboard responsivo com gráficos de evolução e resumo financeiro

## 🛠️ Stack Tecnológico

### Frontend
- **React 18** + TypeScript
- **Vite** (build tool)
- **Tailwind CSS** (styling)
- **shadcn/ui** (componentes acessíveis)
- **Lucide Icons** (ícones)
- **Recharts** (gráficos)

### Backend
- **Python 3.8+**
- **FastAPI** (framework web)
- **Uvicorn** (servidor ASGI)
- **Pydantic** (validação de dados)

## 📦 Pré-requisitos

- Node.js 16+ e npm/bun
- Python 3.8+
- Git

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
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure o Frontend

```bash
cd frontend
npm install
# ou
bun install
```

## 🎯 Como Usar

### Executar o Backend
```bash
cd backend
# Ativar ambiente virtual (se não estiver ativo)
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# Rodar servidor
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`

### Executar o Frontend
```bash
cd frontend
npm run dev
# ou
bun run dev
```

O frontend estará disponível em `http://localhost:8080` (ou porta configurada pelo Vite)

### Acessar a Aplicação
1. Abra o navegador e vá para `http://localhost:8080`
2. Preencha o formulário com suas informações
3. Clique em "Analisar Perfil"
4. Visualize sua carteira recomendada e simulação de crescimento

## 📁 Estrutura do Projeto

```
Robo-Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Aplicação principal + CORS
│   │   ├── core/
│   │   │   └── config.py          # Configurações
│   │   ├── models/
│   │   │   ├── perfil.py          # Modelo do perfil do investidor
│   │   │   └── simulacao.py       # Modelo de simulação
│   │   ├── routes/
│   │   │   ├── planejamento.py    # Endpoint de planejamento
│   │   │   ├── recomendacao.py    # Endpoint de recomendação
│   │   │   └── simulacao.py       # Endpoint de simulação
│   │   └── services/
│   │       ├── suitability.py     # Classificação de perfil de risco
│   │       ├── recomendador.py    # Geração de carteira
│   │       └── simulador.py       # Simulação de crescimento
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx                # Cabeçalho
│   │   │   ├── InvestorForm.tsx          # Formulário de entrada
│   │   │   ├── InvestorProfile.tsx       # Perfil classificado
│   │   │   ├── PortfolioCards.tsx        # Cards da carteira
│   │   │   ├── FinancialSummary.tsx      # Resumo financeiro
│   │   │   ├── EvolutionChart.tsx        # Gráfico de evolução
│   │   │   └── ui/                       # Componentes base (shadcn/ui)
│   │   ├── pages/
│   │   │   ├── Index.tsx                 # Página principal
│   │   │   └── NotFound.tsx              # 404
│   │   ├── types/
│   │   │   └── roboAdvisor.ts           # Tipos TypeScript
│   │   ├── hooks/                        # React hooks customizados
│   │   ├── lib/                          # Utilitários
│   │   ├── App.tsx                       # App root
│   │   └── main.tsx                      # Entry point
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
└── README.md
```

## 🔌 API Endpoints

### POST `/planejamento`
Gera um planejamento financeiro completo com perfil, carteira e simulação.

**Request:**
```json
{
  "idade": 35,
  "renda_mensal": 5000,
  "patrimonio_atual": 50000,
  "aporte_mensal": 1000,
  "prazo_anos": 10,
  "objetivo": "aposentadoria"
}
```

**Response:**
```json
{
  "perfil": "Moderado",
  "carteira": [
    {"ativo": "Renda Fixa", "percentual": 45},
    {"ativo": "ETFs", "percentual": 30},
    {"ativo": "Ações", "percentual": 15},
    {"ativo": "FIIs", "percentual": 10}
  ],
  "resumo": {
    "valor_final": 187500.50,
    "total_investido": 170000,
    "retorno_absoluto": 17500.50,
    "retorno_percentual": 10.29,
    "cagr": 9.75
  },
  "evolucao": [
    {"ano": 0, "valor": 50000},
    {"ano": 1, "valor": 62150},
    {"ano": 2, "valor": 75320}
  ]
}
```

## 🎓 Perfis de Risco

### Conservador
- **Alocação**: 70% Renda Fixa, 15% ETFs, 5% Ações, 10% FIIs
- **Ideal para**: Investidores com horizonte curto ou baixa tolerância ao risco

### Moderado
- **Alocação**: 45% Renda Fixa, 30% ETFs, 15% Ações, 10% FIIs
- **Ideal para**: Investidores com horizonte médio e risco equilibrado

### Arrojado
- **Alocação**: 25% Renda Fixa, 40% ETFs, 25% Ações, 10% FIIs
- **Ideal para**: Investidores com horizonte longo e alta tolerância ao risco

## 📊 Simulação de Crescimento

A simulação utiliza retornos esperados anuais:
- **Renda Fixa**: 8% a.a.
- **ETFs**: 10% a.a.
- **Ações**: 12% a.a.
- **FIIs**: 9% a.a.

O sistema computa mensalmente o crescimento de cada ativo conforme sua alocação percentual.

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou um pull request.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido como um sistema de planejamento financeiro inteligente.

---

**Nota**: Este é um sistema educacional para fins de demonstração. Não é um conselho financeiro profissional.
