import unittest
import json
from pathlib import Path
from fields.datacant import Attachment, EddbId
from models.decision_document import DecisionDocument


class TestDecisionDocument(unittest.TestCase):
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
            'eddb_url': 'http://www.u.ch/download/2005.06.28-5__vzhl.pdf',
            'filename_dasch': '3HIj4A8lXjQ-vxGzbejbhxO.pdf',
            'checksum': 'ba7816bf8',
        }

    def test_constructor(self):
        doc = DecisionDocument(**self.attributes)
        self.assertEqual(doc.eddb_id, EddbId(257))
        self.assertEqual(doc.date_issued, '2021-08-12')
        self.assertEqual(doc.updated_at, '2026-02-20 13:37:26+00:00')
        self.assertEqual(doc.canton, 'FR')
        self.assertEqual(
            doc.attachment.eddb_url,
            'http://www.u.ch/download/2005.06.28-5__vzhl.pdf')
        self.assertEqual(doc.attachment.filename_dasch, '3HIj4A8lXjQ-vxGzbejbhxO.pdf')
        self.assertEqual(doc.attachment.checksum, 'ba7816bf8')

    def test_constructor_fail(self):
        pass

    def test_eddb_filename(self):
        decision = DecisionDocument(**self.attributes)
        self.assertEqual(decision.eddb_filename(), '2005.06.28-5__vzhl.pdf')

    def test_eddb_url_file(self):
        decision = DecisionDocument(**self.attributes)
        url_file = 'http://www.u.ch/download/2005.06.28-5__vzhl.pdf'
        self.assertEqual(decision.attachment.eddb_url, url_file)

    def test_fill_iri_values(self):
        decision = DecisionDocument(**self.attributes)
        decision.fill_iri_values(self.dasch_db)

    def test_from_and_to_json(self):
        decision_original = DecisionDocument(**self.attributes)
        json_str = json.dumps(decision_original.to_dict())
        json_data = json.loads(json_str)
        decision = DecisionDocument(**json_data)
        self.assertEqual(decision.eddb_id, EddbId(257))
        self.assertEqual(decision.date_issued, '2021-08-12')
        self.assertEqual(decision.updated_at, '2026-02-20 13:37:26+00:00')
        self.assertEqual(decision.canton, 'FR')
        self.assertEqual(decision.attachment, Attachment(
            'http://www.u.ch/download/2005.06.28-5__vzhl.pdf',
            '3HIj4A8lXjQ-vxGzbejbhxO.pdf',
            'ba7816bf8',
        ))
        # self.assertTrue(decision.attachment.eddb_url.startswith('http'))
        # self.assertTrue(decision.attachment.filename_dasch.endswith('2005.06.28-5__vzhl.pdf'))

    def test_filename(self):
        decision = DecisionDocument(**self.attributes)
        self.assertEqual(decision.filename(), 'FR_2021-08-12.pdf')

    def test_has_file_field(self):
        decision = DecisionDocument(**self.attributes)
        self.assertTrue(decision.has_attachment_field())

    def test_label(self):
        decision = DecisionDocument(**self.attributes)
        self.assertEqual(decision.label(), 'FR 2021-08-12')

    def test_payload_create(self):
        decision = DecisionDocument(**self.attributes)
        decision.fill_iri_values(self.dasch_db)
        payload = decision.payload_create()
        self.assertEqual(payload['@type'], decision.resource_type())
        self.assertEqual(payload['rdfs:label'], decision.label())

        eddb_id = payload['Datacant:hasId']['knora-api:intValueAsInt']
        self.assertEqual(eddb_id, decision.eddb_id.value)

        filename = payload['Datacant:hasFileName']['knora-api:valueAsString']
        self.assertEqual(filename, decision.filename())

        # TODO: add checksum bloc

        filename_dasch_tmp = payload \
            .get('knora-api:hasDocumentFileValue') \
            .get('knora-api:fileValueHasFilename')
        self.assertEqual(filename_dasch_tmp, decision.attachment.filename_dasch)

    def test_payload_update_fields(self):
        pass

    def test_payload_update_label(self):
        pass

    def test_set_filename_dasch(self):
        decision = DecisionDocument(**self.attributes)
        eddb_url = 'https://...'
        filename_dasch = '4rMCDmxpYAx-DiRuvu3v2rQ.pdf'
        checksum = 'ba7816bf8'
        decision.set_attachment(eddb_url, filename_dasch, checksum)
        self.assertEqual(decision.attachment.eddb_url, eddb_url)
        self.assertEqual(decision.attachment.filename_dasch, filename_dasch)
        self.assertEqual(decision.attachment.checksum, checksum)

    def test_resource_type(self):
        decision = DecisionDocument(**self.attributes)
        self.assertEqual(decision.resource_type(), 'Datacant:DecisionDocument')


if __name__ == '__main__':
    unittest.main()
