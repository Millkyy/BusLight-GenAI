import os
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
RETRIEVAL_THRESHOLD = float(os.getenv("RETRIEVAL_THRESHOLD", "0.1224"))
TOP_K = int(os.getenv("TOP_K", "3"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "base", "trechos.jsonl")
SOURCES_PATH = os.path.join(BASE_DIR, "base", "fontes.csv")
TEST_PATH = os.path.join(BASE_DIR, "avaliacao", "conjunto_teste.jsonl")
