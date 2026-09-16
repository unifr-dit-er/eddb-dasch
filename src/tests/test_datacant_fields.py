import unittest
from fields.datacant import (
    Canton,
    CategoryLink,
    DateGreg,
    DecisionDocumentLink,
    Description,
    EddbId,
    FileName,
    KeywordLink,
    Name,
)


class TestDatacantFields(unittest.TestCase):
    def setUp(self):
        pass

    def test_canton_constructor(self):
        field = Canton('FR')
        self.assertEqual(field.name, 'Datacant:hasCantonList')
        self.assertEqual(field.value, 'FR')

    def test_canton_type(self):
        field = Canton('FR')
        self.assertEqual(field.get_type(), 'knora-api:ListValue')

    def test_canton_is_updated_false(self):
        iri = '1234'
        field = Canton('FR')
        field.set_value_iri(iri)
        dasch_obj = {field.name: {'knora-api:listValueAsListNode': {'@id': iri}}}
        self.assertFalse(field.is_updated(dasch_obj))

    def test_canton_is_updated_true(self):
        field = Canton('FR')
        field.set_value_iri('2')
        dasch_obj = {field.name: {'knora-api:listValueAsListNode': {'@id': '1'}}}
        self.assertTrue(field.is_updated(dasch_obj))

    def test_canton_payload_create(self):
        field = Canton('FR')
        field.set_value_iri(1234)
        key_value = field.to_knora()
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:listValueAsListNode']['@id'], 1234)

    def test_canton_payload_value_update(self):
        field = Canton('FR')
        field.set_value_iri('1b')
        dasch_obj = {field.name: {'@id': '1a'}}
        key_value = field.payload_value_update(dasch_obj)
        v = key_value[field.name]
        self.assertEqual(v['@id'], '1a')
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:listValueAsListNode']['@id'], '1b')

    def test_category_link_constructor(self):
        field = CategoryLink(2)
        self.assertEqual(field.name, 'Datacant:linkToCategoryValue')
        self.assertEqual(field.value, 2)

    def test_category_link_type(self):
        field = CategoryLink(2)
        self.assertEqual(field.get_type(), 'knora-api:LinkValue')

    def test_category_link_is_updated_false(self):
        field = CategoryLink(2)
        field.set_value_iri('1a')
        dasch_obj = {field.name: {'knora-api:linkValueHasTarget': {'@id': '1a'}}}
        self.assertFalse(field.is_updated(dasch_obj))

    def test_category_link_is_updated_true(self):
        field = CategoryLink(2)
        field.set_value_iri('1a')
        dasch_obj = {field.name: {'knora-api:linkValueHasTarget': {'@id': '1b'}}}
        self.assertTrue(field.is_updated(dasch_obj))

    def test_category_link_payload_create(self):
        field = CategoryLink(2)
        field.set_value_iri('1a')
        key_value = field.to_knora()
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:linkValueHasTargetIri']['@id'], '1a')

    def test_category_link_payload_value_update(self):
        field = CategoryLink(2)
        field.set_value_iri('1b')
        dasch_obj = {field.name: {'@id': '1a'}}
        key_value = field.payload_value_update(dasch_obj)
        v = key_value[field.name]
        self.assertEqual(v['@id'], '1a')
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:linkValueHasTargetIri']['@id'], '1b')

    def test_date_greg_constructor(self):
        field = DateGreg('2021-08-12')
        self.assertEqual(field.name, 'Datacant:hasDateIssued')
        self.assertEqual(field.value, '2021-08-12')

    def test_date_greg_constructor_fail(self):
        with self.assertRaises(TypeError):
            DateGreg('Not a date')

    def test_date_greg_type(self):
        field = DateGreg('2021-08-12')
        self.assertEqual(field.get_type(), 'knora-api:DateValue')

    def test_date_greg_is_updated_false(self):
        field = DateGreg('2021-08-12')
        dasch_obj = {field.name: {'knora-api:valueAsString': 'GREGORIAN:2021-08-12 CE'}}
        self.assertFalse(field.is_updated(dasch_obj))

    def test_date_greg_is_updated_true(self):
        field = DateGreg('2021-08-12')
        dasch_obj = {field.name: {'knora-api:valueAsString': 'GREGORIAN:2022-09-13 CE'}}
        self.assertTrue(field.is_updated(dasch_obj))

    def test_date_greg_payload_create(self):
        field = DateGreg('2021-08-12')
        key_value = field.to_knora()
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:dateValueHasStartYear'], 2021)
        self.assertEqual(v['knora-api:dateValueHasEndYear'], 2021)
        self.assertEqual(v['knora-api:dateValueHasStartMonth'], 8)
        self.assertEqual(v['knora-api:dateValueHasEndMonth'], 8)
        self.assertEqual(v['knora-api:dateValueHasStartDay'], 12)
        self.assertEqual(v['knora-api:dateValueHasEndDay'], 12)
        self.assertEqual(v['knora-api:dateValueHasStartEra'], 'CE')
        self.assertEqual(v['knora-api:dateValueHasEndEra'], 'CE')
        self.assertEqual(v['knora-api:dateValueHasCalendar'], 'GREGORIAN')

    def test_date_greg_payload_value_update(self):
        field = DateGreg('2021-08-12')
        dasch_obj = {field.name: {'@id': '1a'}}
        key_value = field.payload_value_update(dasch_obj)
        v = key_value[field.name]
        self.assertEqual(v['@id'], '1a')
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:dateValueHasStartYear'], 2021)
        self.assertEqual(v['knora-api:dateValueHasEndYear'], 2021)
        self.assertEqual(v['knora-api:dateValueHasStartMonth'], 8)
        self.assertEqual(v['knora-api:dateValueHasEndMonth'], 8)
        self.assertEqual(v['knora-api:dateValueHasStartDay'], 12)
        self.assertEqual(v['knora-api:dateValueHasEndDay'], 12)
        self.assertEqual(v['knora-api:dateValueHasStartEra'], 'CE')
        self.assertEqual(v['knora-api:dateValueHasEndEra'], 'CE')
        self.assertEqual(v['knora-api:dateValueHasCalendar'], 'GREGORIAN')

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
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:linkValueHasTargetIri']['@id'], 4422)

        self.assertEqual(DecisionDocumentLink(None).to_knora(), {})

    def test_description_constructor(self):
        field = Description('Private Nutzung von Daten', 'de')
        self.assertEqual(field.name, 'Datacant:hasDescriptionDe')
        self.assertEqual(field.value, 'Private Nutzung von Daten')

    def test_description_constructor_fail(self):
        with self.assertRaises(ValueError):
            Description('', 'fr')

        with self.assertRaises(ValueError):
            Description('Invalid language', 'en')

    def test_description_type(self):
        field = Description('Private Nutzung von Daten', 'de')
        self.assertEqual(field.get_type(), 'knora-api:TextValue')

    def test_description_is_update_false(self):
        field = Description('Some description', 'fr')
        dasch_obj = {field.name: {'knora-api:valueAsString': 'Some description'}}
        self.assertFalse(field.is_updated(dasch_obj))

    def test_description_is_update_true(self):
        field = Description('New description', 'fr')
        dasch_obj = {field.name: {'knora-api:valueAsString': 'Old description'}}
        self.assertTrue(field.is_updated(dasch_obj))

    def test_description_payload_create(self):
        field = Description('Private Nutzung von Daten', 'de')
        key_value = field.to_knora()
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:valueAsString'], 'Private Nutzung von Daten')

    def test_description_payload_value_update(self):
        field = Description('Private Nutzung von Daten', 'de')
        dasch_obj = {field.name: {'@id': '1a'}}
        key_value = field.payload_value_update(dasch_obj)
        v = key_value[field.name]
        self.assertEqual(v['@id'], '1a')
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:valueAsString'], 'Private Nutzung von Daten')

    def test_eddb_id_constructor(self):
        field = EddbId(1)
        self.assertEqual(field.name, 'Datacant:hasId')
        self.assertEqual(field.value, 1)

    def test_eddb_id_constructor_fail(self):
        with self.assertRaises(TypeError):
            EddbId('1')
        with self.assertRaises(ValueError):
            EddbId(-3)

    def test_filename_constructor(self):
        field = FileName('FR_2021-08-12.pdf')
        self.assertEqual(field.name, 'Datacant:hasFileName')
        self.assertEqual(field.value, 'FR_2021-08-12.pdf')

    def test_filename_type(self):
        field = FileName('FR_2021-08-12.pdf')
        self.assertEqual(field.get_type(), 'knora-api:TextValue')

    def test_keyword_link_constructor(self):
        field = KeywordLink([3, 72])
        self.assertEqual(field.name, 'Datacant:linkToKeywordValue')
        self.assertEqual(field.value, [3, 72])

    def test_keyword_link_constructor_fail(self):
        with self.assertRaises(TypeError):
            KeywordLink(3)

    def test_name_constructor(self):
        field = Name(' Schuldbetreibung und Konkurs ', 'de')
        self.assertEqual(field.name, 'Datacant:hasNameDe')
        self.assertEqual(field.value, 'Schuldbetreibung und Konkurs')

    def test_name_constructor_fail(self):
        with self.assertRaises(ValueError):
            Name(' ', 'fr')
        with self.assertRaises(ValueError):
            Name('Invalid language', 'en')


if __name__ == '__main__':
    unittest.main()
