from fields.datacant import (
    Abstract,
    Canton,
    DateGreg,
    Description,
    EddbId,
    FileName,
    KeywordLink,
)
from helper import get_keyword_iri, is_before
from models.resource import Resource
from payload import (
    body_add_link,
    body_create_decision,
    body_unlink_keyword,
    body_update_date,
    body_update_list,
    body_update_rich_text,
    body_update_simple_text,
)


class Decision(Resource):

    def __init__(
        self,
        eddb_id,
        updated_at,
        date_issued,
        canton,
        desc_de,
        desc_fr,
        abstract_de,
        abstract_fr,
        url_file,
        keywords_id
    ):
        '''Initialization of the fields.'''
        if len(keywords_id) == 0:
            raise ValueError('No keyword associated to decision')
        self.eddb_id = EddbId(eddb_id)
        self.updated_at = updated_at
        self.date_issued = DateGreg(date_issued)
        self.canton = Canton(canton)
        self.desc_de = Description(desc_de, 'de')
        self.desc_fr = Description(desc_fr, 'fr')
        self.abstract_de = Abstract(abstract_de, 'de', updated_at)
        self.abstract_fr = Abstract(abstract_fr, 'fr', updated_at)
        self.url_file = url_file
        self.keywords_id = KeywordLink(keywords_id)

    def fields(self):
        return [
            self.eddb_id,
            self.date_issued,
            self.canton,
            FileName(self.filename()),
            self.desc_de,
            self.desc_fr,
            self.abstract_de,
            self.abstract_fr,
            self.keywords_id,
        ]

    def filename(self):
        return '{}_{}.pdf'.format(self.canton.value, self.date_issued.value)

    def filename_eddb(self):
        return self.url_file.split('/')[-1]

    def fill_iri_values(self, dasch_db):
        canton_iri = dasch_db['cantons'][self.canton.value]
        self.canton.set_value_iri(canton_iri)

        tmp = [dasch_db['keyword'][k_id]['@id'] for k_id in self.keywords_id.value]
        self.keywords_id.set_value_iri(tmp)

    def has_label_changed(self, label_old):
        return self.label() != label_old

    @staticmethod
    def key_in_dasch_db():
        return 'decision'

    def label(self):
        return '{} {}'.format(self.canton.value, self.date_issued.value)

    # def payload_add(self, filename_tmp, dasch_db):
    #     eddb_id = self.eddb_id
    #     label = self.label()
    #     filename = self.filename()
    #     canton_iri = dasch_db['cantons'][self.canton]
    #     keywords_iri = []
    #     for keyword_eddb_id in self.keywords_id:
    #         iri = get_keyword_iri(dasch_db, keyword_eddb_id)
    #         keywords_iri.append(iri)
    #     return body_create_decision(
    #         eddb_id, label, self.date_issued, filename, filename_tmp, canton_iri,
    #         self.desc_de, self.desc_fr,
    #         self.abstract_de, self.abstract_fr, keywords_iri
    #     )

    # def payload_update_fields(self, dasch_db):
    #     payloads = []
    #     decision_dasch = dasch_db['decision'][self.eddb_id.value]
    #     resource_id = decision_dasch['@id']
    #     resource_type = self.resource_type()

    #     # canton
    #     canton_iri_old = decision_dasch['Datacant:hasCantonList']['knora-api:listValueAsListNode']['@id']
    #     canton_iri_new = dasch_db['cantons'][self.canton.value]
    #     if canton_iri_old != canton_iri_new:
    #         field = 'Datacant:hasCantonList'
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_list(resource_id, field_id, canton_iri_new)
    #         payloads.append(payload)

    #     # date issued
    #     date_dasch = decision_dasch['Datacant:hasDateIssued']['knora-api:valueAsString']
    #     if self.date_issued.value not in date_dasch:
    #         field = 'Datacant:hasDateIssued'
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_date(resource_id, resource_type, field, field_id, self.date_issued.value)
    #         payloads.append(payload)

    #     # filename
    #     field = 'Datacant:hasFileName'
    #     filename_dasch = decision_dasch[field]['knora-api:valueAsString']
    #     filename_new = self.filename()
    #     if filename_dasch != filename_new:
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_simple_text(resource_id, resource_type, field, field_id, filename_new)
    #         payloads.append(payload)

    #     # description (de + fr)
    #     field = 'Datacant:hasDescriptionDe'
    #     description_de_dasch = decision_dasch[field]['knora-api:valueAsString']
    #     description_de_new = self.desc_de
    #     if description_de_dasch != description_de_new:
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_simple_text(resource_id, resource_type, field, field_id, description_de_new)
    #         payloads.append(payload)
    #     field = 'Datacant:hasDescriptionFr'
    #     description_fr_dasch = decision_dasch[field]['knora-api:valueAsString']
    #     description_fr_new = self.desc_fr
    #     if description_fr_dasch != description_fr_new:
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_simple_text(resource_id, resource_type, field, field_id, description_fr_new)
    #         payloads.append(payload)

    #     # abstract (de + fr)
    #     field = 'Datacant:hasAbstractDe'
    #     date_dasch = decision_dasch[field]['knora-api:valueCreationDate']['@value']
    #     # abstract_de_dasch = decision_dasch[field]['knora-api:textValueAsXml']
    #     abstract_de_new = '<?xml version="1.0" encoding="UTF-8"?>\n' + f'<text>{self.abstract_de}</text>'
    #     if is_before(date_dasch, self.updated_at):
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_rich_text(resource_id, resource_type, field, field_id, abstract_de_new)
    #         payloads.append(payload)

    #     field = 'Datacant:hasAbstractFr'
    #     date_dasch = decision_dasch[field]['knora-api:valueCreationDate']['@value']
    #     # abstract_fr_dasch = decision_dasch[field]['knora-api:textValueAsXml']
    #     abstract_fr_new = '<?xml version="1.0" encoding="UTF-8"?>\n' + f'<text>{self.abstract_fr}</text>'
    #     if is_before(date_dasch, self.updated_at):
    #         field_id = decision_dasch[field]['@id']
    #         payload = body_update_rich_text(resource_id, resource_type, field, field_id, abstract_fr_new)
    #         payloads.append(payload)

    #     # keywords
    #     payloads_add = []
    #     payloads_del = []
    #     field = 'Datacant:linkToKeywordValue'
    #     links = decision_dasch[field]
    #     is_list = isinstance(links, list)
    #     if not is_list:
    #         # When only a single keyword
    #         links = [links]
    #     keywords_iri_new = set(self.keywords_id.value_iri)
    #     #for eddb_id in self.keywords_id:
    #     #    iri = get_keyword_iri(dasch_db, eddb_id)
    #     #    keywords_iri_new.add(iri)
    #     keywords_iri_old = set()
    #     for link in links:
    #         iri = link['knora-api:linkValueHasTarget']['@id']
    #         keywords_iri_old.add(iri)
    #     keyword_iri_to_remove = list(keywords_iri_old - keywords_iri_new)
    #     keyword_iri_to_add = list(keywords_iri_new - keywords_iri_old)

    #     for keyword_iri in keyword_iri_to_add:
    #         field = "Datacant:linkToKeywordValue"
    #         payload = body_add_link(resource_id, resource_type, field, keyword_iri)
    #         payloads_add.append(payload)

    #     for link in links:
    #         link_iri = link['@id']
    #         keyword_iri = link['knora-api:linkValueHasTarget']['@id']
    #         if keyword_iri in keyword_iri_to_remove:
    #             payload = body_unlink_keyword(resource_id, link_iri, keyword_iri)
    #             payloads_del.append(payload)

    #     return payloads, payloads_add, payloads_del

    @staticmethod
    def resource_type():
        return 'Datacant:Decisions'

    def to_dict(self):
        return {
            'eddb_id': self.eddb_id.value,
            'updated_at': self.updated_at,
            'date_issued': self.date_issued.value,
            'canton': self.canton.value,
            'desc_de': self.desc_de.value,
            'desc_fr': self.desc_fr.value,
            'abstract_de': self.abstract_de.value,
            'abstract_fr': self.abstract_fr.value,
            'url_file': self.url_file,
            'keywords_id': self.keywords_id.value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
