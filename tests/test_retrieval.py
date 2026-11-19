import unittest
from src.retrieval import Retriever
from src.evaluate_retrieval import read_cases

class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever = Retriever()
        cls.cases = {c['id']: c for c in read_cases()}
    def test_known_fact_retrieves_relevant_chunk_top3(self):
        c=self.cases['Q03']
        got={x['chunk_id'] for x in self.retriever.retrieve(c['question'],3)}
        self.assertTrue(got.intersection(c['relevant_chunk_ids']))
    def test_gtfs_clock_time_retrieves_time_rule(self):
        c=self.cases['Q06']
        got=self.retriever.retrieve(c['question'],1)[0]['chunk_id']
        self.assertEqual(got,'GTFS-002')

if __name__ == "__main__":
    unittest.main()
