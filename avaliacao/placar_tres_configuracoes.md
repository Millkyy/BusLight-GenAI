# Placar das três configurações

Modelo local: `qwen2.5:3b`.
Resultados medidos nesta execução. Não substituir por estimativas.

| Configuração | Casos | Aprovação | JSON válido | Citações corretas | Acerto da recusa | Resposta sem suporte | Latência média (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 21 | 0.0% | 100.0% | N/A | 0.0% | 0.0% | 11.16 |
| rag | 21 | 19.0% | 100.0% | 62.5% | 80.0% | 0.0% | 31.21 |
| agent | 21 | 61.9% | 100.0% | 93.8% | 100.0% | 0.0% | 32.74 |

## Como interpretar

- `base` não recebe documentos; por isso, citação é `N/A`, não 0% nem 100%.
- Compare `rag` com `base` para observar o ganho da recuperação documental.
- Compare `agent` com `rag` para observar o efeito das regras especializadas.
- Uma taxa menor de respostas sem suporte nas perguntas sem resposta é desejável.
- A taxa automática de aprovação é uma aproximação baseada no gabarito; revise manualmente respostas e fontes antes da conclusão.
- O modo `rag` não recebe o bloqueio determinístico do agente; isso preserva a comparação experimental.
