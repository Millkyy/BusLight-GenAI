# BusLight GenAI — LLM local, RAG e agente especializado

Assistente de mobilidade em português para o projeto BusLight. Este repositório compara o mesmo modelo local em três configurações: **BASE sem contexto**, **RAG simples** e **RAG + agente especializado**.

> **Limite da demonstração:** esta versão responde sobre a documentação curada. Ela não acessa a posição/ETA ao vivo da SPTrans nem a câmera do ponto. Portanto, não deve inventar chegada, lotação ou segurança atual. A integração Olho Vivo deve ocorrer no backend por ferramenta separada, com timestamp.

## Entregáveis

- `docs/FICHA_TECNICA.md`: tarefa da IA, escopo, cidadão e limites.
- `arquitetura/pipeline.mmd`: diagrama do pipeline.
- `base/trechos.jsonl`: trechos documentais com IDs e fontes.
- `base/fontes.csv`: formato, licença/condições, acesso e contagem de trechos.
- `avaliacao/conjunto_teste.jsonl`: 21 perguntas e gabaritos, incluindo cinco casos de abstenção.
- `src/evaluate_retrieval.py`: Recall@1, Recall@3, HitRate e calibração de limiar.
- `src/evaluate_llm.py`: comparação das três configurações e geração do placar/respostas.
- `avaliacao/respostas_benchmark.jsonl`: respostas literais da execução incluída neste repositório.
- `avaliacao/placar_tres_configuracoes.csv` e `.md`: placar medido.
- `docs/ANALISE_DE_ERROS.md`: cinco erros reais observados, respostas literais, causas e correções propostas.
- `notebooks/01_pipeline_e_avaliacao.ipynb`: recuperação e análise dos resultados salvos.
- `docs/RELATORIO_TECNICO.md`: relatório da atividade.

## Requisitos

- Python 3.11 ou superior.
- Ollama instalado e em execução local.
- Memória suficiente para o modelo Qwen 2.5 3B; a primeira execução baixa o modelo.
- Verificar licença/condições do modelo antes de qualquer uso comercial.

## Reproduzir no Windows PowerShell

```powershell
# 1. Criar e ativar ambiente virtual
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependências
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Baixar o modelo local
ollama pull qwen2.5:3b

# 4. Medir a recuperação e o limiar
python -m src.evaluate_retrieval

# 5. Executar testes automatizados
python -m unittest discover -s tests -v

# 6. Executar benchmark completo (21 perguntas x 3 modos = 63 chamadas)
python -m src.evaluate_llm

# 7. Iniciar API local
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Depois de iniciar a API, abra:

- `http://127.0.0.1:8000/` — resumo e links da API.
- `http://127.0.0.1:8000/docs` — documentação interativa para testar `/assist`.
- `http://127.0.0.1:8000/health` — status e configuração.
- `http://127.0.0.1:8000/sources` — inventário de fontes.

No Windows, mantenha a janela do Uvicorn aberta enquanto testa a API. Use uma segunda janela PowerShell para executar chamadas HTTP.

## Exemplo de chamada

```powershell
$body = @{ question = "Como a API informa se um ônibus é acessível?"; mode = "agent" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/assist" -ContentType "application/json" -Body $body
```

## As três configurações

| Modo | Contexto | Especialização | Finalidade |
|---|---|---|---|
| `base` | Nenhum | Prompt genérico | Linha de base do mesmo modelo sem recuperação |
| `rag` | Top-3 trechos recuperados | Prompt documental RAG | Medir efeito do contexto documental |
| `agent` | Top-3 + limiar | Regras BusLight, política live, validação de citações | Medir efeito da especialização por agente |

O agente é a alternativa de especialização escolhida na rubrica; nenhum peso do LLM é atualizado (não é LoRA).

## Resultados da execução salva no repositório

Modelo: `qwen2.5:3b`; 21 perguntas por modo; 63 respostas no JSONL.

| Indicador | Base | RAG | Agent |
|---|---:|---:|---:|
| Aprovação | 0,0% (0/21) | 19,0% (4/21) | 61,9% (13/21) |
| JSON válido | 100% | 100% | 100% |
| Citações corretas em perguntas respondíveis | N/A | 62,5% (10/16) | 93,75% (15/16) |
| Acerto de abstenção | 0% (0/5) | 80% (4/5) | 100% (5/5) |
| Resposta sem suporte em cinco casos não respondíveis | 0% | 0% | 0% |
| Latência média | 11,16 s | 31,21 s | 32,74 s |

**Interpretação importante:** o indicador de resposta sem suporte acima considera exclusivamente as cinco perguntas marcadas como não respondíveis. Ele não detecta todas as afirmações factuais erradas em perguntas respondíveis. Por exemplo, a resposta BASE à Q10 inventou uma lista de princípios da LGPD; esse erro está registrado em `docs/ANALISE_DE_ERROS.md`. A taxa de aprovação automática usa conceitos e citações definidos manualmente; revise as respostas antes da conclusão.

O agente obteve 42,9 pontos percentuais a mais de aprovação que o RAG simples nesta execução, mas ainda teve falhas em perguntas documentais. O placar não deve ser descrito como prova de ausência de alucinação.

## Métricas de recuperação

Resultados salvos em `avaliacao/metricas_busca.json`:

- Recall@1: 83,3%.
- HitRate@1: 93,75%.
- Recall@3: 100%.
- HitRate@3: 100%.
- Limiar recomendado: 0,1224 (ponto médio entre score positivo mínimo 0,1321 e negativo máximo 0,1127).

## Segurança, LGPD e operação

- Tokens da SPTrans ficam apenas no backend, em variável de ambiente/secret manager; nunca versionar `.env`.
- Não versionar dados pessoais, imagens de passageiros ou logs identificáveis.
- A contagem sem reconhecimento facial e sem retenção de imagens está registrada como salvaguarda proposta; não é declaração de implementação ou aprovação jurídica.
- API vinculada a `127.0.0.1` por padrão. Não expor publicamente sem autenticação, TLS, rate limit, monitoramento e política de privacidade.
- A resposta operacional deve usar timestamp da fonte. Se Olho Vivo falhar, exibir indisponibilidade; nunca tratar cache antigo como “agora”.

## Testes automatizados

```powershell
python -m unittest discover -s tests -v
```

Na versão incluída no ZIP verificado, os 20 testes passaram. Os testes automatizados não substituem a avaliação do LLM com Ollama.

## Integrantes

Conforme a lista atualmente registrada pela equipe; confirmar nomes completos conforme cadastro acadêmico:

- Aline Zeppelini — RM 97966
- Camilly Ishida — RM 551474
- Julia Galvão — RM 550201

## Links para publicação

- Repositório informado: https://github.com/Millkyy/BusLight-GenAI.
- Vídeo de demonstração: https://youtu.be/PZOIDPzZQCc.
