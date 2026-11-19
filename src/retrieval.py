"""Busca lexical local híbrida: TF-IDF de palavras e n-gramas de caracteres."""
import unicodedata, re
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .knowledge import load_jsonl

def normalize(text):
    return unicodedata.normalize("NFKD", text or "").encode("ascii","ignore").decode().lower()

def expand_query(query):
    q = normalize(query)
    extras = []
    if any(x in q for x in ["posicao", "localizacao", "onde estao os onibus"]):
        extras.append("Posição dos veículos monitoramento da frota de ônibus latitude longitude API Olho Vivo")
    if any(x in q for x in ["previsao", "chegada", "eta", "atraso", "quatro minutos", "sozinho"]):
        extras.append("Previsão de chegada por linha e parada, veículos, timestamp, horário de atualização; ETA vem da API Olho Vivo e o LLM não inventa")
    if "token" in q or "chave" in q:
        extras.append("cadastro de desenvolvedor criação de aplicativo autenticação Login Autenticar credencial")
    if ("gtfs" in q or "stop_times" in q) and not re.search(r"\d{2}:\d{2}", q):
        extras.append("agency.txt stops.txt routes.txt trips.txt stop_times.txt calendar.txt horários por parada")
    if "lgpd" in q or "dado pessoal" in q or "privacidade" in q:
        extras.append("finalidade adequação necessidade transparência segurança prevenção não discriminação pessoa identificada ou identificável")
    if "open meteo" in q or "meteorolog" in q or "clima" in q:
        extras.append("Open-Meteo dados meteorológicos licença Creative Commons Attribution CC BY 4.0 atribuição")
    return query + " " + " ".join(extras)

class Retriever:
    def __init__(self, chunks=None):
        self.chunks = chunks or load_jsonl()
        texts = [self._doc_text(c) for c in self.chunks]
        self.word = TfidfVectorizer(analyzer="word", ngram_range=(1,2), strip_accents="unicode", lowercase=True, sublinear_tf=True)
        self.char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5), strip_accents="unicode", lowercase=True, sublinear_tf=True)
        self.word_matrix = self.word.fit_transform(texts)
        self.char_matrix = self.char.fit_transform(texts)
        self.matrix = hstack([self.word_matrix, self.char_matrix]).tocsr()
    @staticmethod
    def _doc_text(chunk):
        return " ".join([chunk.get("section", ""), chunk.get("text", ""), chunk.get("chunk_id", "")])
    def retrieve(self, query, top_k=3):
        q = [expand_query(query)]
        qvec = hstack([self.word.transform(q), self.char.transform(q)]).tocsr()
        scores = cosine_similarity(qvec, self.matrix).ravel()
        idx = scores.argsort()[::-1][:top_k]
        out=[]
        for i in idx:
            item=dict(self.chunks[int(i)]); item["score"]=float(scores[int(i)]); out.append(item)
        return out
    def metrics(self, test_cases, k_values=(1,3)):
        valid=[c for c in test_cases if c.get("relevant_chunk_ids")]
        totals={k:0 for k in k_values}; hit={k:0 for k in k_values}
        relevant_total=sum(len(c["relevant_chunk_ids"]) for c in valid)
        for case in valid:
            ranked=self.retrieve(case["question"],max(k_values)); ids=[x["chunk_id"] for x in ranked]; gold=set(case["relevant_chunk_ids"])
            for k in k_values:
                found=gold.intersection(ids[:k]); totals[k]+=len(found); hit[k]+=int(bool(found))
        n=len(valid) or 1; result={}
        for k in k_values:
            result[f"recall@{k}"]=totals[k]/relevant_total if relevant_total else 0.0
            result[f"hit_rate@{k}"]=hit[k]/n
        result["answerable_queries"]=len(valid); result["total_relevant_labels"]=relevant_total
        return result
