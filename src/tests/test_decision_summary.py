import unittest
import json
from pathlib import Path
from fields.datacant import (
    Abstract,
    Canton,
    DateGreg,
    DecisionDocumentLink,
    Description,
    EddbId,
    KeywordLink,
)
from models.decision_summary import DecisionSummary


class TestDecisionSummary(unittest.TestCase):
    def setUp(self):
        file = Path('tests/resources/data_dasch.json')
        data = json.loads(file.read_text(encoding='utf-8'))
        data['category'] = {int(k): v for k, v in data['category'].items()}
        data['keyword'] = {int(k): v for k, v in data['keyword'].items()}
        data['Datacant:DecisionDocument'] = \
            {int(k): v for k, v in data['Datacant:DecisionDocument'].items()}
        data['Datacant:DecisionSummary'] = \
            {int(k): v for k, v in data['Datacant:DecisionSummary'].items()}
        self.dasch_db = data
        self.attributes = {
            'eddb_id': 257,
            'date_issued': '2021-08-12',
            'updated_at': '2026-02-20 13:37:26+00:00',
            'canton': 'FR',
            'desc_de': 'Private Nutzung von Daten',
            'desc_fr': 'Utilisation à des fins privées',
            'abstract_de': 'A. arbeitet seit 1991',
            'abstract_fr': 'Depuis 1991',
            'keywords_id': [3, 72],
            'decision_document': None,
        }

    def test_constructor(self):
        decision = DecisionSummary(**self.attributes)
        edit = self.attributes['updated_at']
        self.assertEqual(decision.eddb_id, EddbId(257))
        self.assertEqual(decision.date_issued, DateGreg('2021-08-12'))
        self.assertEqual(decision.canton, Canton('FR'))
        self.assertEqual(decision.desc_de, Description('Private Nutzung von Daten', 'de'))
        self.assertEqual(decision.desc_fr, Description('Utilisation à des fins privées', 'fr'))
        self.assertEqual(decision.abstract_de, Abstract('A. arbeitet seit 1991', 'de', edit))
        self.assertEqual(decision.abstract_fr, Abstract('Depuis 1991', 'fr', edit))
        self.assertEqual(decision.keywords_id, KeywordLink([3, 72]))

    def test_constructor_fail(self):
        attributes = self.attributes
        attributes['keywords_id'] = []
        with self.assertRaises(ValueError):
            DecisionSummary(**attributes)

    def test_fill_iri_values(self):
        decision = DecisionSummary(**self.attributes)
        decision.fill_iri_values(self.dasch_db)

        canton_iri = decision.canton.value_iri
        self.assertEqual(canton_iri, 'http://rdfh.ch/lists/0871/fSKvY2DQTCC1imPR1tNS6w')

        self.assertEqual(decision.keywords_id.value_iri, [
            'http://rdfh.ch/0871/pFZt9mzuTimLwjdMUByMZg',
            'http://rdfh.ch/0871/qRMfCDGwToWQnbEouGVIaw',
        ])

        # TODO: add decision_document.

    def test_from_and_to_json(self):
        decision_original = DecisionSummary(**self.attributes)
        edit = self.attributes['updated_at']
        json_str = json.dumps(decision_original.to_dict())
        json_data = json.loads(json_str)
        decision = DecisionSummary(**json_data)
        self.assertEqual(decision.eddb_id, EddbId(257))
        self.assertEqual(decision.date_issued, DateGreg('2021-08-12'))
        self.assertEqual(decision.updated_at, '2026-02-20 13:37:26+00:00')
        self.assertEqual(decision.canton, Canton('FR'))
        self.assertEqual(decision.desc_de, Description('Private Nutzung von Daten', 'de'))
        self.assertEqual(decision.desc_fr, Description('Utilisation à des fins privées', 'fr'))
        self.assertEqual(decision.abstract_de, Abstract('A. arbeitet seit 1991', 'de', edit))
        self.assertEqual(decision.abstract_fr, Abstract('Depuis 1991', 'fr', edit))
        self.assertEqual(decision.keywords_id, KeywordLink([3, 72]))
        self.assertEqual(decision.decision_document, DecisionDocumentLink(None))

    def test_label(self):
        decision = DecisionSummary(**self.attributes)
        self.assertEqual(decision.label(), 'FR 2021-08-12')

    def test_payload_create(self):
        decision = DecisionSummary(**self.attributes)
        decision.fill_iri_values(self.dasch_db)
        payload = decision.payload_create()
        self.assertEqual(payload['@type'], decision.resource_type())
        self.assertEqual(payload['rdfs:label'], decision.label())

        eddb_id = payload['Datacant:hasId']['knora-api:intValueAsInt']
        self.assertEqual(eddb_id, decision.eddb_id.value)

        date = payload['Datacant:hasDateIssued']
        self.assertEqual(date['knora-api:dateValueHasStartYear'], 2021)
        self.assertEqual(date['knora-api:dateValueHasEndYear'], 2021)
        self.assertEqual(date['knora-api:dateValueHasStartMonth'], 8)
        self.assertEqual(date['knora-api:dateValueHasEndMonth'], 8)
        self.assertEqual(date['knora-api:dateValueHasStartDay'], 12)
        self.assertEqual(date['knora-api:dateValueHasEndDay'], 12)
        self.assertEqual(date['knora-api:dateValueHasStartEra'], 'CE')
        self.assertEqual(date['knora-api:dateValueHasEndEra'], 'CE')
        self.assertEqual(date['knora-api:dateValueHasCalendar'], 'GREGORIAN')

        canton = payload['Datacant:hasCantonList']['knora-api:listValueAsListNode']['@id']
        self.assertEqual(canton, 'http://rdfh.ch/lists/0871/fSKvY2DQTCC1imPR1tNS6w')

        desc_de = payload['Datacant:hasDescriptionDe']['knora-api:valueAsString']
        self.assertEqual(desc_de, decision.desc_de.value)

        desc_fr = payload['Datacant:hasDescriptionFr']['knora-api:valueAsString']
        self.assertEqual(desc_fr, decision.desc_fr.value)

        abstract_de = payload['Datacant:hasAbstractDe']['knora-api:textValueAsXml']
        self.assertEqual(abstract_de, decision.abstract_de.value)

        abstract_fr = payload['Datacant:hasAbstractFr']['knora-api:textValueAsXml']
        self.assertEqual(abstract_fr, decision.abstract_fr.value)

    def test_payload_update_fields(self):
        args = {
            'eddb_id': self.attributes['eddb_id'],
            'date_issued': '2021-08-13',
            'updated_at': '2026-08-24 10:20:00+00:00',
            'canton': 'ZG',
            'desc_de': 'Eine neue Beschreibung',
            'desc_fr': 'Une nouvelle description',
            'abstract_de': 'Eine neue Zusammenfassung',
            'abstract_fr': 'Un nouveau résumé',
            'keywords_id': [3],
            'decision_document': None,
        }
        decision = DecisionSummary(**args)
        decision.fill_iri_values(self.dasch_db)
        (payloads, links_add, links_del) = decision.payload_update_fields(self.dasch_db)
        self.assertEqual(len(payloads), 6)
        for i in range(6):
            self.assertEqual(payloads[i]['@type'], DecisionSummary.resource_type())

        date_issued = payloads[0]['Datacant:hasDateIssued']
        self.assertEqual(date_issued['knora-api:dateValueHasStartYear'], 2021)
        self.assertEqual(date_issued['knora-api:dateValueHasEndYear'], 2021)
        self.assertEqual(date_issued['knora-api:dateValueHasStartMonth'], 8)
        self.assertEqual(date_issued['knora-api:dateValueHasEndMonth'], 8)
        self.assertEqual(date_issued['knora-api:dateValueHasStartDay'], 13)
        self.assertEqual(date_issued['knora-api:dateValueHasEndDay'], 13)

        node = payloads[1]['Datacant:hasCantonList']['knora-api:listValueAsListNode']['@id']
        self.assertEqual(node, 'http://rdfh.ch/lists/0871/otPRlr4VSjmqcDXtT13v0w')

        desc_de = payloads[2]['Datacant:hasDescriptionDe']['knora-api:valueAsString']
        self.assertEqual(desc_de, 'Eine neue Beschreibung')

        desc_fr = payloads[3]['Datacant:hasDescriptionFr']['knora-api:valueAsString']
        self.assertEqual(desc_fr, 'Une nouvelle description')

        abstract_de = payloads[4]['Datacant:hasAbstractDe']['knora-api:textValueAsXml']
        self.assertEqual(abstract_de, 'Eine neue Zusammenfassung')

        abstract_fr = payloads[5]['Datacant:hasAbstractFr']['knora-api:textValueAsXml']
        self.assertEqual(abstract_fr, 'Un nouveau résumé')

        self.assertEqual(len(links_add), 0)
        self.assertEqual(len(links_del), 1)
        iri_to_remove = links_del[0] \
            .get('Datacant:linkToKeywordValue') \
            .get('knora-api:linkValueHasTargetIri') \
            .get('@id')
        self.assertEqual(iri_to_remove, 'http://rdfh.ch/0871/qRMfCDGwToWQnbEouGVIaw')

    def test_payload_update_label(self):
        dasch_obj = self.dasch_db['Datacant:DecisionSummary'][257]
        decision = DecisionSummary(**self.attributes)
        decision.canton = Canton('ZH')
        payload = decision.payload_update_label(dasch_obj)
        last_modif = '2026-08-18T09:56:20.337248959Z'
        self.assertEqual(payload['@type'], decision.resource_type())
        self.assertEqual(payload['rdfs:label'], decision.label())
        self.assertEqual(payload['knora-api:lastModificationDate']['@value'], last_modif)

    def test_resource_type(self):
        decision = DecisionSummary(**self.attributes)
        self.assertEqual(decision.resource_type(), 'Datacant:DecisionSummary')


if __name__ == '__main__':
    unittest.main()
