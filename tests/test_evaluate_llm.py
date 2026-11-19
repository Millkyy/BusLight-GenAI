import unittest

from src.evaluate_llm import evaluate_case, build_scoreboard


class EvaluateLLMTests(unittest.TestCase):
    def test_base_does_not_require_citations(self):
        case = {
            "id": "QX1",
            "question": "Pergunta documental",
            "should_abstain": False,
            "required_concepts": [["olho vivo"]],
            "relevant_chunk_ids": ["SPT-002"],
        }
        result = {
            "status": "answered",
            "answer": "A informação está na documentação Olho Vivo.",
            "citations": [],
        }

        row = evaluate_case(case, "base", result, True)

        self.assertIsNone(row["citation_ok"])
        self.assertTrue(row["pass"])

    def test_rag_requires_relevant_citation_for_answerable_case(self):
        case = {
            "id": "QX2",
            "question": "Pergunta documental",
            "should_abstain": False,
            "required_concepts": [["olho vivo"]],
            "relevant_chunk_ids": ["SPT-002"],
        }
        result = {
            "status": "answered",
            "answer": "A documentação Olho Vivo contém a informação.",
            "citations": [{"chunk_id": "SPT-002"}],
        }

        row = evaluate_case(case, "rag", result, True)

        self.assertTrue(row["citation_ok"])
        self.assertTrue(row["pass"])

    def test_correct_abstention_does_not_require_citation(self):
        case = {
            "id": "QX3",
            "question": "Pergunta sem resposta",
            "should_abstain": True,
            "required_concepts": [],
            "relevant_chunk_ids": [],
        }
        result = {
            "status": "abstained",
            "answer": "Não consta na base consultada.",
            "citations": [],
        }

        row = evaluate_case(case, "agent", result, True)

        self.assertTrue(row["abstention_correct"])
        self.assertIsNone(row["citation_ok"])
        self.assertTrue(row["pass"])

    def test_answer_to_unanswerable_case_is_counted_as_unsupported(self):
        case = {
            "id": "QX4",
            "question": "Pergunta sem resposta",
            "should_abstain": True,
            "required_concepts": [],
            "relevant_chunk_ids": [],
        }
        result = {
            "status": "answered",
            "answer": "O ponto está lotado.",
            "citations": [],
        }

        row = evaluate_case(case, "rag", result, True)

        self.assertTrue(row["unsupported_answer"])
        self.assertFalse(row["pass"])

    def test_base_citation_rate_is_not_applicable(self):
        cases = [{"id": "QX5", "should_abstain": False}]
        records = [{
            "mode": "base",
            "case_id": "QX5",
            "pass": True,
            "valid_json": True,
            "citation_ok": None,
            "abstention_correct": False,
            "unsupported_answer": False,
            "latency_seconds": 1.0,
        }]

        board = build_scoreboard(records, cases)

        self.assertIsNone(board[0]["citation_rate"])


if __name__ == "__main__":
    unittest.main()
