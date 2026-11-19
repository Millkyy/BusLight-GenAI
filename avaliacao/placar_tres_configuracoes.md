# Placar das três configurações

Resultados medidos nesta execução, usando o mesmo modelo e os mesmos casos. Não substituir por estimativas.

| Configuração | Casos | Taxa de aprovação | JSON válido | Citações corretas | Acerto da recusa | Resposta sem suporte | Latência média (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 21 | 23.8% | 100.0% | 0.0% | 100.0% | 0.0% | 0.00 |
| rag | 21 | 57.1% | 100.0% | 93.8% | 100.0% | 0.0% | 38.88 |
| agent | 21 | 38.1% | 100.0% | 37.5% | 100.0% | 0.0% | 34.44 |

**Interpretação:** comparar primeiro `agent` com `rag` (ganho da especialização) e `rag` com `base` (ganho da recuperação). Uma taxa menor de resposta sem suporte é desejável. Examinar manualmente as respostas antes de concluir.
