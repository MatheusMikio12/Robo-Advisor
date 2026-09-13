# PRD — Prisma: planejamento financeiro conversacional

Versão: 1.0 · Data: 13/09/2026 · Status: proposta para implementação

Este documento consolida as melhorias discutidas para a evolução do Prisma. Não declara essas melhorias entregues nem autoriza contratação de serviços, execução de investimentos ou publicação comercial. Prioridades são propostas; estimativas e responsáveis serão definidos no planejamento de cada fase.

O `PRD.md` da raiz registra o MVP acadêmico anterior. Este documento passa a ser a referência de escopo para a evolução conversacional. `docs/PRISMA_EVOLUTION.md` registra entregas anteriores e limitações conhecidas; seus resultados de testes são históricos, não uma certificação da versão futura.

## 1. Visão e resultado esperado

Transformar um recomendador de carteira em um concierge que ajuda pessoas a decidir o que fazer com seu dinheiro, conectando vida, orçamento, objetivos e investimentos.

Proposta de valor: “Entenda suas possibilidades, escolha seu próximo passo e acompanhe um plano que evolui com sua vida.”

A experiência deve ser simples para iniciantes e verificável para usuários experientes. Sofisticação financeira fica no motor; a interface apresenta decisões, consequências e informações necessárias, sem exigir que o cliente configure modelos quantitativos.

### Público e limites

- Público inicial: pessoas físicas no Brasil, com renda e objetivos predominantemente em reais, organizando reserva, dívidas, compras e aposentadoria.
- Público secundário: investidores com várias metas e posições em diferentes instituições.
- Patrimônio empresarial, internacional ou sucessório complexo: aprofundamento posterior, com encaminhamento especializado quando necessário.
- Não posicionar o software como profissional certificado CFP, gestor discricionário ou garantia de resultados.

### Princípios

1. Entregar valor antes de pedir um diagnóstico completo.
2. Perguntar apenas o que muda a próxima decisão; uma pergunta principal por mensagem.
3. Nunca converter informação ausente em zero ou em uma resposta presumida.
4. Separar fatos confirmados, estimativas e hipóteses de cenário.
5. Calcular no backend; usar IA para entender, perguntar e explicar.
6. Não aumentar risco automaticamente para tornar uma meta aparentemente viável.
7. Não contar patrimônio ou capacidade de aporte duas vezes.
8. Mostrar limitações e indisponibilidade de dados sem inventar produtos ou conexões.
9. Preservar controle do cliente: propostas antes de alterações persistentes.

## 2. Ponto de partida

Baseline baseado no código e na documentação inspecionados durante esta evolução; revalidar antes de cada entrega.

| Área | Base existente | Lacuna principal |
|---|---|---|
| Diagnóstico | 15 perguntas, revisão e rascunho persistido | Jornada longa, campos sem relevância condicional e ausência de perfil parcial explícito |
| Conversa | Histórico e respostas financeiras estruturadas | Não é conversa generativa; Ollama opcional apenas classifica assunto |
| Planejamento | Metas, prioridades e registro de aportes | Metas não compõem um plano de vida integrado com distribuição única de recursos |
| Simulação | Monte Carlo, inflação, custos, imposto aproximado, pausas e retiradas | Excesso de parâmetros visíveis e ausência de modelagem completa do ciclo de vida |
| Carteira | Limites de risco, carteiras-modelo, explicações e exclusões | Estratégia global, não orientada ao conjunto de objetivos |
| Produtos | Referências públicas Tesouro/CVM e filtros de validade | Cadastro não equivale a oferta executável; faltam metadados e disponibilidade para várias classes |
| Vida financeira | Posições, movimentações e importação CSV/OFX | Sem agregação consentida automática; conciliação e classificação precisam evoluir |
| Segurança | Autenticação, MFA, recuperação e auditoria implementados | Operação de produção, entrega SMTP, restauração e validação PostgreSQL pendentes |

A disponibilidade de um modelo local deve ser verificada em tempo de execução. Configurar um adaptador não significa que o modelo esteja conectado ou gerando respostas.

## 3. Frameworks integrados

| Framework | Responsabilidade | Implementação proposta |
|---|---|---|
| Financial Life Planning | Entender o porquê | Motivações, valores, prioridades e limites pessoais coletados progressivamente |
| Life-Cycle | Projetar a evolução da vida financeira | Fluxos de renda/despesas, dependentes, eventos, aposentadoria e riscos familiares |
| Goal-Based Investing | Financiar objetivos | Metas flexíveis/essenciais, orçamento compartilhado, destinação de recursos e estratégias por horizonte |
| Perfil de risco | Limitar decisões | Tolerância, capacidade financeira, conhecimento, liquidez e restrições tratados separadamente |
| Wealth Planning | Tratar complexidade relevante | Triagem de concentração empresarial, proteção, previdência, tributação e sucessão |

Os frameworks não serão cinco questionários ou cinco telas. Life Planning orienta a conversa; Life-Cycle e objetivos compartilham o motor; suitability limita recomendações; Wealth Planning é acionado por necessidade.

## 4. Jornada e arquitetura de informação

### Entrada

Mensagem inicial: “O que você gostaria de resolver primeiro com seu dinheiro?”

Atalhos opcionais: organizar meu dinheiro, sair das dívidas, criar reserva, realizar um objetivo, entender investimentos. Texto livre sempre disponível.

Depois de duas ou três perguntas relevantes, entregar uma primeira síntese ou orientação de próximo passo. Isso não implica liberar recomendação personalizada com dados insuficientes.

### Navegação proposta

- **Conversa:** entrada principal, continuidade, perguntas, propostas e explicações.
- **Meu plano:** objetivos, próximos passos, conflitos, comparações e progresso.
- **Meu dinheiro:** orçamento, patrimônio, dívidas, posições e produtos associados ao plano.
- **Conta:** segurança, privacidade, preferências e integrações.

Diagnóstico vira “Seu contexto”, editável a partir da conversa e do plano. “Metas e cenários” deixa de ser uma ferramenta técnica isolada. Preservar identidade visual aprovada, Manrope, cores sóbrias e hierarquia consistente; evitar novos painéis decorativos sem função.

### Exemplo de fluxo

“Quero comprar um apartamento” → valor da entrada → prazo → valor já guardado → primeira leitura → capacidade mensal e compromissos → comparação de alternativas → confirmação do objetivo → completar informações de risco quando for selecionar investimentos.

## 5. Backlog funcional e critérios de aceite

Prioridades: **P0** fundação e primeira entrega; **P1** aprofundamento do planejamento; **P2** patrimônio complexo e integrações dependentes de terceiros. Segurança essencial acompanha todas as fases, independentemente da prioridade funcional.

### E01 — Diagnóstico progressivo e contexto estruturado · P0

- **D01:** substituir sequência obrigatória de 15 perguntas por roteamento por intenção e informações faltantes.
- **D02:** permitir começar um plano sem suitability completo; bloquear apenas ações que realmente dependam dele.
- **D03:** criar estado explícito por informação: desconhecida, informada, confirmada, estimada ou desatualizada; registrar fonte e data.
- **D04:** permitir pular, corrigir e retomar perguntas. Não perguntar taxa de dívida quando o cliente confirmou não ter dívidas.
- **D05:** indicar por que uma pergunta é necessária e mostrar resumo editável antes da confirmação.
- **D06:** migrar rascunhos antigos sem tratar valores-padrão como fatos confirmados; versionar a jornada, não depender apenas do índice de pergunta.

Aceite: usuário sem perfil consegue iniciar e salvar rascunho de objetivo; respostas sobrevivem a recarga; campos desconhecidos permanecem desconhecidos; geração de carteira informa exatamente quais dados faltam; migração preserva dados existentes e exige confirmação quando a origem for ambígua.

### E02 — Concierge com IA real · P0

- **IA01:** implementar geração conversacional com provedor substituível; priorizar teste local via Ollama/modelo disponível, sem assumir que uso local não tem custo de hardware e operação.
- **IA02:** utilizar histórico recente e memória estruturada relevante, não todo o histórico indiscriminadamente.
- **IA03:** disponibilizar ferramentas autorizadas de consulta de contexto, metas, orçamento, simulação e carteira. O servidor determina usuário e permissões.
- **IA04:** extrair propostas de atualização em esquema validado; apresentar confirmação antes de persistir dados ou modificar metas.
- **IA05:** responder com uma síntese, uma consequência prática e, quando necessário, uma pergunta. Evitar jargão, interrogatórios e respostas excessivamente longas.
- **IA06:** informar estado real: modelo conectado, indisponível ou atendimento estruturado. Timeout, cancelamento e fallback devem preservar mensagens e evitar duplicação.
- **IA07:** impedir instruções em documentos/importações de alterar políticas, acessar outras contas ou executar ferramentas não autorizadas.
- **IA08:** associar afirmações numéricas a resultados de ferramentas e produtos a identificadores consultados. Quando não houver validação, retornar resposta estruturada segura.

Aceite: conversa de múltiplos turnos entende referências como “e se forem cinco anos?”; hipótese não altera plano salvo; confirmação é idempotente e vinculada à revisão atual; falha do modelo aparece com transparência; não há acesso entre usuários, produto inventado ou cálculo financeiro dependente apenas de texto gerado nos testes de bloqueio.

### E03 — Meu plano em linguagem simples · P0

- **UX01:** substituir formulário extenso de cenários por objetivo, valor desejado, valor disponível, prazo e contribuição possível, com coleta progressiva.
- **UX02:** manter retorno, inflação, volatilidade, custos e impostos em “Como calculamos”, com hipóteses visíveis e editáveis, sem apresentá-las como taxas atuais.
- **UX03:** apresentar valor projetado, diferença para o objetivo e alternativas “guardar mais”, “dar mais tempo” e “reduzir o valor”.
- **UX04:** comparar plano atual e alternativa lado a lado; identificar o que mudou e permitir salvar após confirmação.
- **UX05:** explicar poder de compra, incerteza e valores nominais/reais em linguagem comum. Não chamar probabilidade simulada de garantia.
- **UX06:** revisar contraste, alinhamento de valores, hierarquia, estados vazios, erros e experiência móvel. Manter login em uma tentativa como regressão obrigatória.
- **UX07:** credenciais de demonstração, quando exibidas por conveniência, somente em ambiente de demonstração explicitamente habilitado; nunca senhas reais ou de produção. Preservar marca Prisma e ausência do ícone Lovable.

Aceite: pessoa sem experiência cria e compara um objetivo sem editar parâmetros quantitativos; modo avançado mantém rastreabilidade; navegação por teclado e leitores de tela funciona; não há rolagem horizontal a 390 px; testes cobrem login, retomada e confirmação.

### E04 — Objetivos e orçamento integrados · P0

- **GO01:** acrescentar mínimo aceitável, valor desejado, prioridade, essencialidade, flexibilidade de prazo e pagamento único/recorrente.
- **GO02:** criar orçamento compartilhado para metas e vínculos explícitos entre recursos e objetivos.
- **GO03:** distinguir saldo existente, novos aportes, transferências e reserva protegida; conciliar posições com patrimônio informado.
- **GO04:** detectar excesso de compromissos e propor redistribuição sem alterar silenciosamente prioridades.
- **GO05:** acompanhar aporte planejado versus realizado, revisões e progresso; não contar transferência entre contas como renda ou novo patrimônio.

Aceite: soma das destinações não supera recursos disponíveis; duas metas não usam integralmente o mesmo saldo; compromissos recorrentes afetam orçamento; aporte duplicado não é contado; conflitos de metas são apresentados antes de salvar um plano inviável.

### E05 — Life-Cycle e aposentadoria · P1

- **LC01:** modelar família, dependentes, fontes de renda, estabilidade, despesas essenciais/flexíveis e eventos datados.
- **LC02:** construir projeção mensal integrada, com resumo anual, durante acumulação e retiradas.
- **LC03:** adicionar idade desejada de aposentadoria, renda desejada, fontes previdenciárias informadas e horizonte de longevidade editável. Não presumir benefício público ou direito adquirido.
- **LC04:** representar capital humano por cenários de renda, interrupções e concentração setorial; evitar um valor exato fictício para a carreira.
- **LC05:** suportar cenários de desemprego, mudança de carreira, filhos, saúde, inflação, longevidade e sequência desfavorável de retornos.
- **LC06:** definir regras de revisão da estratégia conforme prazo e situação financeira; idade isolada não determina carteira.

Aceite: um evento altera todos os objetivos afetados; saldo negativo não desaparece por truncamento; reserva e retirada são contabilizadas uma única vez; aposentadoria considera gastos recorrentes e fontes de renda; hipóteses e limitações acompanham cada resultado.

### E06 — Carteira orientada a objetivos · P1

- **CA01:** separar estratégia de reserva, objetivos próximos e longo prazo, preservando visão consolidada.
- **CA02:** substituir dependência exclusiva de carteiras-modelo por política por objetivo, com capacidade, tolerância, prazo, liquidez e moeda.
- **CA03:** mensurar cobertura e insuficiência dos objetivos, além de retorno e volatilidade.
- **CA04:** verificar concentração agregada por emissor/grupo, classe, moeda e exposições compartilhadas, inclusive investimentos existentes.
- **CA05:** sugerir rebalanceamento considerando novos aportes, custos, tributação e restrições; não gerar ordens automáticas.
- **CA06:** calibrar e documentar regras hoje simplificadas, como reserva de 6/9/12 meses e corte fixo para dívida cara; distinguir educação, limite de produto e tolerância financeira.

Aceite: estratégia curta não herda risco de uma meta longa; aumento de conhecimento não implica aumento automático de risco; recomendação sem produto adequado mantém parcela não alocada; alterações de dados invalidam análise anterior; cada decisão informa motivo e versão da política.

### E07 — Produtos reais e adequação · P1 / conectores P2

- **PR01:** separar cadastro de instrumento, dados de mercado e oferta disponível numa instituição.
- **PR02:** enriquecer identificador, emissor/grupo, moeda, prazo, liquidez/carência, mínimo, custos, indexador, riscos, regime tributário e fonte.
- **PR03:** definir validade por tipo de dado; cotação, oferta e cadastro não devem compartilhar cegamente a mesma janela.
- **PR04:** contratar/integrar fontes autorizadas quando necessário para B3, distribuidores e ofertas CDB/LCI/LCA; validar direitos de uso.
- **PR05:** implementar elegibilidade antes de ranking. Comparar produtos equivalentes por função, custos e condições, não apenas rentabilidade passada.
- **PR06:** desenvolver cálculo líquido por lote e análise consolidada de garantias aplicáveis, com regras brasileiras versionadas e revisão especializada.
- **PR07:** expor motivos de inclusão/exclusão, alternativas, data da consulta e necessidade de conferir oferta na instituição.
- **PR08:** para ETFs, fundos, FIIs e ações, definir metodologia e dados mínimos específicos; cadastro CVM sozinho não habilita recomendação.

Aceite: informação obrigatória ausente ou vencida bloqueia seleção; disponibilidade não confirmada nunca aparece como compra disponível; nomes e condições vêm da fonte; vínculo produto–objetivo é explicado; não há promessa de rentabilidade ou proteção irrestrita.

### E08 — Consolidação e acompanhamento · P1 / Open Finance P2

- **VI01:** melhorar classificação e conciliação CSV/OFX, com prévia, confirmação, deduplicação e correções persistentes.
- **VI02:** separar transferências, receitas, despesas, aportes e rendimentos; reconciliar divergências com o usuário.
- **VI03:** oferecer revisão por mudança relevante: renda, gastos, meta próxima, reserva insuficiente ou dados vencidos.
- **VI04:** permitir preferências de frequência e silenciamento de alertas; nenhum monitoramento implica execução financeira.
- **VI05:** integrar Open Finance somente com parceiro adequado, consentimento, escopo, validade, revogação e tratamento de falhas.

Aceite: reimportar arquivo não duplica patrimônio; correção de categoria é reaproveitada de forma auditável; alerta explica causa e ação possível; conexão revogada interrompe novas coletas; conta desconectada permanece identificada como tal.

### E09 — Wealth Planning seletivo · P2

- **WP01:** triagem opcional para concentração empresarial/imobiliária, dependentes, proteção, previdência, residência fiscal e ativos internacionais.
- **WP02:** mapear liquidez patrimonial e necessidades familiares sem confundir patrimônio ilíquido com dinheiro disponível.
- **WP03:** desenvolver módulos tributários, previdenciários, de proteção e sucessórios com fontes, jurisdição, vigência e responsável pela revisão.
- **WP04:** encaminhar decisões jurídicas/tributárias complexas a profissional habilitado; registrar pendências e documentos necessários, sem emitir parecer automático definitivo.

Aceite: módulos aparecem por relevância, não para todos; fonte desatualizada impede conclusão específica; regimes estrangeiros não são aplicados ao Brasil por padrão; recomendações fora do escopo são identificadas e encaminhadas.

## 6. Arquitetura proposta

Fluxo: mensagem → autenticação → contexto relevante → intenção/dados faltantes → ferramenta autorizada → resultado validado → explicação → proposta de alteração → confirmação → nova revisão do plano.

Separar responsabilidades, mantendo inicialmente um monólito modular FastAPI:

- **Contexto:** fatos, origem, confirmação e permissões.
- **Orquestrador:** seleção de ferramentas e necessidade de perguntas.
- **Planejador:** orçamento compartilhado, objetivos e eventos.
- **Simulador:** cenários determinísticos e probabilísticos reproduzíveis.
- **Política de investimentos:** limites e consolidação de riscos.
- **Catálogo:** instrumentos, ofertas, fontes e validade.
- **Validação:** consistência financeira, contratos de saída e restrições.
- **Auditoria:** revisões, propostas, confirmações e decisões.

Não exigir múltiplos agentes, microserviços, banco vetorial ou treinamento próprio na primeira entrega. Adotar apenas quando testes demonstrarem benefício. LLM não recebe acesso irrestrito ao banco, shell ou credenciais. Resultados de ferramentas são dados, não instruções.

### Entidades a criar ou evoluir

| Entidade | Conteúdo mínimo |
|---|---|
| Fato de contexto | Campo, valor, estado, fonte, data, confirmação, usuário e revisão |
| Família / renda / despesa | Pessoas, recorrência, período, moeda e hipóteses |
| Evento de vida | Tipo, data, duração, impactos e estado hipótese/confirmado |
| Objetivo | Faixa de valor, prazo, prioridade, flexibilidade e recorrência |
| Destinação | Recurso, objetivo, valor e período; restrições de dupla contagem |
| Revisão de plano | Snapshot dos fatos, política e premissas; resultados e pendências |
| Proposta de alteração | Diferença, revisão-base, validade, confirmação e chave idempotente |
| Instrumento / oferta | Identificador, metadados, instituição, disponibilidade e proveniência |
| Execução de cálculo | Entradas, versão, semente quando aplicável, resultados e limitações |

Contratos de API propostos devem suportar consulta de contexto parcial, propostas/confirmacões, comparação de planos e status do provedor. Definir nomes e schemas no desenho técnico antes de implementação. Não quebrar endpoints antigos sem migração e testes de compatibilidade.

## 7. Método quantitativo e validação

- Separar motor de fluxos de caixa do modelo de retornos; documentar convenções de aportes, retiradas, inflação, taxas e arredondamento.
- Utilizar precisão monetária apropriada no registro contábil; definir tolerâncias explícitas nos modelos probabilísticos.
- Calibrar retornos, volatilidades e correlações por metodologia documentada; não extrapolar um parâmetro arbitrário como previsão de mercado.
- Exibir probabilidade e tamanho da insuficiência; evitar escolher estratégias apenas pela maior probabilidade simulada.
- Versionar regras tributárias e registrar quando o cálculo for aproximação, especialmente antes do motor por lote.
- Testar cenários adversos e sensibilidade; um resultado não pode depender de uma única trajetória favorável.
- Preservar reprodutibilidade com entradas, versões e sementes; não representar precisão matemática como certeza econômica.

## 8. Segurança, privacidade e operação

- Isolamento por usuário em consultas, memória, arquivos e ferramentas; teste obrigatório para cada novo endpoint.
- Minimização de dados enviados ao modelo; segredos nunca entram em prompts ou logs. Provedor externo exige decisão explícita sobre tratamento e transferência de dados.
- Exportação, correção, exclusão e retenção documentadas; consentimentos e acesso operacional com privilégio mínimo.
- Proteção contra prompt injection, abuso de ferramentas, uploads maliciosos e vazamento de informações pessoais.
- Rate limiting, limites de tamanho, timeout e observabilidade também para inferência e importações.
- Auditoria rastreável de decisões sem registrar indiscriminadamente conteúdo sensível; definir retenção e acesso.
- Validar PostgreSQL real, migrações, backup/restauração, SMTP, HTTPS, segredos de produção e alertas antes de lançamento.
- Obter avaliação profissional sobre enquadramento regulatório brasileiro e escopo comercial; aviso de responsabilidade sozinho não substitui essa avaliação.
- Operações com dinheiro e execução de ordens ficam fora deste PRD; exigiriam novo escopo, parceiro e autorizações específicas.

## 9. Métricas e testes de aceite

Metas abaixo são propostas de produto, ainda não medições. Instrumentar baseline antes de fixar compromissos de desempenho.

| Indicador | Alvo inicial / verificação |
|---|---|
| Esforço inicial | Primeira síntese útil após até 3 respostas na jornada simples de objetivo; não equivale a carteira liberada |
| Compreensão | Pelo menos 4 de 5 participantes iniciantes explicam o próximo passo em teste exploratório; ampliar amostra antes de generalizar |
| Usabilidade | Pelo menos 4 de 5 concluem criar/comparar objetivo sem ajuda no piloto |
| Consistência financeira | Zero falha nos testes de dupla contagem, orçamento e invariantes monetários |
| Segurança da IA | Zero vazamento entre contas ou mutação não confirmada na suíte de bloqueio |
| Fundamentação | Números e produtos das respostas de recomendação vinculados a cálculo/fonte nos casos de aceite |
| Continuidade | Retomada de conversa/rascunho e confirmação idempotente cobertas por E2E |
| Disponibilidade percebida | Feedback imediato de processamento; medir p50/p95 e definir timeout segundo hardware/provedor |

Não usar aprovação em perguntas de prova CFP ou retorno de investimentos isoladamente como comprovação de qualidade do produto.

### Casos obrigatórios

1. Iniciante sem diagnóstico inicia uma meta sem receber carteira prematura.
2. Cliente sem dívidas não precisa informar juros de dívida inexistente.
3. Cliente com duas metas e orçamento insuficiente vê conflito e alternativas.
4. Reserva e posições importadas não são somadas novamente ao patrimônio total.
5. Cliente com renda variável recebe cenário de interrupção sem renda fictícia.
6. “E se eu parar de trabalhar?” simula hipótese sem alterar renda confirmada.
7. Aposentadoria apresenta risco de insuficiência em sequência adversa de retornos.
8. Objetivo curto e longo coexistem sem transferir risco indevido ao objetivo curto.
9. Produto vencido/incompleto fica inelegível e a parcela permanece explicitamente não alocada.
10. Moeda não suportada provoca limitação explícita, não conversão silenciosa.
11. Modelo indisponível aciona fallback sem fingir resposta de IA.
12. Documento com instrução maliciosa não altera permissões nem políticas.
13. Confirmação repetida ou sobre revisão antiga não duplica nem sobrescreve alterações.
14. Login único, recuperação, mobile e acessibilidade passam nas regressões.

## 10. Roadmap e dependências

| Fase | Escopo | Dependências | Porta de saída |
|---|---|---|---|
| A — Concierge e plano simples | E01–E04, memória, ferramentas e contexto parcial | Escolha/teste do modelo, migração de dados e contratos | Jornada compreensível, orçamento consistente e IA com confirmação/fallback |
| B — Planejamento ao longo da vida | E05 e evolução quantitativa | Fluxos integrados e metodologia revisada | Eventos e aposentadoria afetam plano completo, com cenários adversos |
| C — Investimentos por objetivos | E06–E07 e consolidação E08 | Dados mínimos, política validada e fontes autorizadas | Produtos rastreáveis e exposição consolidada compatível |
| D — Wealth e conectividade | E09, Open Finance e aprofundamentos fiscais | Parceiros, regras revisadas e operação segura | Consentimento, especialização e limites comerciais aprovados |

Segurança e testes são transversais. Melhorias de importação e qualidade cadastral podem avançar antes da fase C, mas não dispensam suas dependências. Não atribuir datas antes de dimensionar equipe, integrações e metodologia.

### Primeira entrega vertical recomendada

Um usuário novo diz que quer realizar uma compra, informa os dados necessários em conversa, confirma uma meta, vê sua capacidade mensal e compara duas alternativas calculadas. Pode retomar depois. O sistema não exige diagnóstico completo nem inventa rentabilidade; investimentos só aparecem após completar os dados de adequação.

## 11. Riscos e decisões pendentes

| Questão | Encaminhamento |
|---|---|
| Modelo local lento ou insuficiente | Benchmark em português com casos reais; escolher por qualidade/latência, preservar fallback e adaptador substituível |
| Dados financeiros incompletos | Mostrar o que falta e grau de cobertura; não ocultar incerteza |
| Crescimento excessivo de escopo | Priorizar entrega vertical A antes de wealth avançado |
| Custos/licenças de dados | Definir orçamento e parceiros antes de implementar ofertas comerciais |
| Regras financeiras simplificadas | Revisão especializada e versionamento, sem alegar otimização completa |
| Mudança de schema e rascunhos | Migração testada em cópia, backup e confirmação de informações ambíguas |
| Aconselhamento comercial | Definir modelo de serviço e responsabilidade antes de disponibilização pública |

Decisões necessárias: público e escopo do piloto; hardware/provedor de IA; orçamento de dados; metodologia de premissas; responsável financeiro; consentimento/retencão; política de notificações; critérios de passagem de demonstração para produção.

## 12. Definição de pronto

Um item só pode ser marcado como entregue quando tiver implementação integrada, critérios de aceite comprovados, testes proporcionais ao risco, interface revisada, documentação atualizada e limitações identificadas. Um conector não configurado não conta como integração entregue. Uma simulação não equivale a recomendação executável. Nenhuma fase autoriza commit, push, deploy ou contratação automaticamente.

## 13. Referências e inspiração

Referências consultadas na discussão de 13/09/2026; não representam certificação ou equivalência do Prisma a esses serviços.

- [Vanguard — Life-Cycle Investing Model](https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_life_cycle_investing_model_vlcm_a_general_portfolio_framework_for_goals_based_investing.pdf): integração de ciclo de vida e objetivos como base metodológica.
- [CFP Board — processo de planejamento financeiro](https://www.cfp.net/ethics/compliance-resources/2022/01/guide-to-the-financial-planning-process): compreensão do cliente, objetivos, alternativas e acompanhamento; não implica certificação do software.
- [RightCapital — fluxos de caixa](https://help.rightcapital.com/module-overview/client-portal/retirement/cash-flows): referência de visualização integrada de renda, despesas e objetivos ao longo do tempo.
- [Origin — visão técnica](https://useorigin.com/resources/blog/technical-overview): referência arquitetural de contexto, ferramentas e cálculo separado da linguagem. Alegações de desempenho são da própria empresa, não validação independente nem garantia de resultado para clientes.

Referências internacionais orientam produto e arquitetura; regras tributárias, previdenciárias e sucessórias exigem adaptação e validação brasileiras.
