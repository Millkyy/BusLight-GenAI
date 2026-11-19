# Checklist de submissão — Generative AI for Engineering

| Critério da rubrica | Evidência no pacote | Situação real |
|---|---|---|
| Tarefa da IA e casos com gabarito, incluindo “não consta” (0,5) | `docs/FICHA_TECNICA.md` + `avaliacao/conjunto_teste.jsonl` (21 casos) | Preparado; gabaritos incluídos |
| Base de conhecimento em trechos com fonte (1,0) | `base/trechos.jsonl` + `base/fontes.csv` | Preparado; 16 trechos e inventário das fontes |
| Recall@1, Recall@3 e limiar justificado (1,0) | `src/evaluate_retrieval.py` + `avaliacao/metricas_busca.json` | **Medido:** Recall@1 83,3%; Recall@3 100%; limiar 0,1224 |
| Geração fundamentada: JSON válido, citação e recusa (2,0) | `src/schemas.py`, `src/agent.py`, `src/policies.py`, testes e API | Código implementado; teste unitário passa. Validar a saída do LLM com Ollama ainda pendente |
| Especialização LoRA ou agente comparada ao RAG simples (2,0) | Modos `base`, `rag` e `agent` usando o mesmo modelo configurado | Agente implementado como especialização; comparação por inferência real pendente |
| Placar das três configurações, com interpretação (2,0) | `src/evaluate_llm.py` gera CSV, Markdown e respostas brutas | Pendente: este ambiente não tem Ollama disponível, portanto não há scores inventados |
| Cinco erros reais com proposta de correção (1,0) | `docs/ANALISE_DE_ERROS.md` | Cinco cenários de falha definidos; é obrigatório executar o LLM e registrar cinco saídas reais antes de afirmar cumprimento integral |
| README e reprodutibilidade (0,5) | `README.md`, `requirements.txt`, notebook com saídas, API e testes | Preparado; sete testes unitários passam. Confirmar em máquina limpa com Ollama |

## Evidências já verificadas

- `python -m src.evaluate_retrieval`: executado; métricas persistidas em `avaliacao/metricas_busca.json`.
- `python -m unittest discover -s tests -v`: **7 testes aprovados**.
- API FastAPI: `/health` e `/sources` responderam HTTP 200 no teste local; `/assist` recusou corretamente uma pergunta de segurança atual que exige dados não conectados.
- Notebook `notebooks/01_pipeline_e_avaliacao.ipynb`: incluído com saídas salvas.

## Antes de enviar ao professor

- [ ] Preencher nome completo e RM de **todos** os integrantes no README e no relatório.
- [ ] Instalar/iniciar Ollama, executar `ollama pull qwen2.5:3b` e rodar `python -m src.evaluate_llm`.
- [ ] Revisar o placar das três configurações: acurácia/qualidade, respostas sem suporte, recusas corretas e latência.
- [ ] Registrar cinco erros realmente observados com pergunta, resposta literal, configuração, causa confirmada e correção; manter evidência antes/depois.
- [ ] Rodar o notebook do início ao fim no ambiente final e conferir as saídas.
- [ ] Criar repositório GitHub público e inserir URL no README/relatório.
- [ ] Gravar a demonstração e inserir o link do vídeo no relatório.
- [ ] Conferir as licenças e condições de uso das fontes antes de qualquer redistribuição ou uso comercial.
- [ ] Enviar o link do repositório no Teams.

> **Importante:** o pacote cobre a estrutura e os artefatos exigidos, mas não é correto afirmar que os 10 pontos estão garantidos enquanto o benchmark de inferência, os cinco erros reais, os dados dos integrantes e os links públicos não forem completados.
