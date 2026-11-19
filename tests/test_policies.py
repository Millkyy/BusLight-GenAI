import unittest
from src.policies import requires_live_data

class PolicyTests(unittest.TestCase):
    def test_live_eta_is_blocked(self):
        self.assertTrue(requires_live_data("A que horas chega o ônibus da linha 8000 agora?"))
    def test_current_crowd_is_blocked(self):
        self.assertTrue(requires_live_data("Qual a lotação exata do ponto agora?"))
    def test_safety_guarantee_is_blocked(self):
        self.assertTrue(requires_live_data("Esse ponto é seguro para esperar à noite?"))
    def test_current_crime_report_is_blocked(self):
        self.assertTrue(requires_live_data("Quais ocorrências policiais aconteceram hoje?"))
    def test_documentation_question_is_allowed(self):
        self.assertFalse(requires_live_data("Como funciona a API de previsão em tempo real da SPTrans?"))
    def test_face_recognition_design_question_is_documental(self):
        self.assertFalse(requires_live_data("O BusLight precisa reconhecer o rosto das pessoas para contar quem está no ponto?"))
    def test_conceptual_eta_question_is_documental(self):
        self.assertFalse(requires_live_data("O LLM consegue prever sozinho se o ônibus chega em quatro minutos?"))
    def test_exact_live_lotacao_is_blocked(self):
        self.assertTrue(requires_live_data("Qual é a lotação exata do ponto agora?"))

if __name__ == "__main__":
    unittest.main()
