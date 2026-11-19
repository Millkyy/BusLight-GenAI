import json, csv
from pathlib import Path
from .config import KNOWLEDGE_PATH, SOURCES_PATH

def load_jsonl(path=KNOWLEDGE_PATH):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Base não encontrada: {p}")
    with p.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def load_sources(path=SOURCES_PATH):
    p = Path(path)
    with p.open(encoding="utf-8-sig", newline="") as f:
        return {row["source_id"]: row for row in csv.DictReader(f, delimiter=";")}
