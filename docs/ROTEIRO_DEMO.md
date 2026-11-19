# Roteiro de demonstração — BusLight Assist (2 a 3 minutos)

1. **Contexto (15 s):** explicar que o BusLight busca reduzir o tempo de espera e exposição no ponto, sobretudo à noite.
2. **Base e fonte (25 s):** mostrar `base/trechos.jsonl` e `base/fontes.csv`; abrir um chunk SPT-003 e apontar sua origem.
3. **Resposta fundamentada (30 s):** chamar `/assist` com “O que a API de previsão da SPTrans retorna?”; mostrar JSON, citação e trecho.
4. **Abstenção segura (30 s):** perguntar “Qual a lotação exata do ponto agora?” e mostrar `status=abstained`, explicando que a câmera/telemetria ainda não está conectada.
5. **Comparação (30 s):** abrir o placar das três configurações depois de executar `python -m src.evaluate_llm`; comparar base, RAG e agente sem inventar números.
6. **Encerramento (20 s):** reforçar que ETA vem do Olho Vivo, que a IA não inventa dados, e mencionar proteção de dados/LGPD.

Gravar a tela com o terminal/Swagger e a voz de um integrante. Não mostrar tokens, `.env`, dados pessoais ou imagens identificáveis de passageiros. Inserir o link do vídeo no relatório e no README.
