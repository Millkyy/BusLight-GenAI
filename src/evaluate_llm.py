"""Benchmark das três configurações sobre o mesmo modelo local e o mesmo gabarito."""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
import unicodedata
from pathlib import Path

from .agent import answer
from .config import TEST_PATH, OLLAMA_MODEL


MODES = ("base", "rag", "agent")


def read_cases() -> list[dict]:
    """Lê o conjunto JSONL e aponta a linha exata quando houver erro."""
    cases = []
    with open(TEST_PATH, encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"JSON inválido em {TEST_PATH}, linha {line_number}: {exc}"
                ) from exc
    return cases


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def has_concepts(answer_text: str, groups: list[list[str]]) -> bool:
    normalized_answer = norm(answer_text)
    return all(
        any(norm(term) in normalized_answer for term in group)
        for group in groups
    )


def is_explicit_abstention(answer_text: str) -> bool:
    normalized = norm(answer_text)
    prefixes = (
        "nao consta",
        "nao ha informacao",
        "nao ha dados",
        "nao foi possivel",
        "nao tenho informacao",
        "informacao indisponivel",
        "dados indisponiveis",
    )
    return normalized.startswith(prefixes)


def evaluate_case(case: dict, mode: str, result: dict, valid_json: bool) -> dict:
    """Calcula critérios sem penalizar BASE por não citar documentos."""
    status = result.get("status", "error")
    answer_text = result.get("answer", "")
    explicit_refusal = is_explicit_abstention(answer_text)
    should_abstain = bool(case.get("should_abstain", False))

    if should_abstain:
        abstention_correct = status == "abstained" and explicit_refusal
        concepts_ok = True
        unsupported_answer = status == "answered" and not explicit_refusal
    else:
        abstention_correct = status == "answered" and not explicit_refusal
        concepts_ok = (
            status == "answered"
            and has_concepts(answer_text, case.get("required_concepts", []))
        )
        unsupported_answer = False

    expected_chunks = set(case.get("relevant_chunk_ids", []))
    cited_chunks = {
        citation.get("chunk_id")
        for citation in result.get("citations", [])
        if isinstance(citation, dict)
    }

    if mode == "base" or should_abstain:
        # Citação não se aplica ao baseline sem contexto nem a recusas corretas.
        citation_ok = None
    else:
        citation_ok = (
            status == "answered"
            and bool(cited_chunks.intersection(expected_chunks))
        )

    citation_required = mode in {"rag", "agent"} and not should_abstain
    pass_case = (
        valid_json
        and abstention_correct
        and concepts_ok
        and (citation_ok is not False if citation_required else True)
    )

    return {
        "mode": mode,
        "case_id": case["id"],
        "question": case["question"],
        "status": status,
        "answer": answer_text,
        "citations": json.dumps(result.get("citations", []), ensure_ascii=False),
        "retrieval_score": result.get("retrieval_score", ""),
        "valid_json": valid_json,
        "abstention_correct": abstention_correct,
        "concepts_ok": concepts_ok,
        "citation_ok": citation_ok,
        "unsupported_answer": unsupported_answer,
        "pass": pass_case,
        "latency_seconds": result.get("latency_seconds", ""),
        "reason": result.get("reason", ""),
    }


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def build_scoreboard(records: list[dict], cases: list[dict]) -> list[dict]:
    case_by_id = {case["id"]: case for case in cases}
    board = []

    for mode in MODES:
        rows = [record for record in records if record["mode"] == mode]
        answerable_rows = [row for row in rows if not case_by_id[row["case_id"]].get("should_abstain", False)]
        unanswerable_rows = [row for row in rows if case_by_id[row["case_id"]].get("should_abstain", False)]

        citation_rate = None if mode == "base" else _rate(
            sum(row["citation_ok"] is True for row in answerable_rows),
            len(answerable_rows),
        )

        board.append({
            "mode": mode,
            "n": len(rows),
            "accuracy_pass_rate": _rate(sum(bool(row["pass"]) for row in rows), len(rows)),
            "json_valid_rate": _rate(sum(bool(row["valid_json"]) for row in rows), len(rows)),
            "citation_rate": citation_rate,
            "abstention_accuracy": _rate(
                sum(bool(row["abstention_correct"]) for row in unanswerable_rows),
                len(unanswerable_rows),
            ),
            "unsupported_answer_rate": _rate(
                sum(bool(row["unsupported_answer"]) for row in unanswerable_rows),
                len(unanswerable_rows),
            ),
            "mean_latency_seconds": _rate(
                sum(float(row["latency_seconds"] or 0) for row in rows),
                len(rows),
            ),
        })

    return board


def _fmt_rate(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.1%}"


def write_outputs(records: list[dict], board: list[dict]) -> None:
    output_dir = Path("avaliacao")
    output_dir.mkdir(exist_ok=True)

    with (output_dir / "respostas_benchmark.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    columns = [
        "mode", "n", "accuracy_pass_rate", "json_valid_rate", "citation_rate",
        "abstention_accuracy", "unsupported_answer_rate", "mean_latency_seconds",
    ]
    with (output_dir / "placar_tres_configuracoes.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(board)

    lines = [
        "# Placar das três configurações",
        "",
        f"Modelo local: `{OLLAMA_MODEL}`.",
        "Resultados medidos nesta execução. Não substituir por estimativas.",
        "",
        "| Configuração | Casos | Aprovação | JSON válido | Citações corretas | Acerto da recusa | Resposta sem suporte | Latência média (s) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in board:
        latency = "N/A" if row["mean_latency_seconds"] is None else f"{row['mean_latency_seconds']:.2f}"
        lines.append(
            f"| {row['mode']} | {row['n']} | {_fmt_rate(row['accuracy_pass_rate'])} "
            f"| {_fmt_rate(row['json_valid_rate'])} | {_fmt_rate(row['citation_rate'])} "
            f"| {_fmt_rate(row['abstention_accuracy'])} | {_fmt_rate(row['unsupported_answer_rate'])} "
            f"| {latency} |"
        )
    lines.extend([
        "",
        "## Como interpretar",
        "",
        "- `base` não recebe documentos; por isso, citação é `N/A`, não 0% nem 100%.",
        "- Compare `rag` com `base` para observar o ganho da recuperação documental.",
        "- Compare `agent` com `rag` para observar o efeito das regras especializadas.",
        "- Uma taxa menor de respostas sem suporte nas perguntas sem resposta é desejável.",
        "- A taxa automática de aprovação é uma aproximação baseada no gabarito; revise manualmente respostas e fontes antes da conclusão.",
        "- O modo `rag` não recebe o bloqueio determinístico do agente; isso preserva a comparação experimental.",
        "",
    ])
    (output_dir / "placar_tres_configuracoes.md").write_text("\n".join(lines), encoding="utf-8")


def run(limit: int | None = None) -> None:
    cases = read_cases()
    if limit is not None:
        if limit <= 0:
            raise ValueError("--limit deve ser um inteiro positivo")
        cases = cases[:limit]

    records = []
    for mode in MODES:
        for case in cases:
            started = time.perf_counter()
            try:
                result = answer(case["question"], mode=mode)
                valid_json = isinstance(result, dict) and {
                    "status", "answer", "citations", "reason"
                }.issubset(result.keys())
            except Exception as exc:
                result = {
                    "status": "error",
                    "answer": str(exc),
                    "citations": [],
                    "reason": "execution_error",
                    "retrieval_score": "",
                }
                valid_json = False

            elapsed = round(time.perf_counter() - started, 2)
            result.setdefault("latency_seconds", elapsed)
            record = evaluate_case(case, mode, result, valid_json)
            record["latency_seconds"] = elapsed
            records.append(record)
            print(
                f"[{mode}] {case['id']} {record['status']} "
                f"pass={record['pass']} ({elapsed:.2f}s)"
            )

    board = build_scoreboard(records, cases)
    write_outputs(records, board)

    print("\nPLACAR GERADO: avaliacao/placar_tres_configuracoes.csv e .md")
    for row in board:
        print(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    run(args.limit)
