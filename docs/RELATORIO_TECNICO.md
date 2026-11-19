# Relatório Técnico — Generative AI for Engineering
## BusLight Assist: assistente local fundamentado por RAG e agente especializado

**Disciplina:** Generative AI for Engineering  
**Atividade:** Treinamento de uma LLM local  
**Turma:** Engenharia de Software — 4º ano — 4ES  
**Integrantes:** preencher nome completo e RM de todos os integrantes  
**Professor:** Francisco Elanio Bezerra  
**Repositório:** `[URL pública do GitHub]`  
**Vídeo:** `[URL do vídeo, quando disponível]`

---

## 1. Resumo executivo

O BusLight é uma CitizenTech de mobilidade com foco no ponto de ônibus como espaço de espera e potencial exposição. Seu público prioritário são trabalhadores da periferia de São Paulo, passageiros noturnos, estudantes, mulheres, idosos e pessoas com deficiência visual. A atividade de IA foi recortada como um **assistente de informação e explicabilidade**: responde dúvidas sobre a arquitetura, os dados e as regras do BusLight usando trechos documentais identificados; reconhece limites; e se abstém quando a resposta exige dado operacional atual que não foi conectado.

A escolha evita uma falha crítica: um LLM não deve inventar ETA, lotação, atraso ou segurança atual. A posição e a previsão de chegada precisam vir da integração de transporte (por exemplo, Olho Vivo) com horário de atualização. O modelo local explica a informação recebida, mas não a substitui.

## 2. Problema e tarefa da IA

### Problema de mobilidade

Na periferia, o passageiro pode esperar longos períodos no ponto, muitas vezes de madrugada ou à noite, sem saber se o ônibus já passou, vai atrasar ou chegar lotado. Isso reduz previsibilidade e aumenta o tempo de exposição.

### Tarefa escolhida

Responder perguntas em português sobre:

- funcionamento e limites do BusLight;
- origem e interpretação dos dados do Olho Vivo e GTFS;
- acessibilidade indicada pelas fontes;
- uso de dados meteorológicos;
- privacidade, LGPD e salvaguardas de visão computacional;
- limites da demonstração e indisponibilidade de fontes.

### Perguntas fora do escopo

ETA atual, posição atual, lotação em tempo real, incidentes atuais e garantia de segurança. Sem integração operacional e timestamp, a resposta correta é abster-se. Também não se fornece conselho emergencial ou garantia de segurança individual.

## 3. Ficha técnica

A ficha completa está em [`FICHA_TECNICA.md`](FICHA_TECNICA.md). Em resumo: Qwen 2.5 3B executado localmente pelo Ollama; recuperação TF-IDF híbrida local; saída JSON; citações por chunk; modo de agente especializado.

## 4. Fontes e base de conhecimento

A base é composta por trechos curtos, com `chunk_id`, `source_id`, seção, texto e URL. O inventário completo está em [`../base/fontes.csv`](../base/fontes.csv) e os trechos em [`../base/trechos.jsonl`](../base/trechos.jsonl).

| Fonte | Formato | Condição/licença registrada | Trechos |
|---|---|---|---:|
| Briefing interno BusLight | Texto/Markdown | Material interno da equipe | 4 |
| SPTrans Olho Vivo — documentação | HTML/JSON exemplificativo | Gratuito mediante cadastro/token; sem licença aberta padronizada identificada; não redistribuir sem observar condições | 4 |
| SPTrans — condições de acesso | HTML | Não alugar, sublicenciar ou vender dados; disponibilidade/correção não garantidas | 1 |
| SPTrans — portal de desenvolvedor | HTML | Verificar termos do recurso específico | 0* |
| GTFS Schedule Reference | HTML | A referência não licencia os feeds dos operadores; verificar a licença do feed | 2 |
| Open-Meteo | HTML | Dados CC BY 4.0; atribuição obrigatória | 2 |
| Lei e orientação LGPD | HTML | Texto normativo e orientação pública | 2 |
| Censo 2022 — Dados Abertos SP | Catálogo de conjunto | CC BY 4.0 conforme catálogo | 1 |

`*` O portal foi registrado no inventário como fonte de descoberta, mas não gerou trecho isolado adicional. O total de trechos na base é **16**; a contagem por `source_id` também está explícita na coluna `chunk_count` de `base/fontes.csv`.

### Observações de licenciamento

- O cadastro de desenvolvedor da SPTrans informa acesso gratuito e restrições a aluguel, sublicenciamento e venda. O projeto deve conferir os termos atuais antes de publicar ou redistribuir dados brutos.
- O GTFS é uma especificação; a licença do arquivo GTFS da operadora deve ser tratada separadamente.
- Dados Open-Meteo requerem atribuição CC BY 4.0. Se o BusLight virar produto comercial ou elevar volume de chamadas, revisar os termos e plano aplicável.
- O catálogo de Censo 2022 registra CC BY 4.0; a equipe ainda deve documentar o arquivo/variáveis/recorte efetivamente utilizados.
- SSP-SP e GeoSampa são fontes previstas no conceito geral do BusLight, mas não foram incorporadas a esta base de IA porque o conjunto/endpoint, licença e trecho efetivamente utilizado ainda precisam ser fixados. Não se deve fazer afirmação criminal ou de iluminação atual com a base atual.

## 5. Arquitetura e pipeline

Ver [`../arquitetura/pipeline.mmd`](../arquitetura/pipeline.mmd) e [`../arquitetura/DECISOES_TECNICAS.md`](../arquitetura/DECISOES_TECNICAS.md).

1. Curadoria de documentos públicos e requisitos internos.
2. Registro de fonte, formato, condição de uso e URL.
3. Segmentação manual em 16 chunks rastreáveis.
4. Índice local TF-IDF: bigramas de palavras + n-gramas de caracteres.
5. Recuperação Top-3 com similaridade cosseno.
6. Três configurações com o mesmo Qwen local: base, RAG e agente.
7. Validação do JSON e das citações; o agente bloqueia respostas sem evidência e consultas que exigem fonte live não conectada.
8. Benchmark com gabarito e placar gerado em CSV/Markdown.

## 6. Estratégia de recuperação e métricas

O conjunto de avaliação possui 21 perguntas, incluindo cinco consultas sem resposta na base e que exigem “não consta”. Os rótulos `relevant_chunk_ids` foram definidos manualmente.

- Recall@1 = quantidade de rótulos relevantes encontrados no primeiro resultado / total de rótulos relevantes.
- Recall@3 = quantidade de rótulos relevantes encontrados entre os três primeiros / total de rótulos relevantes.
- HitRate@k = proporção de perguntas respondíveis que recuperam ao menos um chunk relevante no top-k.

A avaliação foi executada em `python -m src.evaluate_retrieval`, com os seguintes resultados registrados em `avaliacao/metricas_busca.json`:

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
| Limiar recomendado (ponto médio) | **0,1224** |

O limiar foi calculado no ponto médio entre o menor score positivo e o maior score negativo, pois houve separação no conjunto avaliado. As cinco perguntas sem resposta ou com necessidade de dado em tempo real são tratadas como abstenção antes da geração. As métricas de recuperação avaliam a seleção de trechos, **não** medem a qualidade final das respostas do LLM.

## 7. Geração fundamentada e proteção contra alucinação

Todas as configurações usam contrato JSON com `status`, `answer`, `citations` e `reason`. A geração é executada localmente por Ollama.

- **Base:** mesmo modelo, sem contexto documental.
- **RAG simples:** Top-3 trechos anexados ao prompt e instrução para citar fontes; não tem bloqueio forte por limiar nem verificador pós-geração.
- **Agente:** mesmas fontes e modelo, mas adiciona política de domínio BusLight, recusa para consultas de dados em tempo real não conectados, limiar de recuperação, validação de citações contra os chunks recuperados e substituição por abstenção quando a citação não é verificável.

O agente não é LoRA e não altera pesos. É uma especialização por agente — alternativa descrita na rubrica. O desenho facilita explicar a decisão, manter rastreabilidade e controlar informações que podem afetar a segurança do cidadão.

## 8. Placar das três configurações

O benchmark completo é gerado por `python -m src.evaluate_llm`. Arquivos:

- `avaliacao/placar_tres_configuracoes.csv`
- `avaliacao/placar_tres_configuracoes.md`
- `avaliacao/respostas_benchmark.jsonl`

**O placar de inferência ainda não foi preenchido porque o runtime Ollama não estava instalado/disponível no ambiente de preparação.** Não foram inventadas acurácias ou respostas. O script está implementado; depois de executar o benchmark no computador com Ollama, registrar os valores e interpretar:

1. ganho de RAG sobre o baseline sem contexto;
2. ganho do agente sobre o RAG simples;
3. queda de respostas sem suporte nos quatro testes “não consta”;
4. trade-off de latência;
5. casos em que o agente se absteve corretamente ou recusou demais.

## 9. Cinco erros e correções propostas

A tabela em [`ANALISE_DE_ERROS.md`](ANALISE_DE_ERROS.md) contém cinco cenários reproduzíveis, causa provável e correção proposta. **Eles ainda são cenários de falha a confirmar, não cinco erros observados**. Para cumprir literalmente “erros reais” na rubrica, a equipe deve executar o modelo, anexar a resposta literal de cada falha e registrar antes/depois.

## 10. LGPD e IA responsável

A demonstração não precisa de dados pessoais. O assistente não solicita nome, CPF, endereço residencial ou localização exata. O token da SPTrans é exclusivamente segredo de backend. Perguntas não são persistidas por padrão.

Para a câmera do ponto, o requisito recomendado é contagem agregada sem reconhecimento facial, sem retenção de imagens e com transparência ao cidadão. Isso é uma decisão de projeto proposta; não significa que o tratamento já esteja validado. Antes do piloto, a equipe deve avaliar base legal, finalidade, necessidade, retenção, acesso, aviso, segurança e riscos aos titulares.

O modelo não fornece garantia de segurança individual nem transforma estatísticas criminais agregadas em recomendações definitivas. A ferramenta de IA deve permanecer explicável e sujeita a revisão humana em decisões que afetem o cidadão.

## 11. Limitações

- O runtime do LLM e o benchmark das três configurações ainda precisam ser executados localmente. As métricas de recuperação já foram medidas; elas não substituem o benchmark de geração.
- A API Olho Vivo não foi conectada nesta entrega e nenhuma credencial foi incluída.
- A câmera/YOLO e dados de lotação não estão conectados.
- A base não inclui ainda arquivos de dados brutos do GTFS, SSP-SP ou GeoSampa; o inventário explicita isso.
- Métricas automáticas de conceito são proxies e exigem auditoria humana.

## 12. Conclusão técnica

O recorte de GenAI do BusLight é uma camada de orientação fundamentada, não o mecanismo responsável por inventar previsões de transporte. A arquitetura local de RAG + agente torna possível rastrear cada resposta, mostrar a fonte, declarar limites e abster-se quando faltar evidência. A comparação justa entre modelo sem contexto, RAG e agente será concluída com o benchmark executado no mesmo ambiente e com as mesmas perguntas. A principal condição para produção é integrar a fonte operacional por ferramenta autenticada e timestampada, sem expor segredos nem dados pessoais ao LLM.

## 13. Links finais

- GitHub: `[INSERIR URL PÚBLICA]`
- Demonstração da API: `[INSERIR URL OU VÍDEO]`
- Vídeo pitch/demonstração: `[INSERIR LINK]`
