import unittest
from unittest.mock import patch

from src.agent import answer


SAMPLE_CHUNK = {
    "chunk_id": "SPT-001",
    "source_id": "SPTRANS_OLHOVIVO",
    "section": "Acesso e autenticação",
    "text": "O desenvolvedor deve realizar cadastro e criar um aplicativo para obter token.",
    "source_url": "https://www.sptrans.com.br/desenvolvedores/api-do-olho-vivo-guia-de-referencia/documentacao-api",
    "score": 0.8,
}


class AgentModeTests(unittest.TestCase):
    @patch("src.agent.generate")
    @patch("src.agent.retriever.retrieve")
    def test_base_calls_model_without_retrieval(self, retrieve_mock, generate_mock):
        generate_mock.return_value = {
            "status": "answered",
            "answer": "A documentação geral da API deve ser consultada.",
            "citations": [],
            "reason": "Resposta sem documentos.",
        }

        result = answer("O que é uma API?", mode="base")

        retrieve_mock.assert_not_called()
        generate_mock.assert_called_once()
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["citations"], [])
        self.assertEqual(result["mode"], "base")

    @patch("src.agent.generate")
    @patch("src.agent.retriever.retrieve", return_value=[SAMPLE_CHUNK])
    def test_rag_is_not_blocked_by_agent_threshold(self, retrieve_mock, generate_mock):
        generate_mock.return_value = {
            "status": "answered",
            "answer": "O cadastro e a criação de aplicativo permitem obter o token.",
            "citations": [{
                "chunk_id": "SPT-001",
                "source_id": "SPTRANS_OLHOVIVO",
                "title": "Acesso e autenticação",
                "url": SAMPLE_CHUNK["source_url"],
            }],
            "reason": "Trecho documental recuperado.",
        }

        result = answer("Como consigo o token?", mode="rag", threshold=0.99)

        retrieve_mock.assert_called_once()
        generate_mock.assert_called_once()
        self.assertEqual(result["status"], "answered")

    @patch("src.agent.generate")
    @patch("src.agent.requires_live_data", return_value=True)
    def test_agent_blocks_live_query_before_generation(self, live_mock, generate_mock):
        result = answer("Qual é a lotação exata do ponto agora?", mode="agent")

        live_mock.assert_called_once()
        generate_mock.assert_not_called()
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["citations"], [])

    @patch("src.agent.generate")
    @patch("src.agent.retriever.retrieve", return_value=[SAMPLE_CHUNK])
    def test_agent_requires_a_citation_from_retrieved_context(self, retrieve_mock, generate_mock):
        generate_mock.return_value = {
            "status": "answered",
            "answer": "Para obter o token, faça o cadastro e crie um aplicativo.",
            "citations": [],
            "reason": "Resposta documental.",
        }

        result = answer("Como consigo o token?", mode="agent")

        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["citations"], [])
        self.assertIn("citação válida", result["reason"])

    @patch("src.agent.generate")
    @patch("src.agent.retriever.retrieve", return_value=[SAMPLE_CHUNK])
    def test_agent_keeps_only_grounded_citations(self, retrieve_mock, generate_mock):
        generate_mock.return_value = {
            "status": "abstained",
            "answer": "Para obter o token, faça o cadastro e crie um aplicativo.",
            "citations": [
                {"chunk_id": "FAKE-999", "source_id": "FAKE", "title": "Fake", "url": ""},
                {"chunk_id": "SPT-001", "source_id": "SPTRANS_OLHOVIVO", "title": "Acesso", "url": ""},
            ],
            "reason": "O modelo marcou abstained apesar da evidência citada.",
        }

        result = answer("Como consigo o token?", mode="agent")

        self.assertEqual(result["status"], "answered")
        self.assertEqual([x["chunk_id"] for x in result["citations"]], ["SPT-001"])


if __name__ == "__main__":
    unittest.main()
