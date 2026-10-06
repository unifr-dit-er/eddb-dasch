import unittest
from unittest.mock import MagicMock, patch
import json
from pathlib import Path
from database.datacant import Datacant


class TestDatacant(unittest.TestCase):
    def setUp(self):
        dasch_token_response = MagicMock()
        dasch_token_response.status_code = 200
        dasch_token_response.json.return_value = {'token': 'af32-3242'}

        def mock_post(url, *args, **kwargs):
            if url.endswith('/v2/authentication'):
                return dasch_token_response
            raise ValueError(f'Unexpected URL: {url}')

        with patch('requests.post', side_effect=mock_post):
            directory = Path('tests/resources/datacant')
            self.db = Datacant(directory)

    def test_get_dasch(self):
        category_3 = self.db.get_dasch('Datacant:Category', 3)
        self.assertEqual(category_3['rdfs:label'], 'Surveillance')
        category_22 = self.db.get_dasch('Datacant:Category', 22)
        self.assertEqual(category_22['rdfs:label'], 'Justifications')
        keyword_3 = self.db.get_dasch('Datacant:Keyword', 3)
        self.assertEqual(keyword_3['rdfs:label'], 'Video surveillance')
        keyword_72 = self.db.get_dasch('Datacant:Keyword', 72)
        self.assertEqual(keyword_72['rdfs:label'], 'Consent')

    def test_get_dasch_items(self):
        categories = self.db.get_dasch_items('Datacant:Category')
        self.assertEqual(len(list(categories)), 2)
        keywords = self.db.get_dasch_items('Datacant:Keyword')
        self.assertEqual(len(list(keywords)), 2)
        decision_summary = self.db.get_dasch_items('Datacant:DecisionSummary')
        self.assertEqual(len(list(decision_summary)), 2)

    def test_resource_types(self):
        types = self.db.resource_types()
        self.assertEqual(len(types), 4)
        self.assertEqual(types[0], 'Datacant:Category')
        self.assertEqual(types[1], 'Datacant:Keyword')
        self.assertEqual(types[2], 'Datacant:DecisionDocument')
        self.assertEqual(types[3], 'Datacant:DecisionSummary')


if __name__ == '__main__':
    unittest.main()
