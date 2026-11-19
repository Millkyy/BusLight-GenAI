"""Benchmark das três configurações sobre o mesmo modelo local e o mesmo gabarito."""
import argparse, json, csv, re, unicodedata, time
from pathlib import Path
from .agent import answer
from .config import TEST_PATH, OLLAMA_MODEL

def read_cases():
    with open(TEST_PATH,encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]
def norm(s):
    s=unicodedata.normalize("NFKD",s or "").encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+"," ",s).strip()
def has_concepts(answer_text, groups):
    a=norm(answer_text)
    return all(any(norm(term) in a for term in group) for group in groups)
def run(limit=None):
    cases=read_cases()[:limit] if limit else read_cases()
    records=[]
    for mode in ("base","rag","agent"):
        for c in cases:
            start=time.time()
            try:
                res=answer(c["question"],mode=mode)
                valid_json=True
            except Exception as exc:
                res={"status":"error","answer":str(exc),"citations":[],"reason":"execution_error","mode":mode,"model":OLLAMA_MODEL}
                valid_json=False
            elapsed=round(time.time()-start,2)
            status = res.get("status")
            answer_text = res.get("answer", "")

            answer_norm = norm(answer_text)

            explicit_abstention = answer_norm.startswith((
                "nao consta",
                "nao ha informacao",
                "nao foi possivel",
                "nao tenho informacao"
            ))

            if c["should_abstain"]:

                abstain_correct = (
                    status == "abstained"
                    and explicit_abstention
                )

                concepts_ok = True

                unsupported_answer = (
                    status == "answered"
                    and not explicit_abstention
                )

            else:

                abstain_correct = (
                    status == "answered"
                    and not explicit_abstention
                )

                concepts_ok = has_concepts(
                    answer_text,
                    c.get("required_concepts", [])
                )

                unsupported_answer = False

            expected = set(c.get("relevant_chunk_ids", []))

            cited = {
                x.get("chunk_id")
                for x in res.get("citations", [])
                if isinstance(x, dict)
            }

            citation_required = (
                mode in {"rag", "agent"}
                and not c["should_abstain"]
            )

            if mode == "base":
                citation_ok = True

            else:
                citation_ok = (
                    bool(cited.intersection(expected))
                    if expected and status == "answered"
                    else (
                        not c["should_abstain"]
                        and status == "answered"
                        and bool(cited)
                    )
                )

            pass_case = (
                valid_json
                and abstain_correct
                and concepts_ok
                and (
                    citation_ok
                    if citation_required
                    else True
                )
            )
            expected=set(c.get("relevant_chunk_ids",[]))
            cited={x.get("chunk_id") for x in res.get("citations",[]) if isinstance(x,dict)}
            citation_ok=bool(cited.intersection(expected)) if expected and status=="answered" else (not c["should_abstain"] and status=="answered" and bool(cited))
            unsupported_answer=bool(c["should_abstain"] and status=="answered")
            pass_case=valid_json and abstain_correct and concepts_ok and (citation_ok if not c["should_abstain"] else True)
            row={"mode":mode,"case_id":c["id"],"question":c["question"],"status":status,"answer":res.get("answer",""),"citations":json.dumps(res.get("citations",[]),ensure_ascii=False),"retrieval_score":res.get("retrieval_score",""),"valid_json":valid_json,"abstention_correct":abstain_correct,"concepts_ok":concepts_ok,"citation_ok":citation_ok,"unsupported_answer":unsupported_answer,"pass":pass_case,"latency_seconds":elapsed,"reason":res.get("reason","")}
            records.append(row)
            print(f"[{mode}] {c['id']} {status} pass={pass_case} ({elapsed}s)")
    Path("avaliacao").mkdir(exist_ok=True)
    with open("avaliacao/respostas_benchmark.jsonl","w",encoding="utf-8") as f:
        for r in records: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    keys=["mode","n","accuracy_pass_rate","json_valid_rate","citation_rate","abstention_accuracy","unsupported_answer_rate","mean_latency_seconds"]
    board=[]
    for mode in ("base","rag","agent"):
        rows=[x for x in records if x["mode"]==mode]; n=len(rows) or 1
        answerable=[x for x in rows if not next(c for c in cases if c["id"]==x["case_id"])["should_abstain"]]
        unanswerable=[x for x in rows if next(c for c in cases if c["id"]==x["case_id"])["should_abstain"]]
        board.append({"mode":mode,"n":len(rows),"accuracy_pass_rate":sum(x["pass"] for x in rows)/n,"json_valid_rate":sum(x["valid_json"] for x in rows)/n,"citation_rate":sum(x["citation_ok"] for x in answerable)/max(1,len(answerable)),"abstention_accuracy":sum(x["abstention_correct"] for x in unanswerable)/max(1,len(unanswerable)),"unsupported_answer_rate":sum(x["unsupported_answer"] for x in unanswerable)/max(1,len(unanswerable)),"mean_latency_seconds":sum(x["latency_seconds"] for x in rows)/n})
    with open("avaliacao/placar_tres_configuracoes.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=keys,delimiter=";"); w.writeheader(); w.writerows(board)
    with open("avaliacao/placar_tres_configuracoes.md","w",encoding="utf-8") as f:
        f.write("# Placar das três configurações\n\n")
        f.write("Resultados medidos nesta execução, usando o mesmo modelo e os mesmos casos. Não substituir por estimativas.\n\n")
        f.write("| Configuração | Casos | Taxa de aprovação | JSON válido | Citações corretas | Acerto da recusa | Resposta sem suporte | Latência média (s) |\n|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for b in board:
            f.write(f"| {b['mode']} | {b['n']} | {b['accuracy_pass_rate']:.1%} | {b['json_valid_rate']:.1%} | {b['citation_rate']:.1%} | {b['abstention_accuracy']:.1%} | {b['unsupported_answer_rate']:.1%} | {b['mean_latency_seconds']:.2f} |\n")
        f.write("\n**Interpretação:** comparar primeiro `agent` com `rag` (ganho da especialização) e `rag` com `base` (ganho da recuperação). Uma taxa menor de resposta sem suporte é desejável. Examinar manualmente as respostas antes de concluir.\n")
    print("\nPLCAR GERADO: avaliacao/placar_tres_configuracoes.csv e .md")
    for b in board: print(b)
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--limit",type=int,default=None); args=p.parse_args(); run(args.limit)
