import unittest
from models.keyword_model import Keyword
import json


class TestCategory(unittest.TestCase):
    def setUp(self):
        pass

    def test_keyword_constructor(self):
        keyword = Keyword(2, 1, 'Privacy', 'Datenschutz', 'Vie privée')
        self.assertEqual(keyword.eddb_id, 2)
        self.assertEqual(keyword.category_id, 1)
        self.assertEqual(keyword.name_en, 'Privacy')
        self.assertEqual(keyword.name_de, 'Datenschutz')
        self.assertEqual(keyword.name_fr, 'Vie privée')

    def test_keyword_name_fail(self):
        with self.assertRaises(ValueError):
            Keyword(2, 1, None, 'Datenschutz', 'Vie privée')
        with self.assertRaises(ValueError):
            Keyword(2, 1, 'Privacy', None, 'Vie privée')
        with self.assertRaises(ValueError):
            Keyword(2, 1, 'Privacy', 'Datenschutz', None)

    def test_from_and_to_json(self):
        keyword = Keyword(3, 2, 'Privacy', 'Datenschutz', 'Vie privée')
        json_str = json.dumps(keyword.__dict__)
        json_data = json.loads(json_str)
        new_keyword = Keyword(**json_data)
        self.assertEqual(new_keyword.eddb_id, 3)
        self.assertEqual(new_keyword.category_id, 2)
        self.assertEqual(new_keyword.name_en, 'Privacy')
        self.assertEqual(new_keyword.name_de, 'Datenschutz')
        self.assertEqual(new_keyword.name_fr, 'Vie privée')

    def test_resource_type(self):
        keyword = Keyword(2, 1, 'Privacy', 'Datenschutz', 'Vie privée')
        self.assertEqual(keyword.resource_type(), 'Datacant:Keyword')


if __name__ == '__main__':
    unittest.main()
