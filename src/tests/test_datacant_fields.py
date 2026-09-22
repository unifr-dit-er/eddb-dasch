import unittest
from fields.datacant import (
    Abstract,
    Attachment,
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

    def test_abstract_constructor(self):
        updated_at = '2026-02-20 13:37:26+00:00'
        field = Abstract('A. arbeitet seit 1991', 'de', updated_at)
        self.assertEqual(field.name, 'Datacant:hasAbstractDe')
        self.assertEqual(field.value, 'A. arbeitet seit 1991')
        self.assertEqual(field.updated_at, '2026-02-20 13:37:26+00:00')

    def test_abstract_type(self):
        updated_at = '2026-02-20 13:37:26+00:00'
        field = Abstract('A. arbeitet seit 1991', 'de', updated_at)
        self.assertEqual(field.get_type(), 'knora-api:TextValue')

    def test_abstract_is_updated_false(self):
        created_at = '2026-09-16T08:16:43.552906918Z'
        updated_at = '2026-02-20 13:37:26+00:00'
        field = Abstract('A. arbeitet seit 1991', 'de', updated_at)
        dasch_obj = {field.name: {'knora-api:valueCreationDate': {'@value': created_at}}}
        self.assertFalse(field.is_updated(dasch_obj))

    # Note: we don't test `test_abstract_is_updated_true` because api is required.

    def test_abstract_payload_create(self):
        updated_at = '2026-02-20 13:37:26+00:00'
        field = Abstract('A. arbeitet seit 1991', 'de', updated_at)
        key_value = field.to_knora()
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:textValueAsXml'], field.value)
        self.assertTrue(v['knora-api:textValueHasMapping']['@id'].endswith('StandardMapping'))

    def test_abstract_payload_value_update(self):
        updated_at = '2026-02-20 13:37:26+00:00'
        field = Abstract('A. arbeitet seit 1991', 'de', updated_at)
        dasch_obj = {field.name: {'@id': '1a'}}
        key_value = field.payload_value_update(dasch_obj)
        v = key_value[field.name]
        self.assertEqual(v['@id'], '1a')
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:textValueAsXml'], field.value)
        self.assertIsNone(v['knora-api:textValueHasMapping']['@id'])

    def test_attachment_constructor(self):
        updated_at = '2026-02-20 13:37:26+00:00'
        field = Attachment('https://', 'tmp.pdf', 'ba7816bf8', updated_at)
        self.assertEqual(field.name, 'knora-api:hasDocumentFileValue')
        self.assertEqual(field.value, 'tmp.pdf')
        self.assertEqual(field.checksum, 'ba7816bf8')
        self.assertEqual(field.eddb_url, 'https://')
        self.assertEqual(field.license, 'http://rdfh.ch/licenses/public-domain')
        self.assertEqual(field.copyright, 'Public Domain - Not Protected by Copyright')
        self.assertEqual(field.authors, ['Swiss court'])

    def test_attachment_type(self):
        field = Attachment('https://', 'tmp.pdf', None, '2026-02-20 13:37:26+00:00')
        self.assertEqual(field.get_type(), 'knora-api:DocumentFileValue')

    def test_attachment_is_updated_false(self):
        field = Attachment('https://', 'tmp.pdf', 'ab', '2026-02-20 13:37:26+00:00')
        dasch_obj = {
            field.name: {
                'knora-api:valueCreationDate': {'@value': '2026-02-20 13:37:26+00:00'}
            },
            'Datacant:hasChecksum': {'knora-api:valueAsString': 'ab'},
        }
        self.assertFalse(field.is_updated(dasch_obj))

    def test_attachment_is_updated_by_checksum(self):
        field = Attachment('https://', 'tmp.pdf', 'bc', '2026-02-20 13:37:26+00:00')
        dasch_obj = {
            field.name: {
                'knora-api:valueCreationDate': {'@value': '2026-02-20 13:37:26+00:00'}
            },
            'Datacant:hasChecksum': {'knora-api:valueAsString': 'ab'},
        }
        self.assertTrue(field.is_updated(dasch_obj))

    def test_attachment_is_updated_by_date(self):
        field = Attachment('https://', 'tmp.pdf', 'ab', '2026-02-21 00:00:00+00:00')
        dasch_obj = {
            field.name: {
                'knora-api:valueCreationDate': {'@value': '2026-02-20 13:37:26+00:00'}
            },
            'Datacant:hasChecksum': {'knora-api:valueAsString': 'ab'},
        }
        self.assertTrue(field.is_updated(dasch_obj))

    def test_attachment_payload_create(self):
        field = Attachment('https://', 'tmp.pdf', 'ab', '2026-02-21 00:00:00+00:00')
        key_value = field.to_knora()
        v = key_value[field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:fileValueHasFilename'], 'tmp.pdf')
        self.assertTrue(v['knora-api:hasLicense']['@id'].endswith('/licenses/public-domain'))
        self.assertTrue(v['knora-api:hasCopyrightHolder'].startswith('Public Domain'))
        self.assertEqual(v['knora-api:hasAuthorship'], ['Swiss court'])

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

    def test_eddb_id_type(self):
        field = EddbId(1)
        self.assertEqual(field.get_type(), 'knora-api:IntValue')

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

    def test_keyword_link_type(self):
        field = KeywordLink([3, 72])
        self.assertEqual(field.get_type(), 'knora-api:LinkValue')

    def test_keyword_link_is_updated_false(self):
        field = KeywordLink([3, 72])
        field.set_value_iri(['1a', '1b'])
        dasch_obj = {
            field.name: [
                {'knora-api:linkValueHasTargetIri': {'@id': '1a'}},
                {'knora-api:linkValueHasTargetIri': {'@id': '1b'}},
            ]
        }
        self.assertFalse(field.is_updated(dasch_obj))

    def test_keyword_link_is_updated_true(self):
        field = KeywordLink([3, 72])
        field.set_value_iri(['1a', '1b'])
        dasch_obj = {
            # Note: It is not a list when there is only one keyword.
            field.name: {
                'knora-api:linkValueHasTargetIri': {'@id': '1a'},
            }
        }
        self.assertTrue(field.is_updated(dasch_obj))

    def test_keyword_link_payload_create(self):
        field = KeywordLink([3, 72])
        field.set_value_iri(['1a', '1b'])
        key_value = field.to_knora()
        values = key_value[field.name]
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0]['@type'], field.get_type())
        self.assertEqual(values[0]['knora-api:linkValueHasTargetIri']['@id'], '1a')
        self.assertEqual(values[1]['@type'], field.get_type())
        self.assertEqual(values[1]['knora-api:linkValueHasTargetIri']['@id'], '1b')

    def test_keyword_link_payload_value_add(self):
        field = KeywordLink([3, 72])
        field.set_value_iri(['1a', '1b'])
        dasch_obj = {
            field.name: [
                {'knora-api:linkValueHasTarget': {'@id': '1a'}},
            ]
        }
        key_value = field.payload_value_add(dasch_obj)
        self.assertEqual(len(key_value), 1)
        v = key_value[0][field.name]
        self.assertEqual(v['@type'], field.get_type())
        self.assertEqual(v['knora-api:linkValueHasTargetIri']['@id'], '1b')

    def test_keyword_link_payload_value_del(self):
        field = KeywordLink([3])
        field.set_value_iri(['1a'])
        dasch_obj = {
            field.name: [
                {'@id': '22', 'knora-api:linkValueHasTarget': {'@id': '1a'}},
                {'@id': '33', 'knora-api:linkValueHasTarget': {'@id': '1b'}},
            ]
        }
        key_value = field.payload_value_del(dasch_obj)
        self.assertEqual(len(key_value), 1)
        v = key_value[0][field.name]
        self.assertEqual(v['@id'], '33')
        self.assertEqual(v['@type'], field.get_type())

    def test_keyword_link_payload_value_update(self):
        with self.assertRaises(RuntimeError):
            field = KeywordLink([3])
            field.payload_value_update(None)

    def test_name_constructor(self):
        field = Name(' Schuldbetreibung und Konkurs ', 'de')
        self.assertEqual(field.name, 'Datacant:hasNameDe')
        self.assertEqual(field.value, 'Schuldbetreibung und Konkurs')

    def test_name_constructor_fail(self):
        with self.assertRaises(ValueError):
            Name(' ', 'fr')
        with self.assertRaises(ValueError):
            Name('Invalid language', 'en')

    def test_name_type(self):
        field = Name(' Schuldbetreibung und Konkurs ', 'de')
        self.assertEqual(field.get_type(), 'knora-api:TextValue')


if __name__ == '__main__':
    unittest.main()
