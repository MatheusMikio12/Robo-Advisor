# Prisma — execução do PRD conversacional

Data: 13/09/2026. Referência: `PRD_PRISMA_CONCIERGE.md`.

## Iteração 1 — entrega parcial da fase A

Implementado e integrado:

- Criação guiada de objetivo pela conversa, sem exigir perfil completo: nome, valor, prazo, saldo e contribuição. Ausência de resposta não vira zero.
- Rascunho estruturado versionado nas mensagens, retomável após recarga. Cancelamento/reinício explícitos; interpretação numérica restrita para evitar ambiguidade.
- Proposta com referência mensal calculada no backend, sem rendimento/inflação presumidos, e confirmação explícita para salvar.
- Confirmação idempotente; propostas canceladas, substituídas ou com contexto financeiro alterado são rejeitadas.
- Validação inicial de orçamento no cadastro/edição/confirmação de metas quando há diagnóstico: soma dos aportes versus capacidade e soma dos saldos versus patrimônio.
- Meu plano substitui o nome Metas e cenários. Parâmetros quantitativos e formulário de nova meta ficam recolhidos; comparação por mais contribuição ou mais prazo.
- Diagnóstico deixa de ser pré-requisito para iniciar um objetivo; custo de dívida é pulado quando o saldo informado é zero. O diagnóstico completo ainda existe para investimentos.
- Correção de perda de texto digitado durante chegada da resposta anterior.
- Adaptador Ollama evoluído para explicação suplementar com histórico limitado e resposta estruturada de referência. Não altera dados e não substitui o cálculo. Estado/fallback aparecem em cada resposta.

## Evidências

- Backend: 114 testes aprovados; dois avisos de depreciação de dependências.
- E2E: dois fluxos aprovados em 31,7 segundos, incluindo criação sem diagnóstico, retomada, confirmação, login único, diagnóstico, carteira, comparação e mobile.
- Build frontend e verificação de tipos aprovados; lint sem erros, com oito avisos preexistentes de fast refresh.
- Captura móvel revisada; formulário de criação recolhido após primeira crítica visual.
- API local reiniciada na porta 8000 e saúde confirmada. Sem commit, push ou publicação.

## Limitações desta iteração — não marcar a fase A inteira como concluída

- Conversa de criação ainda é um fluxo guiado, não interpretação livre de qualquer pedido. “Pular” preserva o estado, mas não avança o cálculo com valor desconhecido.
- Contexto parcial é apenas o rascunho do objetivo. Proveniência genérica por campo, revisão completa do diagnóstico e migração de seus defaults ainda pendentes.
- Modelo local não foi ativado ou baixado. A geração opcional precisa de benchmark real, avaliação semântica/adversarial e modelo disponível antes de ser usada como aconselhamento. O filtro numérico não prova veracidade de texto gerado.
- A validação orçamentária inicial não equivale a um livro de destinações: faltam reserva protegida por finalidade, transferências, fluxos recorrentes e serialização transacional de todas as alterações concorrentes. Sem perfil, adequação orçamentária permanece desconhecida.
- Cenários continuam usando o simulador anterior com hipóteses ilustrativas. Não foi implementado o motor Life-Cycle, aposentadoria integrada ou carteira por múltiplos objetivos.
- Interface preserva abas de diagnóstico/carteira/vida financeira; a consolidação final da navegação do PRD está pendente.
- Restam E05–E09, enriquecimento de catálogo, Open Finance, fontes contratadas, revisão regulatória e operação de produção conforme PRD.

## Próxima sequência

1. Contexto parcial por campo, confirmação/revisão e avaliação do modelo local.
2. Livro de destinações e orçamento integrado com consistência transacional, depois fluxos de vida e aposentadoria.
3. Estratégias por objetivo, produtos elegíveis e revisão metodológica.
4. Integrações externas e wealth especializado após resolver parceiros, fontes e escopo profissional.

## Ralph Loop

As instruções disponíveis do plugin foram consultadas. O stop hook depende do Claude Code e não está ativo nesta sessão Codex. Foi usado o ciclo manual de implementação, testes, diagnóstico da falha e nova validação. Não existe promessa de conclusão automática do PRD inteiro.
