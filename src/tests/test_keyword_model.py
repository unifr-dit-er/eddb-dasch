import unittest
import json
from pathlib import Path
from fields.datacant import CategoryLink, EddbId, NameDe, NameFr
from models.keyword_model import Keyword


class TestKeyword(unittest.TestCase):
    def setUp(self):
        file = Path('tests/resources/data_dasch.json')
        data = json.loads(file.read_text(encoding='utf-8'))
        data['category'] = {int(k): v for k, v in data['category'].items()}
        data['keyword'] = {int(k): v for k, v in data['keyword'].items()}
        data['decision'] = {int(k): v for k, v in data['decision'].items()}
        self.dasch_db = data

    def test_constructor(self):
        keyword = Keyword(72, 22, 'Consent', 'Einwilligung', 'Consentement')
        self.assertEqual(keyword.eddb_id, EddbId(72))
        self.assertEqual(keyword.category_id, CategoryLink(22))
        self.assertEqual(keyword.name_en, 'Consent')
        self.assertEqual(keyword.name_de, NameDe('Einwilligung'))
        self.assertEqual(keyword.name_fr, NameFr('Consentement'))

    def test_constructor_fail(self):
        with self.assertRaises(ValueError):
            Keyword(72, 22, None, 'Einwilligung', 'Consentement')
        with self.assertRaises(ValueError):
            Keyword(72, 22, 'Consent', None, 'Consentement')
        with self.assertRaises(ValueError):
            Keyword(72, 22, 'Consent', 'EinwilligungDatenschutz', None)

    def test_fill_iri_values(self):
        keyword = Keyword(72, 22, 'Consent', 'Einwilligung', 'Consentement')
        keyword.fill_iri_values(self.dasch_db)
        iri = keyword.category_id.value_iri
        self.assertEqual(iri, 'http://rdfh.ch/0871/TG3ioIXHQ5-FNWmiLEzOFw')

    def test_from_and_to_json(self):
        keyword = Keyword(72, 22, 'Consent', 'Einwilligung', 'Consentement')
        json_str = json.dumps(keyword.to_dict())
        json_data = json.loads(json_str)
        new_keyword = Keyword(**json_data)
        self.assertEqual(new_keyword.eddb_id, EddbId(72))
        self.assertEqual(new_keyword.category_id, CategoryLink(22))
        self.assertEqual(new_keyword.name_en, 'Consent')
        self.assertEqual(new_keyword.name_de, NameDe('Einwilligung'))
        self.assertEqual(new_keyword.name_fr, NameFr('Consentement'))

    def test_has_file_field(self):
        keyword = Keyword(72, 22, 'Consent', 'Einwilligung', 'Consentement')
        self.assertFalse(keyword.has_file_field())

    def test_label(self):
        keyword = Keyword(72, 22, 'Consent', 'Einwilligung', 'Consentement')
        self.assertEqual(keyword.label(), 'Consent')

    def test_payload_create(self):
        keyword = Keyword(72, 22, 'Consent', 'Einwilligung', 'Consentement')
        keyword.fill_iri_values(self.dasch_db)
        payload = keyword.payload_create()
        self.assertEqual(payload['@type'], keyword.resource_type())
        self.assertEqual(payload['rdfs:label'], keyword.label())

        eddb_id = payload['Datacant:hasId']['knora-api:intValueAsInt']
        self.assertEqual(eddb_id, keyword.eddb_id.value)

        iri = extract_category_iri_from_payload(payload)
        self.assertEqual(iri, 'http://rdfh.ch/0871/TG3ioIXHQ5-FNWmiLEzOFw')

        name_de = payload['Datacant:hasNameDe']['knora-api:valueAsString']
        self.assertEqual(name_de, keyword.name_de.value)

        name_fr = payload['Datacant:hasNameFr']['knora-api:valueAsString']
        self.assertEqual(name_fr, keyword.name_fr.value)

    def test_payload_update_fields(self):
        keyword = Keyword(72, 3, 'Consent', 'Einwilligung2', 'Consentement2')
        keyword.fill_iri_values(self.dasch_db)
        (payloads, _, _) = keyword.payload_update_fields(self.dasch_db)
        self.assertEqual(len(payloads), 3)

        cat_iri = extract_category_iri_from_payload(payloads[0])
        self.assertEqual(payloads[0]['@type'], Keyword.resource_type())
        self.assertEqual(cat_iri, 'http://rdfh.ch/0871/oTMF94U2TrCoWzM2iW1Jyg')

        name_de = payloads[1]['Datacant:hasNameDe']['knora-api:valueAsString']
        self.assertEqual(payloads[1]['@type'], Keyword.resource_type())
        self.assertEqual(name_de, 'Einwilligung2')

        name_fr = payloads[2]['Datacant:hasNameFr']['knora-api:valueAsString']
        self.assertEqual(payloads[2]['@type'], Keyword.resource_type())
        self.assertEqual(name_fr, 'Consentement2')

    def test_payload_update_label(self):
        dasch_obj = self.dasch_db['keyword'][72]
        keyword = Keyword(72, 22, 'Consent2', 'Einwilligung', 'Consentement')
        payload = keyword.payload_update_label(dasch_obj)
        last_modif = None
        self.assertEqual(payload['@type'], keyword.resource_type())
        self.assertEqual(payload['rdfs:label'], keyword.label())
        self.assertEqual(payload['knora-api:lastModificationDate']['@value'], last_modif)

    def test_resource_type(self):
        self.assertEqual(Keyword.resource_type(), 'Datacant:Keyword')


def extract_category_iri_from_payload(p):
    return p \
        .get('Datacant:linkToCategoryValue') \
        .get('knora-api:linkValueHasTargetIri') \
        .get('@id')


if __name__ == '__main__':
    unittest.main()
