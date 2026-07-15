import unittest
from models.category_model import Category
import json


class TestCategory(unittest.TestCase):
    def setUp(self):
        pass

    def test_category_constructor(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        self.assertEqual(category.eddb_id, 1)
        self.assertEqual(category.name_en, 'Privacy')
        self.assertEqual(category.name_de, 'Datenschutz')
        self.assertEqual(category.name_fr, 'Vie privée')

    def test_category_name_fail(self):
        with self.assertRaises(ValueError):
            Category(1, None, 'Datenschutz', 'Vie privée')
        with self.assertRaises(ValueError):
            Category(1, 'Privacy', None, 'Vie privée')
        with self.assertRaises(ValueError):
            Category(1, 'Privacy', 'Datenschutz', None)

    def test_from_and_to_json(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        json_str = json.dumps(category.__dict__)
        json_data = json.loads(json_str)
        new_category = Category(**json_data)
        self.assertEqual(new_category.eddb_id, 1)
        self.assertEqual(new_category.name_en, 'Privacy')
        self.assertEqual(new_category.name_de, 'Datenschutz')
        self.assertEqual(new_category.name_fr, 'Vie privée')

    def test_resource_type(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        self.assertEqual(category.resource_type(), 'Datacant:Category')


if __name__ == '__main__':
    unittest.main()
