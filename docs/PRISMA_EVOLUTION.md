# Prisma: evolução do concierge

Escopo solicitado: diagnóstico completo, conversa persistente, metas vivas,
simulações, visão financeira, catálogo real, carteira explicável e base de produção.

## Critérios de aceite

- [x] Diagnóstico editável, rascunho persistido e isolamento por usuário.
- [x] Capacidade e tolerância distintas; reserva, dívida, liquidez e prazo limitam risco.
- [x] Conversas persistentes com roteamento entre orçamento, metas e investimentos.
- [x] Metas com prioridade, progresso, registro de aportes e cenários reproduzíveis.
- [x] Simulação com inflação, custos, tributação aproximada, Monte Carlo, pausa e retiradas.
- [x] Posições e movimentações; importação CSV/OFX com prévia e deduplicação.
- [x] Produtos com identificadores, fontes e data; referências vencidas são excluídas.
- [x] Seleção determinística inicial explicada, alternativas e rastreabilidade.
- [x] Interface responsiva com contexto, produtos e comparação de cenários.
- [x] Configuração PostgreSQL, migrações, CI, saúde e auditoria. PostgreSQL ainda não executado neste computador.
- [x] Recuperação de senha implementada (entrega depende de SMTP), MFA opcional testado.
- [x] Testes financeiros, isolamento entre contas e fluxo de interface.

## Evidências desta entrega

96 testes de backend aprovados após atualização de dependências. Teste E2E
aprovado em 22,7 segundos, cobrindo login único, retomada do rascunho, carteira,
memória de conversa, metas, cenário e viewport de 390 pixels. Build e tipos
aprovados. npm audit após atualização: zero vulnerabilidades reportadas.
Migração do SQLite local aplicada sem remover dados; alembic check sem diferenças.
Importador testado com o CSV real do Tesouro: 58 títulos de referência.
ZIP cadastral real da CVM importado: 126.796 registros processados, com deduplicação
por identificador. Cadastros incompletos permanecem inelegíveis para seleção.

## Ainda não entregue como serviço de produção

- Open Finance consentido e execução/ordens: exigem parceiro, credenciais e desenho do fluxo de autorização.
- Catálogo de ofertas de corretoras (CDB/LCI/LCA) e cotações B3: exigem fonte contratada.
- Análise completa de ETFs, FIIs e ações: faltam dados de custos, crédito, tracking e pesquisa; o cadastro CVM sozinho não habilita seleção.
- Ranking por rentabilidade líquida por lote, regras fiscais específicas e FGC consolidado: dependem dos metadados e metodologia adicionais. O motor inicial usa custos, liquidez e risco.
- Agente CFP de linguagem livre: Ollama opcional faz classificação semântica; as respostas financeiras ainda são estruturadas.
- Entrega de e-mails, deploy PostgreSQL, backups e alertas do provedor: configuração operacional necessária.
- Parecer regulatório para disponibilização comercial individualizada: depende de profissional responsável.

Esses itens permanecem explícitos; esta entrega não equivale a um wealth manager
comercial completo nem a um serviço conectado ao Open Finance.

## Direção visual

Preservar Manrope e a identidade aprovada: fundo #F8F9FC, papel #FFFFFF,
texto #132047, azul #3855EF, cinza #65758B. Conversa à esquerda e contexto
à direita no desktop, empilhados no celular. Produtos em lista comparável;
números alinhados, sem gradientes decorativos ou novo conjunto de cartões coloridos.

## Integrações externas

Tesouro Transparente e CVM: consulta pública, com proveniência e validade.
B3: fonte licenciada necessária para distribuição de cotações.
CDB/LCI/LCA: catálogo contratado de distribuidor necessário para ofertas executáveis.
Open Finance: depende de parceiro participante e consentimento do cliente.
SMTP: recuperação de senha depende de configuração de entrega de e-mail.
LLM: provedor local opcional; nunca calcula ou escolhe produtos por texto gerado.
Não apresentar conectores não configurados como conectados.

## Método

Iterar implementação, testes e revisão conforme Ralph Loop. O stop hook do
Claude Code não está disponível no Codex; não existe loop automático ativo.
O checklist registra conclusão comprovada, não apenas criação de arquivos.
