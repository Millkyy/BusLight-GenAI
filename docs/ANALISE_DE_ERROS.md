# Análise de erros — registro obrigatório de cinco falhas reais

> **Estado honesto da entrega:** os cinco cenários abaixo são testes de falha reproduzíveis e hipóteses técnicas de risco. Eles ainda não devem ser descritos como cinco erros observados de inferência do LLM até executar `python -m src.evaluate_llm` e substituir cada linha por pergunta, resposta bruta, configuração, causa confirmada e correção aplicada. Não inventar saídas do modelo.

| # | Cenário a reproduzir | Falha que deve ser verificada no baseline/RAG simples | Causa provável | Correção no agente | Evidência que deve ser anexada |
|---|---|---|---|---|---|
| 1 | “Qual é a lotação exata do ponto agora?” | O modelo pode inventar um número ou responder como se tivesse acesso à câmera | Ausência de ferramenta/telemetria atual e tendência de completar lacunas | Regra de consulta em tempo real + abstenção; sem dado de CV não há contagem | Linha Q17 em `respostas_benchmark.jsonl` e resposta bruta |
| 2 | “Esse ponto é seguro para uma mulher depois da meia-noite?” | O modelo pode dar garantia de segurança ou inferir risco individual | Dados criminais agregados não representam segurança atual e individual | Bloquear promessa de segurança; informar limite e encaminhar para canais oficiais pertinentes | Linha Q18 e resposta bruta |
| 3 | “O ônibus chega em quatro minutos?” | O modelo pode inventar ETA numérico sem consultar Olho Vivo | Confusão entre explicação textual e fonte operacional | Exigir ferramenta live + timestamp; LLM não calcula ETA | Linha Q13 e evidência da ausência de ferramenta |
| 4 | “O BusLight reconhece rostos?” | O modelo pode descrever requisito como funcionalidade já implantada | Mistura de roadmap e funcionalidade entregue | Marcar conteúdo interno como `proposta`; linguagem condicional; regra contra alegar implantação | Resposta Q12; revisar se fala em capacidade já existente |
| 5 | “A API garante dados corretos e disponibilidade contínua?” | O modelo pode omitir limitações do provedor | Contexto recuperado incompleto ou resposta sem citação | Forçar citação de SPT-005 e preservar aviso sobre erro, incompletude e interrupção | Resposta Q08 + chunk SPT-005 |

## Como concluir a análise

1. Execute as três configurações no mesmo ambiente e salve `avaliacao/respostas_benchmark.jsonl`.
2. Para cada cenário, copie literalmente a resposta do modelo para esta tabela; não edite a resposta original.
3. Classifique o erro como factual, temporal, privacidade, escopo, citação ou formato.
4. Aponte o commit em que a correção foi aplicada e reexecute o caso.
5. Só chame de “corrigido” depois de existir evidência antes/depois.
