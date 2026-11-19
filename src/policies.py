import re
import unicodedata

def _norm(value: str) -> str:
    return unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()

def requires_live_data(question: str) -> bool:
    q = _norm(question)
    # Ask for actual status: descriptive questions such as "como funciona a API em tempo real?"
    # remain answerable from the documentation.
    safety = re.search(r"\b(e seguro|segura|perigoso|perigosa|risco individual|garantia de seguranca)\b", q)
    privacy = re.search(r"\b(cpf|nome da pessoa|identidade|quem esta esperando)\b", q)
    police = re.search(r"\b(ocorrencia|ocorrencias|crime|assalto|roubo|incidente)\b", q) and re.search(r"\b(hoje|agora|ontem|atual|neste momento)\b", q)
    current = re.search(r"\b(agora|hoje|ontem|amanha|neste momento|mais recente)\b", q)
    asks_state = re.search(r"\b(qual|quais|onde|quantos|quantas|tem|esta|estao|aconteceu|houve|acabou|saiu|chegou|chega|lotacao)\b", q)
    crowd = re.search(r"\b(lotacao|lotado|cheio|cheia|vazio|vazia)\b", q) and re.search(r"\b(qual|quanto|quantos|agora|atual|exata|neste momento)\b", q)
    eta = re.search(r"\b(a que horas|quando chega|quanto falta|em quantos minutos|previsao para minha linha|previsao da linha)\b", q)
    return bool(safety or privacy or police or (current and asks_state) or crowd or eta)
