import requests
from .config import OLLAMA_HOST, OLLAMA_MODEL
from .schemas import AssistantResponse

class OllamaError(RuntimeError):
    pass

def generate(system_prompt: str, user_prompt: str, model: str = OLLAMA_MODEL) -> dict:
    """Chama o modelo local pelo endpoint Ollama. Não envia conteúdo a terceiros."""
    schema = AssistantResponse.model_json_schema()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "format": schema,
        "options": {"temperature": 0, "top_p": 0.9, "seed": 42}
    }
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=180)
        response.raise_for_status()
        raw = response.json().get("message", {}).get("content", "")
    except requests.RequestException as exc:
        raise OllamaError(f"Não foi possível acessar o Ollama em {OLLAMA_HOST}: {exc}") from exc
    try:
        import json
        data = json.loads(raw)
        return AssistantResponse.model_validate(data).model_dump()
    except Exception as exc:
        raise OllamaError(f"O modelo retornou conteúdo fora do schema JSON: {raw[:500]}") from exc
