# 🤖 Robo-Advisor

Um sistema inteligente de recomendação de investimentos e planejamento financeiro que personaliza alocações de carteira e traça rotas para alcançar seus objetivos financeiros. O Robo-Advisor automatiza a análise de risco, fornece simulações de crescimento patrimonial e calcula aportes necessários para suas metas.

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
- **Planejamento de Metas**: 
    - **Cálculo de Aporte**: Descubra quanto investir mensalmente para atingir seu objetivo.
    - **Cálculo de Prazo**: Saiba quanto tempo levará para alcançar sua meta com seu aporte atual.
    - **Análise de Viabilidade**: Verifique se sua meta é realista com os parâmetros atuais.
- **Simulação de Crescimento**: Projeta o patrimônio futuro com base em aportes mensais e retornos esperados (Juros Compostos)
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
- **Python 3.10+**
- **FastAPI** (framework web de alta performance)
- **Uvicorn** (servidor ASGI)
- **Pydantic** (validação de dados robusta)

## 📦 Pré-requisitos

- Node.js 16+ e npm/bun
- Python 3.10+
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
venv\Scripts\activate # ou source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
A API estará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

### Executar o Frontend
```bash
cd frontend
npm run dev
# ou
bun run dev
```
O frontend estará disponível em `http://localhost:8080` (ou porta configurada pelo Vite).

### Acessar a Aplicação
1. Abra o navegador e vá para `http://localhost:8080`
2. Defina suas **Metas Financeiras** ou faça o **Questionário de Perfil**
3. Visualize sua carteira recomendada e o plano para atingir seus objetivos

## 📁 Estrutura do Projeto

```
Robo-Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Aplicação principal + Configuração de Rotas
│   │   ├── core/
│   │   │   └── config.py          # Configurações do ambiente
│   │   ├── models/
│   │   │   ├── perfil.py          # Modelo do perfil do investidor
│   │   │   ├── meta.py            # Modelo de metas financeiras
│   │   │   └── simulacao.py       # Modelo de simulação
│   │   ├── routes/
│   │   │   ├── planejamento.py    # Endpoint de planejamento (perfil + carteira)
│   │   │   ├── meta.py            # Endpoint de metas (aporte vs prazo)
│   │   │   ├── recomendacao.py    # Endpoint isolado de recomendação
│   │   │   └── simulacao.py       # Endpoint isolado de simulação
│   │   └── services/
│   │       ├── suitability.py     # Lógica de classificação de perfil
│   │       ├── recomendador.py    # Lógica de alocação de ativos
│   │       ├── simulador.py       # Motor de juros compostos
│   │       └── planejador.py      # Motor de busca binária para metas
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/           # Componentes React modularizados
│   │   ├── pages/                # Páginas da aplicação
│   │   ├── types/                # Definições de tipos TypeScript
│   │   ├── hooks/                # Hooks customizados
│   │   └── lib/                  # Utilitários
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
└── README.md
```

## 🔌 API Endpoints Principais

### POST `/planejamento`
Gera um planejamento financeiro completo com classificação de risco e carteira sugerida.

**Request:**
```json
{
  "idade": 30,
  "renda_mensal": 8000,
  "patrimonio_atual": 150000,
  "aporte_mensal": 2000,
  "prazo_anos": 15,
  "objetivo": "crescimento",
  "risco": 3
}
```

### POST `/meta`
Calcula o caminho para atingir um objetivo específico. O sistema inteligentemente decide o que calcular:
- Se faltar `aporte_mensal` -> Calcula quanto você precisa investir.
- Se faltar `prazo_desejado` -> Calcula quando você atingirá a meta.
- Se tiver ambos -> Valida se a meta é viável.

**Request (Exemplo: Calculando Aporte Necessário):**
```json
{
  "valor_alvo": 1000000,
  "patrimonio_atual": 50000,
  "prazo_desejado": 20,
  "objetivo": "aposentadoria"
}
```

**Response:**
```json
{
  "modo": "calcular_aporte",
  "aporte_mensal": 1850.50,
  "simulacao": { ... },
  "meta_atingida": true
}
```

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

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido como um sistema de planejamento financeiro inteligente e moderno.

---

**Nota**: Este é um sistema educacional para fins de demonstração. Não é um conselho financeiro profissional.
