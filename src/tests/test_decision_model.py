import unittest
from models.decision_model import Decision


class TestDecision(unittest.TestCase):
    def setUp(self):
        self.attributes = {
            'eddb_id': 3,
            'date_issued': '2025-01-13',
            'updated_at': '2026-02-20 13:37:26+00:00',
            'canton': 'FR',
            'desc_de': '',
            'desc_fr': 'Une description',
            'abstract_de': '',
            'abstract_fr': 'Un résumé',
            'url_file': 'https://www.unifr.ch/example/download/2005.06.28-5__vzhl.pdf',
            'keywords_id': [4, 7],
        }

    def test_constructor(self):
        decision = Decision(**self.attributes)
        self.assertEqual(decision.eddb_id, 3)
        self.assertEqual(decision.canton, 'FR')
        self.assertEqual(decision.desc_de, '')
        self.assertEqual(decision.desc_fr, 'Une description')
        self.assertEqual(decision.abstract_de, '')
        self.assertEqual(decision.abstract_fr, 'Un résumé')

    def test_constructor_without_keyword(self):
        attributes = self.attributes
        attributes['keywords_id'] = []
        with self.assertRaises(ValueError):
            Decision(**attributes)

    def test_filename(self):
        decision = Decision(**self.attributes)
        self.assertEqual(decision.filename(), 'FR_2025-01-13.pdf')

    def test_filename_eddb(self):
        decision = Decision(**self.attributes)
        self.assertEqual(decision.filename_eddb(), '2005.06.28-5__vzhl.pdf')

    def test_resource_type(self):
        decision = Decision(**self.attributes)
        self.assertEqual(decision.resource_type(), 'Datacant:Decisions')


if __name__ == '__main__':
    unittest.main()
