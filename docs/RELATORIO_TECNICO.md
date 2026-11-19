# Relatório Técnico — Generative AI for Engineering
## BusLight Assist: assistente local fundamentado por RAG e agente especializado

**Disciplina:** Generative AI for Engineering  
**Atividade:** Treinamento de uma LLM local  
**Turma:** Engenharia de Software — 4º ano — 4ES  
**Professor:** Francisco Elanio Bezerra  
**Integrantes (conforme identificação já registrada no README):** Aline Zeppelini — RM 97966; Camilly Ishida — RM 551474; Julia Galvão — RM 550201. **Antes do envio, confirmar se os nomes estão completos e grafados exatamente como no cadastro acadêmico.**  
**Vídeo:** `[]`  
**Repositório informado:** https://github.com/Millkyy/BusLight-GenAI.

---

## 1. Resumo executivo

O BusLight é uma CitizenTech de mobilidade com foco no ponto de ônibus como espaço de espera e potencial exposição. Seu público prioritário são trabalhadores da periferia de São Paulo, passageiros noturnos, estudantes, mulheres, idosos e pessoas com deficiência visual. A atividade de IA foi recortada como um **assistente de informação e explicabilidade**: responde dúvidas sobre a arquitetura, os dados e as regras do BusLight usando trechos documentais identificados; reconhece limites; e se abstém quando a resposta exige dado operacional atual que não foi conectado.

A regra de segurança central é que o LLM não inventa ETA, lotação, atraso ou segurança atual. A posição e a previsão de chegada dependem de integração operacional (por exemplo, Olho Vivo) com horário de atualização. Nesta demonstração a API Olho Vivo e a câmera/YOLO não estão conectadas.

## 2. Problema e tarefa da IA

### Problema de mobilidade

Na periferia, o passageiro pode esperar longos períodos no ponto, muitas vezes de madrugada ou à noite, sem saber se o ônibus já passou, vai atrasar ou chegar lotado. Isso reduz previsibilidade e aumenta o tempo de exposição.

### Tarefa escolhida

Responder perguntas em português sobre:

- funcionamento e limites do BusLight;
- origem e interpretação dos dados do Olho Vivo e GTFS;
- acessibilidade indicada pelas fontes;
- uso de dados meteorológicos;
- privacidade, LGPD e salvaguardas propostas para visão computacional;
- limites da demonstração e indisponibilidade de fontes.

### Perguntas fora do escopo

ETA atual, posição atual, lotação em tempo real, incidentes atuais e garantia de segurança. Sem integração operacional e timestamp, a resposta correta é abster-se. Também não se fornece conselho emergencial ou garantia de segurança individual.

## 3. Ficha técnica

A ficha completa está em [`FICHA_TECNICA.md`](FICHA_TECNICA.md). Em resumo: Qwen 2.5 3B executado localmente pelo Ollama; recuperação TF-IDF híbrida local; saída JSON; citações por chunk; modos base, RAG simples e agente especializado. A especialização escolhida é por agente, uma das alternativas previstas na rubrica; não foram atualizados pesos por LoRA.

## 4. Fontes e base de conhecimento

A base contém **16 trechos** curados, cada um com `chunk_id`, `source_id`, seção, texto e URL. Inventário completo: [`../base/fontes.csv`](../base/fontes.csv); trechos: [`../base/trechos.jsonl`](../base/trechos.jsonl).

| Fonte | Formato | Condição/licença registrada | Trechos |
|---|---|---|---:|
| Briefing interno BusLight | Texto/Markdown | Material interno da equipe | 4 |
| SPTrans Olho Vivo — documentação | HTML/JSON exemplificativo | Gratuito mediante cadastro/token; sem licença aberta padronizada identificada; observar condições de uso | 4 |
| SPTrans — condições de acesso | HTML | Não alugar, sublicenciar ou vender dados; disponibilidade/correção não garantidas | 1 |
| SPTrans — portal de desenvolvedor | HTML | Verificar termos do recurso específico | 0* |
| GTFS Schedule Reference | HTML | A referência não licencia os feeds dos operadores; verificar a licença do feed | 2 |
| Open-Meteo | HTML | Dados CC BY 4.0; atribuição obrigatória | 2 |
| Lei e orientação LGPD | HTML | Texto normativo e orientação pública | 2 |
| Censo 2022 — Dados Abertos SP | Catálogo de conjunto | CC BY 4.0 conforme catálogo | 1 |

`*` Fonte de descoberta registrada no inventário, sem trecho independente adicional. Total: **16 trechos**. A coluna `chunk_count` em `base/fontes.csv` registra a distribuição por fonte.

### Observações de licenciamento

- O cadastro de desenvolvedor da SPTrans informa acesso gratuito e restrições a aluguel, sublicenciamento e venda. Conferir termos atuais antes de publicar ou redistribuir dados brutos.
- O GTFS é uma especificação; a licença do feed de cada operadora deve ser tratada separadamente.
- Open-Meteo requer atribuição CC BY 4.0. Uso comercial e volume de chamadas devem observar os termos/plano aplicáveis.
- O catálogo de Censo 2022 registra CC BY 4.0; para uso de tabela específica, documentar arquivo, variáveis, recorte e data de extração.
- SSP-SP e GeoSampa são fontes previstas no conceito geral do BusLight, mas não foram incorporadas a esta base de IA porque conjunto/endpoint, licença e trechos efetivamente usados ainda precisam ser definidos. Não fazer afirmações atuais sobre criminalidade ou iluminação com a base presente.

## 5. Arquitetura e pipeline

Ver [`../arquitetura/pipeline.mmd`](../arquitetura/pipeline.mmd) e [`../arquitetura/DECISOES_TECNICAS.md`](../arquitetura/DECISOES_TECNICAS.md).

1. Curadoria de documentos públicos e requisitos internos.
2. Registro de fonte, formato, condição de uso e URL.
3. Segmentação em 16 chunks rastreáveis.
4. Índice local TF-IDF híbrido: bigramas de palavras e n-gramas de caracteres.
5. Recuperação Top-3 com similaridade cosseno.
6. Três configurações com o mesmo Qwen local: base, RAG e agente.
7. Validação do JSON e das citações; o agente adiciona política de domínio, limiar e abstenção para dados live não conectados.
8. Benchmark com gabarito e placar gerado em CSV/Markdown.

## 6. Estratégia de recuperação e métricas

O conjunto de avaliação possui **21 perguntas**: 16 respondíveis com a base e cinco casos que exigem “não consta”/abstenção. Os rótulos `relevant_chunk_ids` foram definidos manualmente.

- **Recall@k:** trechos relevantes encontrados nos k primeiros resultados / total de rótulos relevantes.
- **HitRate@k:** proporção de perguntas respondíveis com ao menos um chunk relevante no top-k.

Resultados medidos em `avaliacao/metricas_busca.json`:

| Métrica | Resultado |
|---|---:|
| Recall@1 | **83,3%** |
| HitRate@1 | **93,75%** |
| Recall@3 | **100%** |
| HitRate@3 | **100%** |
| Perguntas respondíveis | 16 |
| Rótulos de relevância | 18 |
| Menor score top-1 positivo | 0,1321 |
| Maior score top-1 negativo | 0,1127 |
| Limiar recomendado | **0,1224** |

O limiar é o ponto médio entre o menor score positivo e o maior score negativo no conjunto avaliado. Houve separação entre esses valores nessa amostra. As consultas marcadas como dependentes de dados atuais são encaminhadas à regra de abstenção antes da geração. Essas métricas medem recuperação, não precisão semântica da resposta final.

## 7. Geração fundamentada e proteção contra alucinação

As três configurações usam o modelo local `qwen2.5:3b`, temperatura 0 e seed 42, com contrato JSON contendo `status`, `answer`, `citations` e `reason`.

- **Base:** mesmo modelo sem contexto documental.
- **RAG simples:** Top-3 chunks anexados ao prompt e instrução de fundamentação/citação.
- **Agente:** recuperação + política BusLight, bloqueio de perguntas live não conectadas, limiar e validação de citações contra chunks recuperados. A especialização é por agente; pesos não são atualizados.

O modo base é um controle experimental; suas respostas não devem ser usadas como orientação ao passageiro. Uma resposta “Não consta” com `status=answered` é uma inconsistência de saída, mesmo que o texto pareça recusar.

## 8. Placar das três configurações

O ZIP recebido contém 63 respostas salvas em `avaliacao/respostas_benchmark.jsonl` (21 perguntas por configuração) e o placar em CSV/Markdown. Resultados desta execução:

| Configuração | Aprovação | JSON válido | Citações corretas* | Acerto das recusas** | Resposta sem suporte** | Latência média |
|---|---:|---:|---:|---:|---:|---:|
| Base | **0/21 (0,0%)** | 100,0% | N/A | **0/5 (0,0%)** | 0/5 (0,0%) | 11,16 s |
| RAG | **4/21 (19,0%)** | 100,0% | **10/16 (62,5%)** | **4/5 (80,0%)** | 0/5 (0,0%) | 31,21 s |
| Agent | **13/21 (61,9%)** | 100,0% | **15/16 (93,75%)** | **5/5 (100,0%)** | 0/5 (0,0%) | 32,74 s |

\* Citações calculadas apenas nas 16 perguntas respondíveis; para BASE não se aplica porque não recebe documentos.  
\** Recusas e respostas sem suporte calculadas apenas nas cinco perguntas rotuladas como não respondíveis/operacionais.

### Interpretação

- O agente obteve **+42,9 pontos percentuais** de aprovação em relação ao RAG (61,9% contra 19,0%) e nove casos aprovados a mais nesta amostra.
- A taxa de citações corretas do agente foi 93,75%, contra 62,5% no RAG, diferença de 31,25 pontos percentuais.
- O agente acertou a abstenção nos cinco casos não respondíveis; o RAG acertou quatro de cinco; o modo base apresentou inconsistência entre texto de recusa e campo `status` nos casos avaliados.
- O custo de latência médio do agente foi 1,53 s acima do RAG nesta execução.
- O modo base teve 0% de aprovação automática. Além disso, a auditoria identificou uma resposta factual inventada na Q10. Isso evidencia o risco de responder sem contexto.
- **Limitação da métrica de alucinação:** `unsupported_answer_rate` do placar considera apenas as cinco perguntas marcadas como não respondíveis. Portanto, o valor 0% não significa ausência de qualquer afirmação sem suporte nas perguntas respondíveis. A resposta BASE Q10 foi identificada manualmente como erro factual e está documentada em `ANALISE_DE_ERROS.md`.

A amostra possui 21 perguntas, com gabaritos e conceitos definidos manualmente. A taxa automática de aprovação é proxy de aderência ao gabarito, não avaliação humana completa. As respostas devem ser revisadas quanto a significado, fonte e contradições.

## 9. Cinco erros reais e propostas de correção

Cinco falhas efetivamente observadas nas respostas salvas foram documentadas em [`ANALISE_DE_ERROS.md`](ANALISE_DE_ERROS.md):

1. BASE Q10: inventou princípios da LGPD sem apoio documental.
2. RAG Q01: colocou IDs de chunks no campo `answer` em vez de explicar o ETA.
3. RAG Q07: respondeu “Não consta” apesar de recuperar SPT-004, que contém a informação sobre acessibilidade.
4. AGENT Q15: declarou que a informação não estava disponível apesar de citar IBGE-001, que contém os dados e a licença.
5. RAG Q19: retornou `answer` vazio e citações sem pertinência para a pergunta.

As causas e correções propostas estão descritas junto às respostas literais. **As propostas ainda precisam ser implementadas/testadas**; não afirmar que as falhas foram corrigidas sem uma nova execução antes/depois.

## 10. LGPD e IA responsável

A demonstração não precisa de dados pessoais. O assistente não solicita nome, CPF, endereço residencial ou localização exata. O token da SPTrans deve permanecer exclusivamente no backend, fora do código e das respostas públicas.

Para a câmera do ponto, a proposta é contagem agregada sem reconhecimento facial e sem retenção de imagens; trata-se de salvaguarda de projeto, não de funcionalidade implementada ou validação jurídica concluída. Antes do piloto, avaliar base legal, finalidade, necessidade, aviso, retenção, acesso, segurança e riscos aos titulares.

O modelo não fornece garantia de segurança individual nem transforma estatísticas agregadas em recomendações definitivas. A ferramenta deve permanecer explicável e sujeita a revisão humana em decisões que afetem o cidadão.

## 11. Limitações

- A API Olho Vivo não foi conectada nesta entrega; não há ETA, posição ou previsão operacional live.
- A câmera/YOLO e lotação atual não estão conectadas.
- A base não inclui arquivos brutos do GTFS, SSP-SP ou GeoSampa; a tabela de fontes deixa isso explícito.
- Métricas automáticas de conceitos são proxies e precisam de revisão humana.
- Os resultados do placar correspondem à execução salva no ZIP. Se código, prompt ou gabarito forem alterados, executar novamente o benchmark e substituir os resultados antes da publicação final.

## 12. Conclusão técnica

Nesta execução, o agente especializado apresentou a maior aprovação automática (61,9%), a maior taxa de citações corretas (93,75%) e acertou todas as cinco abstenções esperadas. O resultado supera o RAG simples em 42,9 pontos percentuais de aprovação, com aumento médio de latência de 1,53 s. O baseline sem contexto teve 0% de aprovação, e a revisão manual identificou uma resposta com princípios da LGPD não sustentados pela base.

Os resultados apoiam a escolha de uma camada de agente sobre RAG para o recorte do BusLight, mas **não provam ausência geral de alucinações**: o indicador automático de respostas sem suporte mede somente os cinco casos não respondíveis. A auditoria manual e os erros descritos mostram por que a avaliação semântica continua necessária. Para produção, o BusLight deve integrar fontes operacionais por ferramentas autenticadas e timestampadas, sem expor segredos nem dados pessoais ao LLM.

## 13. Links finais

- GitHub informado pela equipe: https://github.com/Millkyy/BusLight-GenAI (confirmar visibilidade pública e atualização final).
- Vídeo de demonstração: `PREENCHER COM LINK DO VÍDEO NÃO LISTADO`.
- API local para gravação de demonstração: `http://127.0.0.1:8000/docs` (não é URL pública).
