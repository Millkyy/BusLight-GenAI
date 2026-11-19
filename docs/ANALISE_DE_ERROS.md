# Análise de cinco erros reais — benchmark salvo no repositório

## Escopo e rastreabilidade

Esta análise foi montada a partir das respostas literais de `avaliacao/respostas_benchmark.jsonl` incluídas no ZIP recebido. Não são cenários hipotéticos. As saídas abaixo pertencem à execução registrada no pacote (`qwen2.5:3b`, 21 perguntas por configuração). As correções listadas são propostas técnicas; **não devem ser chamadas de corrigidas até rodar novamente os casos e registrar a resposta posterior**.

## 1. BASE — Q10: invenção de princípios da LGPD

**Pergunta:** Quais princípios da LGPD o BusLight deve seguir?

**Resposta literal:**

> O BusLight deve seguir os princípios da LGPD (Lei Geral sobre a Privacidade e Proteção de Dados), que incluem: Objetividade, Limite de Coleta, Transparência, Limitação de Dados, Integridade e Qualidade, Proporção, Não Dano, Autonomia do Titular dos Dados, Respeito ao Direito de Oposição e Direito de Apagamento.

**Evidência esperada:** o chunk `LGPD-002` lista finalidade, adequação, necessidade, livre acesso, qualidade dos dados, transparência, segurança, prevenção, não discriminação e responsabilização/prestação de contas.

**Classificação:** afirmação factual sem fundamentação no contexto (alucinação/erro factual do baseline).

**Causa provável:** o BASE não recebe documentos; o modelo completou a resposta com uma lista não sustentada pelo material do projeto.

**Correção proposta:** manter BASE apenas como linha de comparação; exigir, no RAG/AGENT, recuperação e citação do `LGPD-002`; incluir teste de regressão para impedir que a lista inventada apareça como resposta fundamentada.

## 2. RAG — Q01: metadados em vez de resposta

**Pergunta:** Como o BusLight deve informar o tempo estimado de chegada?

**Resposta literal:**

> CHUNK_ID: SPT-003 | CHUNK_ID: BL-003 | CHUNK_ID: SPT-002

**Citações registradas:** `SPT-003`, `BL-003` e `SPT-002`.

**Classificação:** erro de formato/conteúdo: identificadores internos foram colocados em `answer`, sem explicação em linguagem natural.

**Causa provável:** o modelo confundiu o contexto recuperado com o conteúdo da resposta.

**Correção proposta:** reforçar que `answer` deve explicar que a previsão vem da consulta à Olho Vivo por linha e parada, com horário de atualização; IDs devem aparecer apenas em `citations`. Acrescentar teste para rejeitar resposta formada só por metadados.

## 3. RAG — Q07: abstenção indevida

**Pergunta:** Como a API informa se um ônibus é acessível?

**Resposta literal:**

> Não consta

**Contexto recuperado:** `SPT-004` (score top-1 registrado: `0.1717`). Esse trecho diz que o campo booleano `a` indica se o veículo é acessível para pessoas com deficiência e ressalva que isso não garante a acessibilidade completa da viagem, ponto ou trajeto.

**Classificação:** falso negativo / abstenção indevida.

**Causa provável:** o modelo não utilizou um trecho que já havia sido recuperado e era pertinente à pergunta.

**Correção proposta:** instruir o RAG a responder quando o trecho recuperado contiver diretamente a informação; adicionar resposta de referência e teste de regressão para `SPT-004`.

## 4. AGENT — Q15: falso negativo apesar de citação pertinente

**Pergunta:** Quais dados e licença constam no catálogo Censo 2022 do Estado de São Paulo?

**Resposta literal:**

> Os trechos recuperados não fornecem informações sobre dados e licença do Censo 2022 do Estado de São Paulo. Os trechos fornecidos são sobre o Censo 2022 do IBGE e a API Open-Meteo, não o Censo 2022 do Estado de São Paulo.

**Citações registradas:** `IBGE-001` e `OM-001`. O chunk `IBGE-001` contém os campos população, domicílios, educação e trabalho e informa licença CC BY 4.0.

**Classificação:** falso negativo / contradição entre a resposta e a evidência citada.

**Causa provável:** o agente tratou a pergunta como não respondível apesar de ter recuperado e citado a fonte correta.

**Correção proposta:** reforçar a regra de que um chunk citado que contém a resposta deve ser usado antes de concluir “não consta”; incluir exemplo documental para `IBGE-001` e teste de regressão Q15.

## 5. RAG — Q19: resposta vazia e citações irrelevantes

**Pergunta:** Qual ônibus acabou de sair da garagem da empresa ontem às 23h?

**Resposta literal:**

> [campo answer vazio]

**Status e motivo registrados:** `status=abstained`; `reason=` `Não consta`.

**Citações registradas:** `SPT-002`, `SPT-005` e `OM-001`, embora não respondam à pergunta sobre saída de garagem.

**Classificação:** erro de abstenção/contrato semântico: JSON estruturalmente válido, mas `answer` vazio e citações sem pertinência.

**Causa provável:** o modelo não respeitou a regra de remover citações quando se abstém e não preencheu a explicação ao passageiro.

**Correção proposta:** normalizar respostas abstidas para texto explícito em `answer` e `citations=[]`; validar status, conteúdo e ausência de citações em casos “não consta”.

## Evidência complementar do benchmark

- Arquivo bruto: [`../avaliacao/respostas_benchmark.jsonl`](../avaliacao/respostas_benchmark.jsonl).
- Placar: [`../avaliacao/placar_tres_configuracoes.csv`](../avaliacao/placar_tres_configuracoes.csv).
- Os cinco exemplos acima foram selecionados diretamente das respostas registradas, sem reescrever o texto produzido pelo modelo.

## Verificação das correções

Para cada correção proposta, reexecutar pelo menos o caso indicado (`Q10`, `Q01`, `Q07`, `Q15`, `Q19`) nas configurações relevantes e salvar as novas respostas. Atualizar esta análise com a saída posterior, data da execução e resultado do teste. Até isso ocorrer, o estado é **correção proposta, ainda não validada**.
