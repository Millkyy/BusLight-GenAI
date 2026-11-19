# BusLight GenAI — RAG local + agente especializado

Assistente de mobilidade em português para o projeto BusLight. Este repositório implementa uma comparação controlada entre **LLM sem contexto**, **RAG simples** e **RAG + agente especializado**, usando o mesmo modelo local.

> **Importante:** o módulo responde sobre a documentação curada. Ele não acessa a posição/ETA ao vivo da SPTrans nem a câmera do ponto nesta versão. Portanto, não deve inventar chegada, lotação ou segurança atual. A integração com Olho Vivo deve ocorrer no backend por ferramenta separada.

## Entregáveis do desafio

- `docs/FICHA_TECNICA.md`: tarefa da IA, escopo, cidadão e limites.
- `arquitetura/pipeline.mmd`: diagrama do pipeline.
- `base/trechos.jsonl`: trechos com IDs e fontes.
- `base/fontes.csv`: formato, licença/condições, acesso e contagem de trechos por fonte.
- `avaliacao/conjunto_teste.jsonl`: perguntas, gabaritos e casos “não consta”.
- `src/evaluate_retrieval.py`: mede Recall@1, Recall@3, HitRate e calibra o limiar.
- `src/evaluate_llm.py`: compara as três configurações e gera placar e respostas brutas.
- `docs/ANALISE_DE_ERROS.md`: cinco cenários de falha reproduzíveis e plano para registrar erro real.
- `docs/ROTEIRO_DEMO.md`: roteiro curto para gravar a demonstração.
- `notebooks/01_pipeline_e_avaliacao.ipynb`: demonstração executável de recuperação e avaliação.
- `docs/RELATORIO_TECNICO.md`: relatório solicitado para GitHub.

## Requisitos

- Python 3.11 ou superior.
- Ollama instalado e em execução local.
- Memória suficiente para o modelo Qwen 2.5 3B. A primeira execução pode baixar o modelo.
- Verifique a licença do modelo Qwen 2.5 3B antes de uso comercial; a distribuição indicada na página do modelo usa a Qwen Research License.

## Reproduzir

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# 2. Instale dependências
pip install -r requirements.txt

# 3. Baixe/prepare o modelo local
ollama pull qwen2.5:3b

# 4. Meça busca, recall e limiar
python -m src.evaluate_retrieval

# 5. Rode os testes unitários
python -m unittest discover -s tests -v

# 6. Rode o benchmark das três configurações
python -m src.evaluate_llm

# 7. Suba a API local
uvicorn src.api:app --host 127.0.0.1 --port 8000

Depois de iniciar a API, abra `http://127.0.0.1:8000/` para ver os links, ou `http://127.0.0.1:8000/docs` para testar os endpoints.
```

A etapa 5 faz 3 chamadas por caso do conjunto de teste; pode levar alguns minutos conforme o hardware. Os resultados reais são escritos em `avaliacao/placar_tres_configuracoes.csv`, `avaliacao/placar_tres_configuracoes.md` e `avaliacao/respostas_benchmark.jsonl`.

### Exemplo de chamada

```bash
curl -X POST http://127.0.0.1:8000/assist \
  -H "Content-Type: application/json" \
  -d '{"question":"Como consigo o token do Olho Vivo?","mode":"agent"}'
```

No Windows PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/assist `
  -ContentType 'application/json' `
  -Body '{"question":"Como consigo o token do Olho Vivo?","mode":"agent"}'
```

## As três configurações

| Modo | Contexto | Especialização | Finalidade |
|---|---|---|---|
| `base` | Nenhum | Prompt genérico | Linha de base do mesmo modelo sem RAG |
| `rag` | Top-3 trechos recuperados | Prompt RAG simples | Medir ganho de contexto documental |
| `agent` | Top-3 + limiar | Regras BusLight, recusa para dados ao vivo, JSON e verificador de citação | Medir ganho da especialização |

A especialização escolhida foi **agente**, alternativa prevista na rubrica, em vez de LoRA. Nenhum peso é atualizado; a comparação isola o efeito da recuperação e da camada de agente.

## Métricas

- **Recall@k:** total de trechos relevantes recuperados entre os k primeiros / total de rótulos relevantes manuais.
- **HitRate@k:** proporção de perguntas respondíveis com ao menos um trecho relevante no top-k.
- **Aprovação do caso:** JSON válido + decisão correta entre responder/abster-se + conceitos obrigatórios presentes + citação relevante nas perguntas respondíveis.
- **Taxa de resposta sem suporte:** fração das perguntas “não consta” em que o modelo respondeu mesmo assim. É um proxy de alucinação, não uma medição semântica perfeita.
- **Latência média:** tempo medido por chamada no mesmo ambiente.

O gabarito de relevância é manual e deve ser revisado por uma pessoa. Não trate métricas automáticas como prova definitiva de factualidade.

## Segurança, LGPD e operação

- Tokens da SPTrans ficam apenas no backend, em variável de ambiente/secret manager.
- Não versionar `.env`, tokens, imagens de passageiros, endereços residenciais ou logs identificáveis.
- A demonstração não precisa de dado pessoal. Não pedir CPF, nome ou localização residencial ao passageiro.
- A contagem de pessoas foi especificada sem reconhecimento facial e sem retenção de imagem como salvaguarda proposta; antes de piloto, validar base legal, aviso, retenção, acesso e avaliação de impacto.
- API vinculada a `127.0.0.1` por padrão. Não expor publicamente sem autenticação, TLS, rate limit, monitoramento e política de privacidade.
- A resposta operacional deve sempre mostrar timestamp da fonte. Se API falhar, exibir indisponibilidade; nunca transformar cache antigo em “agora”.

## Limitações e próximos passos

1. Conectar backend ao Olho Vivo com token de servidor e injetar previsão + timestamp como ferramenta autorizada.
2. Integrar contagem agregada do YOLO sem armazenar frames, após revisão de privacidade.
3. Ampliar base com arquivo GTFS real da SPTrans, registrando versão, extração, licença do feed e número de trechos derivados.
4. Aumentar o conjunto de teste com casos reais anonimizados e validação de passageiros.
5. Executar o benchmark local, preencher resultados e substituir os cinco cenários de falha por cinco saídas reais do modelo.

## Testes automatizados

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem roteamento de perguntas por política e recuperação de trechos. Eles não substituem a execução do benchmark LLM.

## Integrantes

Preencher todos os integrantes com **nome completo e RM** antes da entrega. Não foram inventados nomes nem RMs.

- `Aline Zeppelini` — `RM97966`
- `Camilly Ishida` — `RM551474`
- `Julia Galvão` — `RM550201`
