"""Três configurações experimentais: base, RAG simples e agente especializado."""
from __future__ import annotations

from .config import RETRIEVAL_THRESHOLD, TOP_K, OLLAMA_MODEL
from .knowledge import load_sources
from .retrieval import Retriever
from .llm import generate
from .schemas import AssistantResponse
from .policies import requires_live_data


retriever = Retriever()
sources = load_sources()


BASE_SYSTEM = """
Você é um assistente de mobilidade urbana que responde em português.

Esta é a configuração BASE: você não recebeu documentos de referência,
recuperação de trechos ou ferramentas externas. Responda usando apenas
conhecimento geral que você realmente possui. Não finja ter consultado fontes.

Não invente informações específicas do BusLight. Não invente previsões,
horários de chegada, posição atual de veículos, lotação ou condições atuais
de segurança. Para perguntas sobre esses dados atuais, responda que não há
informação disponível nesta demonstração.

Se não souber uma informação, diga claramente "Não consta". Como não há
documentos nesta configuração, citations deve ser uma lista vazia.

Retorne somente um JSON compatível com o schema solicitado, contendo
status, answer, citations e reason.
"""


RAG_SYSTEM = """
Você é o assistente documental do BusLight e responde em português claro.

Você recebeu trechos recuperados de uma base de conhecimento. Use esses
TRECHOS como evidência principal. Esta configuração é RAG simples: não há
uma camada adicional de regras determinísticas do agente.

REGRAS:
1. Se os trechos sustentarem a resposta, responda de forma direta e completa.
2. Se os trechos não contiverem a informação necessária, responda "Não consta".
3. Perguntas sobre condições atuais (ETA, localização atual, lotação, segurança
   ou ocorrências recentes) não podem ser respondidas por documentos estáticos.
   Sem ferramenta operacional conectada, responda "Não consta".
4. Não invente fatos, fontes, horários, números ou identificadores.
5. Para uma resposta factual, cite somente chunk_id que apareça nos trechos.
6. Não coloque marcadores [CHUNK_ID] ou [SOURCE_ID] no texto answer.
7. Não contradiga os trechos nem transforme proposta futura em funcionalidade
   já implementada.
8. Quando a informação estiver documentada, use status="answered".
9. Quando faltar evidência, use status="abstained" e citations=[].

Retorne somente um JSON compatível com o schema solicitado, contendo
status, answer, citations e reason.
"""


AGENT_SYSTEM = """
Você é o BusLight Assist, um agente especializado em mobilidade urbana,
acessibilidade e privacidade no transporte público. Responda em português,
com frases completas, claras e objetivas.

DISTINÇÃO OBRIGATÓRIA:

A) PERGUNTAS DOCUMENTAIS
Incluem dúvidas sobre a API Olho Vivo, GTFS, licenças, LGPD, acessibilidade,
privacidade, arquitetura, funcionamento e decisões de projeto do BusLight.
Se houver evidência nos trechos recuperados, RESPONDA. Não confunda a ausência
de dados operacionais em tempo real com ausência de documentação.

B) PERGUNTAS OPERACIONAIS ATUAIS
Incluem ETA exato, posição atual, lotação atual, segurança atual de um ponto,
e ocorrências policiais de hoje/agora. Nenhuma ferramenta operacional está
conectada nesta demonstração. Portanto, NÃO invente nem estime esses dados;
responda com status="abstained" e informe a limitação.

REGRAS:
- Use os trechos recuperados como evidência.
- Não invente informações, previsões, horários, lotação ou garantias de segurança.
- Não exponha tokens ou credenciais.
- Diferencie requisitos/propostas de funcionalidades efetivamente implementadas.
- Toda resposta documental factual deve citar os chunk_id correspondentes.
- Use somente os chunk_id presentes nos trechos fornecidos.
- O campo answer deve conter a explicação em linguagem natural.
- O campo citations deve conter os objetos de citação, nunca texto de metadados.
- Nunca escreva [CHUNK_ID] ou [SOURCE_ID] dentro de answer.
- Não responda "Não consta" se a informação estiver claramente documentada.
- Não produza afirmações contraditórias.

Se houver evidência suficiente e citação válida, use status="answered".
Se não houver evidência suficiente, use status="abstained" e citations=[].

Retorne somente um JSON compatível com o schema solicitado, contendo
status, answer, citations e reason.
"""


def _abstain(
    reason: str,
    answer: str = (
        "Não consta na base consultada ou não há dado operacional "
        "em tempo real conectado nesta demonstração."
    ),
) -> dict:
    """Padroniza uma recusa sem citar fontes que não sustentam a resposta."""
    return AssistantResponse(
        status="abstained",
        answer=answer,
        citations=[],
        reason=reason,
    ).model_dump()


def _context(retrieved: list[dict]) -> str:
    """Formata os chunks recuperados para o contexto do modelo."""
    blocks = []
    for chunk in retrieved:
        blocks.append(
            f"[CHUNK_ID: {chunk['chunk_id']} | SOURCE_ID: {chunk['source_id']} "
            f"| SCORE: {chunk['score']:.4f}]\n"
            f"Seção: {chunk.get('section', '')}\n"
            f"Conteúdo: {chunk.get('text', '')}\n"
            f"URL: {chunk.get('source_url', '')}"
        )
    return "\n\n".join(blocks)


def _normalize_text(text: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower().strip()


def _is_refusal_text(text: str) -> bool:
    normalized = _normalize_text(text)
    refusal_prefixes = (
        "nao consta",
        "nao ha informacao",
        "nao ha dados",
        "nao foi possivel",
        "nao tenho informacao",
        "informacao indisponivel",
        "dados indisponiveis",
    )
    return normalized.startswith(refusal_prefixes)


def _citation_from_chunk(chunk: dict) -> dict:
    source = sources.get(chunk["source_id"], {})
    return {
        "chunk_id": chunk["chunk_id"],
        "source_id": chunk["source_id"],
        "title": source.get("title") or chunk["source_id"],
        "url": source.get("url") or chunk.get("source_url", ""),
    }


def _validate_agent_response(data: dict, retrieved: list[dict]) -> dict:
    """Valida evidência/citações do agente; não inventa citação substituta."""
    try:
        response = AssistantResponse.model_validate(data).model_dump()
    except Exception as exc:
        return _abstain(f"Resposta fora do schema: {exc}")

    answer_text = (response.get("answer") or "").strip()
    if not answer_text:
        return _abstain("O modelo não produziu uma resposta.")

    if _is_refusal_text(answer_text):
        return _abstain(
            response.get("reason") or "Informação não encontrada ou indisponível.",
            answer_text,
        )

    upper_answer = answer_text.upper()
    if "[CHUNK_ID:" in upper_answer or "[SOURCE_ID:" in upper_answer:
        return _abstain(
            "O modelo retornou metadados em vez de uma resposta em linguagem natural."
        )

    allowed_chunks = {chunk["chunk_id"]: chunk for chunk in retrieved}
    valid_citations = []
    seen = set()

    for citation in response.get("citations") or []:
        citation_id = citation.get("chunk_id") if isinstance(citation, dict) else None
        if citation_id in allowed_chunks and citation_id not in seen:
            valid_citations.append(_citation_from_chunk(allowed_chunks[citation_id]))
            seen.add(citation_id)

    # Agente só responde quando existe pelo menos uma citação realmente
    # pertencente ao contexto que recebeu. Não substituímos por top-1 às cegas.
    if not valid_citations:
        return _abstain(
            "A resposta não apresentou uma citação válida entre os trechos recuperados."
        )

    response["status"] = "answered"
    response["citations"] = valid_citations
    response["answer"] = answer_text
    return AssistantResponse.model_validate(response).model_dump()


def answer(
    question: str,
    mode: str = "agent",
    top_k: int = TOP_K,
    threshold: float = RETRIEVAL_THRESHOLD,
) -> dict:
    """Executa BASE, RAG simples ou agente especializado.

    BASE: mesmo LLM, sem recuperação e sem regras especiais de bloqueio.
    RAG: recuperação + prompt documental, sem bloqueio determinístico do agente.
    AGENT: recuperação + política live + limiar + validação de citação.
    """
    if mode not in {"base", "rag", "agent"}:
        raise ValueError("mode deve ser 'base', 'rag' ou 'agent'")

    # A regra operacional determinística pertence somente ao agente.
    # BASE e RAG precisam permanecer como linhas de comparação experimentais.
    if mode == "agent" and requires_live_data(question):
        result = _abstain(
            "Consulta depende de dados operacionais atuais e nenhuma "
            "ferramenta está conectada nesta demonstração."
        )
        result.update({"mode": mode, "model": OLLAMA_MODEL, "retrieval_score": 0.0})
        return result

    retrieved = [] if mode == "base" else retriever.retrieve(question, top_k=top_k)
    max_score = retrieved[0]["score"] if retrieved else 0.0

    # O limiar também é uma especialização do agente. O RAG simples mantém
    # a recuperação top-k para que possamos medir seus acertos e falhas.
    if mode == "agent" and (not retrieved or max_score < threshold):
        result = _abstain(
            f"Similaridade máxima ({max_score:.3f}) abaixo do limiar ({threshold:.3f})."
        )
        result.update({"mode": mode, "model": OLLAMA_MODEL, "retrieval_score": round(max_score, 4)})
        return result

    if mode == "base":
        system_prompt = BASE_SYSTEM
    elif mode == "rag":
        system_prompt = RAG_SYSTEM
    else:
        system_prompt = AGENT_SYSTEM

    context = _context(retrieved) if retrieved else "Nenhum contexto documental foi fornecido."
    user_prompt = (
        f"Pergunta do passageiro/equipe: {question}\n\n"
        f"Trechos recuperados (podem estar vazios):\n{context}\n\n"
        "Devolva somente o JSON solicitado."
    )

    result = generate(system_prompt, user_prompt)

    # Apenas AGENT aplica a validação especializada pós-geração.
    # RAG simples mantém o comportamento bruto do RAG para comparação.
    if mode == "agent":
        result = _validate_agent_response(result, retrieved)

    result["mode"] = mode
    result["model"] = OLLAMA_MODEL
    result["retrieval_score"] = round(max_score, 4)
    return result
