"""Três configurações experimentais: base, RAG simples e agente especializado."""
import re
from .config import RETRIEVAL_THRESHOLD, TOP_K, OLLAMA_MODEL
from .knowledge import load_sources
from .retrieval import Retriever
from .llm import generate
from .schemas import AssistantResponse
from .policies import requires_live_data

retriever = Retriever()
sources = load_sources()

BASE_SYSTEM = """
Você é um assistente de mobilidade urbana.

Responda em português.

Nesta configuração você NÃO recebeu documentos
de referência.

Tente responder usando seu conhecimento prévio,
sem fingir que consultou fontes externas.

Não invente informações específicas do BusLight.

Não invente previsões, horários de chegada,
lotação, posição atual de veículos ou
condições atuais de segurança.

Se não souber responder, diga "Não consta".

Como não recebeu documentos, o campo citations
deve ser uma lista vazia.

Responda somente no JSON:
status, answer, citations, reason.
"""
RAG_SYSTEM = """
Você é o assistente do BusLight.

Responda em português claro e utilizando exclusivamente
as informações dos trechos documentais fornecidos.

REGRAS:

1. Se os trechos contiverem a resposta, responda.
2. Não se recuse a responder perguntas conceituais ou
   documentais que estejam cobertas pela base.
3. Se a resposta não estiver documentada, use status="abstained".
4. Não invente dados de previsão, lotação, segurança ou
   ocorrências atuais.
5. Não invente fontes ou identificadores.
6. Toda resposta factual deve possuir citações.
7. Coloque o texto explicativo no campo answer.
8. Os identificadores dos documentos devem aparecer
   somente no campo citations.
9. Nunca coloque textos como [CHUNK_ID: ...] no campo answer.
10. Não contradiga as informações fornecidas.

Se a pergunta estiver documentada:
status = "answered"

Se a pergunta não estiver documentada:
status = "abstained"

Responda somente no JSON:
status, answer, citations, reason.
"""

AGENT_SYSTEM = """
Você é o BusLight Assist, um agente especializado em
mobilidade urbana e acessibilidade no transporte público.

Responda em português claro, com frases completas e objetivas.

DISTINÇÃO ENTRE PERGUNTAS:

1. PERGUNTAS DOCUMENTAIS:
São perguntas sobre APIs, GTFS, LGPD, acessibilidade,
privacidade, licenças e funcionamento do BusLight.

Quando houver informação nos trechos recuperados,
VOCÊ DEVE RESPONDER.

Não confunda falta de informação em tempo real com
falta de documentação.

2. PERGUNTAS OPERACIONAIS:
São perguntas sobre lotação atual, chegada exata do ônibus,
posição atual, ocorrências recentes e segurança atual.

Como não existem ferramentas operacionais conectadas,
VOCÊ DEVE SE RECUSAR A INVENTAR essas informações.

REGRAS OBRIGATÓRIAS:

- Use os trechos recuperados.
- Não invente informações.
- Não invente horários de chegada.
- Não prometa segurança.
- Não invente lotação.
- Não exponha tokens ou credenciais.
- Não confunda funcionalidades planejadas com implementadas.
- Toda resposta documental deve conter citações.
- As citações devem utilizar os identificadores exatos
  dos trechos fornecidos.
- O texto explicativo deve ficar no campo answer.
- Nunca coloque [CHUNK_ID] ou [SOURCE_ID] dentro de answer.
- Não responda "Não consta" se a resposta estiver
  claramente presente nos documentos.
- Não produza afirmações contraditórias.

Quando tiver contexto suficiente:
status = "answered"

Quando não tiver contexto suficiente:
status = "abstained"

Responda somente no JSON:
status, answer, citations, reason.
"""

def _abstain(reason, answer="Não consta na base consultada ou não há dado operacional em tempo real conectado nesta demonstração."):
    return AssistantResponse(status="abstained", answer=answer, citations=[], reason=reason).model_dump()

def _context(retrieved):
    blocks=[]
    for c in retrieved:
        blocks.append(
            f"[CHUNK_ID: {c['chunk_id']} | SOURCE_ID: {c['source_id']} | SCORE: {c['score']:.4f}]\n"
            f"Seção: {c['section']}\nConteúdo: {c['text']}\nURL: {c.get('source_url','')}"
        )
    return "\n\n".join(blocks)

def _is_refusal_text(text):
    text = (text or "").strip().lower()

    phrases = (
        "não consta",
        "nao consta",
        "não há informação",
        "nao ha informacao",
        "não foi possível",
        "nao foi possivel",
        "não tenho informação",
        "nao tenho informacao",
    )

    return text.startswith(phrases)


def _validate_agent_response(data, retrieved):

    answer_text = (data.get("answer") or "").strip()

    # Se a resposta for uma recusa explícita,
    # mantém a recusa.
    if _is_refusal_text(answer_text):
        return _abstain(
            "Informação não encontrada ou indisponível.",
            answer_text
        )

    # Se o modelo produziu uma explicação completa,
    # mas marcou abstained incorretamente,
    # corrige o status.
    if data.get("status") != "answered":

        if not answer_text:
            return _abstain(
                "O modelo não produziu uma resposta."
            )

        data["status"] = "answered"

    # Não aceitar identificadores como se fossem respostas.
    if "[CHUNK_ID:" in answer_text.upper():
        return _abstain(
            "O modelo retornou metadados em vez de uma resposta."
        )

    allowed = {
        c["chunk_id"]: c
        for c in retrieved
    }

    citations = data.get("citations") or []
    valid = []

    for citation in citations:

        if not isinstance(citation, dict):
            continue

        cid = citation.get("chunk_id")

        if cid in allowed:

            c = allowed[cid]
            src = sources.get(c["source_id"], {})

            valid.append({
                "chunk_id": cid,
                "source_id": c["source_id"],
                "title": src.get("title", c["source_id"]),
                "url": (
                    src.get("url")
                    or c.get("source_url", "")
                )
            })

    # Se o modelo não fornecer a citação,
    # utiliza o primeiro trecho recuperado,
    # desde que ele tenha passado pelo limiar de busca.
    if not valid and retrieved:

        c = retrieved[0]
        src = sources.get(c["source_id"], {})

        valid.append({
            "chunk_id": c["chunk_id"],
            "source_id": c["source_id"],
            "title": src.get("title", c["source_id"]),
            "url": (
                src.get("url")
                or c.get("source_url", "")
            )
        })

    if not valid:
        return _abstain(
            "Nenhuma fonte documental pôde ser validada."
        )

    data["citations"] = valid

    return AssistantResponse.model_validate(data).model_dump()

def answer(question: str, mode: str = "agent", top_k: int = TOP_K, threshold: float = RETRIEVAL_THRESHOLD):
    if mode not in {"base", "rag", "agent"}:
        raise ValueError("mode deve ser 'base', 'rag' ou 'agent'")
    retrieved = [] if mode == "base" else retriever.retrieve(question, top_k=top_k)
    max_score = retrieved[0]["score"] if retrieved else 0.0
    if mode in {"rag", "agent"}:

        if requires_live_data(question):
            return _abstain(
            "Consulta depende de dados operacionais atuais "
            "e nenhuma ferramenta está conectada."
        )

    if not retrieved or max_score < threshold:
        return _abstain(
            f"Similaridade máxima ({max_score:.3f}) "
            f"abaixo do limiar ({threshold:.3f})."
        )

    if mode == "agent":
        system = AGENT_SYSTEM

    elif mode == "rag":
        system = RAG_SYSTEM

    else:
        system = BASE_SYSTEM
    context = _context(retrieved) if retrieved else "Nenhum contexto documental foi fornecido."
    user = f"Pergunta do passageiro/equipe: {question}\n\nTrechos recuperados (use apenas se existirem):\n{context}\n\nDevolva o JSON solicitado."
    result = generate(system, user)
    if mode in {"agent", "rag"}:
        result = _validate_agent_response(result, retrieved)
    result["mode"] = mode
    result["model"] = OLLAMA_MODEL
    result["retrieval_score"] = round(max_score, 4)
    return result
