"""Regressões das melhorias de coerência e segunda tentativa fundamentada."""
import unittest
from unittest.mock import patch
from src.agent import answer

CHUNK = {
    'chunk_id': 'SPT-001', 'source_id': 'SPTRANS_OLHOVIVO',
    'section': 'Acesso e autenticação',
    'text': 'O desenvolvedor faz cadastro e cria um aplicativo para obter token.',
    'source_url': 'https://www.sptrans.com.br/desenvolvedores/api-do-olho-vivo-guia-de-referencia/documentacao-api',
    'score': 0.8,
}

class ImprovementTests(unittest.TestCase):
    @patch('src.agent.generate', return_value={
        'status': 'answered', 'answer': 'Não consta', 'citations': [], 'reason': ''})
    def test_base_refusal_status_is_consistent(self, generate):
        response = answer('Qual é o mascote oficial?', mode='base')
        self.assertEqual(response['status'], 'abstained')
        self.assertEqual(response['citations'], [])

    @patch('src.agent.retriever.retrieve', return_value=[CHUNK])
    @patch('src.agent.generate')
    def test_agent_retries_missing_citation_without_fabricating(self, generate, retrieve):
        generate.side_effect = [
            {'status': 'answered', 'answer': 'Cadastre-se e crie aplicativo.', 'citations': [], 'reason': ''},
            {'status': 'answered', 'answer': 'Cadastre-se e crie aplicativo.',
             'citations': [{'chunk_id': 'SPT-001', 'source_id': 'SPTRANS_OLHOVIVO', 'title': '', 'url': ''}], 'reason': ''},
        ]
        response = answer('Como consigo o token?', mode='agent')
        self.assertEqual(response['status'], 'answered')
        self.assertEqual(response['citations'][0]['chunk_id'], 'SPT-001')
        self.assertEqual(generate.call_count, 2)

    @patch('src.agent.retriever.retrieve', return_value=[CHUNK])
    @patch('src.agent.generate', return_value={
        'status': 'answered', 'answer': 'Não consta', 'citations': [], 'reason': ''})
    def test_agent_still_abstains_when_retry_fails(self, generate, retrieve):
        response = answer('Pergunta sem suporte?', mode='agent')
        self.assertEqual(response['status'], 'abstained')
        self.assertEqual(response['citations'], [])
        self.assertEqual(generate.call_count, 2)

if __name__ == '__main__':
    unittest.main()
