# Decisões técnicas

1. **Modelo único nas três configurações:** `qwen2.5:3b` servido localmente pelo Ollama; temperatura 0 e seed 42. O mesmo modelo, parâmetros e conjunto de teste são usados em base, RAG e agente.
2. **Especialização por agente, não LoRA:** a rubrica permite LoRA ou agente. O agente adiciona política de domínio, bloqueio de perguntas que exigem dado ao vivo, limiar de recuperação, saída estruturada e verificador de citação. Os pesos do LLM não são alterados.
3. **Recuperação local:** TF-IDF híbrido de palavras (1–2 gramas) e caracteres (3–5 gramas). Para este corpus pequeno e controlado, reduz custo, dispensa serviço externo e é fácil de reproduzir. A limitação semântica deve ser observada; embeddings multilíngues podem ser avaliados numa evolução.
4. **Separação entre LLM e dados operacionais:** o LLM não calcula ETA. A aplicação deve obter previsão/posição da API operacional e só então entregar o resultado como contexto de ferramenta. Esta demonstração não contém credencial nem integração live.
5. **Abstenção:** casos que pedem lotação/posição/ETA/ocorrências/segurança atuais são recusados enquanto não houver ferramenta conectada. Também há recusa quando a similaridade top-1 fica abaixo do limiar.
6. **LGPD desde o desenho:** não enviar imagens, localização precisa ou identificadores pessoais ao LLM; não registrar perguntas por padrão; manter token no ambiente; contar pessoas sem reconhecimento facial como requisito de privacidade proposto, sujeito a validação jurídica e técnica.
7. **Avaliação:** rótulos de relevância do conjunto de teste são manuais e versionados. Recall@k é computado apenas sobre perguntas respondíveis. O limiar é calibrado com scores positivos e negativos do mesmo conjunto, e deve ser revisto com dados reais.
