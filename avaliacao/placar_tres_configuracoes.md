# Placar das três configurações

Modelo local: `qwen2.5:3b`. Execução registrada no `respostas_benchmark.jsonl` incluído neste repositório. Foram executadas 21 perguntas em cada configuração (63 registros).

| Configuração | Casos | Aprovação | JSON válido | Citações corretas* | Acerto da recusa** | Resposta sem suporte** | Latência média (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 21 | 0/21 (0,0%) | 100,0% | N/A | 0/5 (0,0%) | 0/5 (0,0%) | 11,16 |
| rag | 21 | 4/21 (19,0%) | 100,0% | 10/16 (62,5%) | 4/5 (80,0%) | 0/5 (0,0%) | 31,21 |
| agent | 21 | 13/21 (61,9%) | 100,0% | 15/16 (93,75%) | 5/5 (100,0%) | 0/5 (0,0%) | 32,74 |

\* Citações corretas são calculadas apenas nas 16 perguntas respondíveis. Para BASE, citação não se aplica porque não recebe documentos.  
\** Recusas/respostas sem suporte são calculadas apenas nos cinco casos de pergunta não respondível/operacional.

## Interpretação

- O agente supera o RAG simples em 42,9 pontos percentuais na taxa de aprovação automática (61,9% vs. 19,0%), nove casos aprovados a mais na amostra.
- O agente apresenta 93,75% de citações corretas em perguntas respondíveis, contra 62,5% no RAG.
- O agente acertou as cinco abstenções; o RAG acertou quatro; o BASE teve inconsistências entre texto de recusa e `status`.
- A latência média do agente foi 1,53 segundo maior que a do RAG nesta execução.
- A taxa `resposta sem suporte` considera apenas os cinco casos rotulados como não respondíveis. Ela não é uma taxa geral de alucinação. A resposta BASE Q10 contém erro factual detectado manualmente e está descrita em `docs/ANALISE_DE_ERROS.md`.
- A aprovação automática depende de gabaritos e grupos de conceitos manuais; resultados exigem revisão humana das respostas e fontes.

## Arquivos de evidência

- `respostas_benchmark.jsonl`: 63 respostas literais.
- `conjunto_teste.jsonl`: 21 perguntas e gabaritos.
- `metricas_busca.json`: Recall@1, Recall@3, HitRate e limiar.
- `../docs/ANALISE_DE_ERROS.md`: cinco erros reais e correções propostas.
