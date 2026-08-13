import unittest
from fields.datacant import EddbId, NameDe, NameFr
from models.category_model import Category
import json


class TestCategory(unittest.TestCase):
    def setUp(self):
        self.dasch_db = {'category': {}}
        with open('tests/resources/dasch_category.json', 'r') as txt:
            tmp = json.load(txt)
            self.dasch_db['category'] = {int(k): v for k, v in tmp['category'].items()}

    def test_category_constructor(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        self.assertEqual(category.eddb_id, EddbId(1))
        self.assertEqual(category.name_en, 'Privacy')
        self.assertEqual(category.name_de, NameDe('Datenschutz'))
        self.assertEqual(category.name_fr, NameFr('Vie privée'))

    def test_category_name_fail(self):
        with self.assertRaises(ValueError):
            Category(1, None, 'Datenschutz', 'Vie privée')
        with self.assertRaises(ValueError):
            Category(1, 'Privacy', None, 'Vie privée')
        with self.assertRaises(ValueError):
            Category(1, 'Privacy', 'Datenschutz', None)

    def test_from_and_to_json(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        json_str = json.dumps(category.to_dict())
        json_data = json.loads(json_str)
        new_category = Category(**json_data)
        self.assertEqual(new_category.eddb_id, 1)
        self.assertEqual(new_category.name_en, 'Privacy')
        self.assertEqual(new_category.name_de, 'Datenschutz')
        self.assertEqual(new_category.name_fr, 'Vie privée')

    def test_label(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        self.assertEqual(category.label(), 'Privacy')

    def test_payload_create(self):
        category = Category(1, 'Privacy', 'Datenschutz', 'Vie privée')
        payload = category.payload_create()
        self.assertEqual(payload['@type'], category.resource_type())
        self.assertEqual(payload['rdfs:label'], category.label())

        eddb_id = payload['Datacant:hasId']['knora-api:intValueAsInt']
        self.assertEqual(eddb_id, category.eddb_id.value)

        name_de = payload['Datacant:hasNameDe']['knora-api:valueAsString']
        self.assertEqual(name_de, category.name_de.value)

        name_fr = payload['Datacant:hasNameFr']['knora-api:valueAsString']
        self.assertEqual(name_fr, category.name_fr.value)

    def test_payload_update_fields(self):
        category = Category(3, 'Surveillance', 'Überwachung2', 'Surveillance2')
        (payloads, _, _) = category.payload_update_fields(self.dasch_db)
        self.assertEqual(len(payloads), 2)

        name_de = payloads[0]['Datacant:hasNameDe']['knora-api:valueAsString']
        self.assertEqual(payloads[0]['@type'], Category.resource_type())
        self.assertEqual(name_de, 'Überwachung2')

        name_fr = payloads[1]['Datacant:hasNameFr']['knora-api:valueAsString']
        self.assertEqual(payloads[1]['@type'], Category.resource_type())
        self.assertEqual(name_fr, 'Surveillance2')

    def test_payload_update_label(self):
        dasch_obj = self.dasch_db['category'][3]
        category = Category(3, 'Surveillance2', 'Überwachung2', 'Surveillance2')
        payload = category.payload_update_label(dasch_obj)
        self.assertEqual(payload['@type'], category.resource_type())
        self.assertEqual(payload['rdfs:label'], category.label())
        self.assertEqual(payload['knora-api:lastModificationDate']['@value'], None)

    def test_resource_type(self):
        self.assertEqual(Category.resource_type(), 'Datacant:Category')


if __name__ == '__main__':
    unittest.main()
