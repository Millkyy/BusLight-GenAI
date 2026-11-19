# Ficha Técnica — BusLight Assist

| Campo | Descrição |
|---|---|
| Produto | BusLight — assistente de mobilidade e informação do ponto |
| Domínio | Mobilidade urbana, ônibus, acessibilidade e privacidade |
| Cidadãos beneficiados | Trabalhadores periféricos, passageiros noturnos, estudantes, mulheres, idosos e pessoas com deficiência visual |
| Problema | Espera prolongada no ponto sem informação confiável sobre chegada, atraso ou lotação, com maior exposição em horários noturnos |
| Tarefa da IA | Responder dúvidas sobre o funcionamento do BusLight e explicar, com fonte, dados e conceitos de mobilidade que constem na base; reconhecer ausência de evidência e se abster |
| Fora do escopo | Gerar ETA, informar lotação atual, afirmar que um ponto é seguro, reportar ocorrência atual ou substituir API operacional, central de emergência ou agente público |
| Modelo | Qwen 2.5 3B local via Ollama (`qwen2.5:3b`) |
| Estratégia RAG | TF-IDF híbrido local (palavras + caracteres), Top-3, fonte e chunk identificáveis |
| Especialização | Agente com política de mobilidade, limiar, regra de abstenção, contrato JSON e validação de citação |
| Idioma | Português brasileiro |
| Saída | JSON com `status`, `answer`, `citations` e `reason` |
| Dados usados | Especificação fornecida pela equipe e páginas/documentações públicas listadas em `base/fontes.csv` |
| Dados pessoais | Não necessários para responder; não devem ser solicitados nem persistidos por padrão |
| Integração futura | API Olho Vivo via backend; o backend injeta resposta com timestamp como ferramenta, nunca um token no prompt do passageiro |
| Limitação | A demonstração não conecta o Olho Vivo nem câmera; a base estática não tem ETA/lotação atual |

## Critério de sucesso

O agente deve aumentar respostas corretas e fundamentadas em relação ao mesmo modelo sem contexto e ao RAG simples, produzir JSON válido, citar trechos existentes e se abster em consultas sem evidência ou dependentes de dados atuais não conectados.
