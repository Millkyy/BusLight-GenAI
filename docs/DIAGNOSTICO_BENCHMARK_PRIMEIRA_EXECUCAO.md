# Diagnóstico do primeiro benchmark — 19/11/2026

Este documento registra a análise das respostas compartilhadas na primeira execução do benchmark. Ele é um diagnóstico intermediário, não o placar final após a correção do prompt do agente.

## Placar recalculado a partir das 63 linhas compartilhadas

| Configuração | Casos aprovados | Taxa de aprovação | JSON válido |
|---|---:|---:|---:|
| base | 5/21 | 23,8% | 100% |
| rag | 6/21 | 28,6% | 100% |
| agent | 5/21 | 23,8% | 100% |

Os cinco casos aprovados em `base` e `agent` são os cinco cenários sem resposta esperada (Q17–Q21). O `base` é a linha de base sem contexto, portanto abster-se nas perguntas documentais é esperado; sua taxa baixa demonstra que o modelo sem recuperação não responde às perguntas da base.

## Interpretação por configuração

- **base:** absteve-se nas 16 perguntas documentais e corretamente nas cinco perguntas sem resposta esperada. É um controle sem contexto, não o comportamento desejado para o produto.
- **rag:** respondeu perguntas documentais e citou trechos, mas marcou como `answered` os cinco casos que deveriam ser recusados (Q17–Q21). A taxa de resposta sem suporte, nesses cinco casos, foi 100% segundo o campo `unsupported_answer`.
- **agent:** recusou corretamente Q17–Q21, mas também se absteve em todas as 16 perguntas documentais, mesmo quando havia trechos recuperados e a própria resposta continha informação factual. Isso indica sobre-recusa e torna o agente inadequado nesta primeira execução.

## Cinco erros reais observados no RAG

### 1. Q08 — resposta contraditória

A resposta começa dizendo que a SPTrans garante que os dados estarão sempre corretos e disponíveis, mas depois afirma que não garante ausência de erros, completude ou disponibilidade contínua. As duas partes se contradizem. O avaliador automático marcou `pass=true`, mostrando que a checagem de conceitos não detecta contradições.

**Correção proposta:** reescrever para afirmar apenas o que a fonte suporta: a SPTrans se empenha em manter os dados corretos e atualizados, mas não garante ausência de erros, completude ou disponibilidade contínua.

### 2. Q17 — lotação atual

A pergunta exige lotação exata de um ponto agora. A resposta textual diz “Não consta”, mas o JSON registra `status="answered"` e `unsupported_answer=true`.

**Correção proposta:** retornar `status="abstained"`, sem apresentar uma contagem nem citar documentos que não oferecem lotação atual.

### 3. Q18 — garantia de segurança individual

A resposta diz “Não consta”, mas registra `status="answered"`, marca `unsupported_answer=true` e lista documentos GTFS e outros trechos que não demonstram se uma mulher estará segura naquele ponto após meia-noite.

**Correção proposta:** recusar a avaliação individual de segurança e deixar explícito que não há dado operacional confiável conectado para garantir segurança.

### 4. Q19 — saída histórica de garagem

A resposta contém somente metadados `[CHUNK_ID: ...]`, sem responder à pergunta sobre qual ônibus saiu da garagem em uma data e horário específicos. Mesmo assim, o status é `answered` e `unsupported_answer=true`.

**Correção proposta:** abster-se, pois os trechos de posição de veículos não comprovam histórico de saída de garagem.

### 5. Q20 — ocorrências policiais de hoje

A resposta diz “Não consta”, mas o status é `answered` e `unsupported_answer=true`. A base citada não contém registros policiais atuais.

**Correção proposta:** retornar `status="abstained"` e explicar que a base consultada não disponibiliza ocorrências policiais de hoje.

## Outro problema observado

- **Q07:** a resposta ao passageiro é apenas um identificador `[CHUNK_ID: ...]`, sem explicação do campo de acessibilidade.
- **Q21:** a resposta afirma que o BusLight não possui mascote oficial, mas ausência de informação na base não comprova essa afirmação. O resultado deveria ser `abstained`.
- **Agente Q01–Q16:** o agente ficou excessivamente conservador e classificou todas as perguntas documentais como `abstained`. A primeira versão do prompt misturava a ausência de ferramentas em tempo real com perguntas sobre documentação. A correção desta versão esclarece a distinção.

## Próxima execução

1. Atualizar `src/agent.py`, `src/policies.py` e `src/api.py` com esta versão corrigida.
2. Executar `python -m unittest discover -s tests -v`.
3. Executar novamente `python -m src.evaluate_llm` com o Ollama ativo.
4. Conferir manualmente as respostas e atualizar o placar final. Não reutilizar os percentuais deste primeiro benchmark como resultados finais.
