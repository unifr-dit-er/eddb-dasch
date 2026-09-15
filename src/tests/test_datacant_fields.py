import unittest
from fields.datacant import (
    DecisionDocumentLink,
    EddbId,
    NameDe,
    NameFr,
)


class TestDatacantFields(unittest.TestCase):
    def setUp(self):
        pass

    def test_decision_document_link_constructor(self):
        field = DecisionDocumentLink(44)
        self.assertEqual(field.name, 'Datacant:linkToDocumentValue')
        self.assertEqual(field.value, 44)

        field_null = DecisionDocumentLink(None)
        self.assertIsNone(field_null.value)

    def test_decision_document_link_type(self):
        field = DecisionDocumentLink(44)
        self.assertEqual(field.get_type(), 'knora-api:LinkValue')

    def test_decision_document_link_payload_create(self):
        field = DecisionDocumentLink(44)
        field.set_value_iri(4422)
        key_value = field.to_knora()
        v = next(iter(key_value.values()))
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:linkValueHasTargetIri']['@id'], 4422)

        self.assertEqual(DecisionDocumentLink(None).to_knora(), {})

    def test_eddb_id(self):
        field = EddbId(1)
        self.assertEqual(field.name, 'Datacant:hasId')
        self.assertEqual(field.value, 1)

    def test_eddb_id_fail(self):
        with self.assertRaises(TypeError):
            EddbId('1')
        with self.assertRaises(ValueError):
            EddbId(-3)

    def test_name_de(self):
        field = NameDe(' Schuldbetreibung und Konkurs ')
        self.assertEqual(field.name, 'Datacant:hasNameDe')
        self.assertEqual(field.value, 'Schuldbetreibung und Konkurs')

    def test_name_de_fail(self):
        with self.assertRaises(ValueError):
            NameDe(' ')
        with self.assertRaises(ValueError):
            NameDe(None)

    def test_name_fr(self):
        field = NameFr(' Poursuite pour dette et faillite ')
        self.assertEqual(field.name, 'Datacant:hasNameFr')
        self.assertEqual(field.value, 'Poursuite pour dette et faillite')

    def test_name_fr_fail(self):
        with self.assertRaises(ValueError):
            NameFr(' ')
        with self.assertRaises(ValueError):
            NameFr(None)


if __name__ == '__main__':
    unittest.main()
