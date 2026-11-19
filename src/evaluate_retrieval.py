import json, csv
from pathlib import Path
from .config import TEST_PATH
from .retrieval import Retriever
from .policies import requires_live_data

def read_cases():
    with open(TEST_PATH, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def main():
    cases=read_cases(); r=Retriever(); metrics=r.metrics(cases)
    positive=[]; negative=[]
    for c in cases:
        score=r.retrieve(c["question"],1)[0]["score"]
        if c["relevant_chunk_ids"]:
            positive.append((c["id"],score))
        elif not c.get("requires_live_data", requires_live_data(c["question"])):
            negative.append((c["id"],score))
    # Use the midpoint only when the labelled set provides separation; otherwise choose
    # a conservative threshold and explicitly report overlap for human review.
    pmin=min((s for _,s in positive), default=0.0)
    nmax=max((s for _,s in negative), default=0.0)
    separated = pmin > nmax
    threshold = (pmin+nmax)/2 if separated else max(0.10, nmax+0.02)
    out={"retrieval_metrics":metrics,"positive_min_top1":round(pmin,4),"negative_max_top1":round(nmax,4),"separable":separated,"recommended_threshold":round(threshold,4),"threshold_method":"midpoint between minimum positive and maximum unknown/non-live negative top-1 score; live-data refusals are policy-routed before retrieval" if separated else "conservative nmax + 0.02 (floor 0.10); inspect false positives/negatives manually"}
    outpath=Path("avaliacao/metricas_busca.json"); outpath.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    print("\nTop-3 por consulta:")
    for c in cases:
        hits=r.retrieve(c["question"],3)
        print(c["id"],"|",c["question"],"|",[(x['chunk_id'],round(x['score'],3)) for x in hits])
if __name__=="__main__": main()
