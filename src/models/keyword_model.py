from payload import (
    body_create_keyword,
    body_update_label,
    body_update_link,
    body_update_simple_text,
)


class Keyword():

    def __init__(self, eddb_id, category_id, name_en, name_de, name_fr):
        '''Initialization of the fields.'''
        en = (name_en or '').strip()
        de = (name_de or '').strip()
        fr = (name_fr or '').strip()
        if len(en) == 0:
            raise ValueError('Keyword name_en is not set')
        if len(de) == 0:
            raise ValueError('Keyword name_de is not set')
        if len(fr) == 0:
            raise ValueError('Keyword name_fr is not set')
        self.eddb_id = eddb_id
        self.category_id = category_id
        self.name_en = en
        self.name_de = de
        self.name_fr = fr

    def has_label_changed(self, label_old):
        return self.label() != label_old

    def label(self):
        return self.name_en

    def payload_add(self, category_iri):
        eddb_id = self.eddb_id
        label = self.label()
        name_de = self.name_de
        name_fr = self.name_fr
        return body_create_keyword(eddb_id, label, name_de, name_fr, category_iri)

    def payload_update_fields(self, dasch_db):
        eddb_id = str(self.eddb_id)
        payloads = []
        keyword_dasch = dasch_db['keyword'][eddb_id]
        resource_id = keyword_dasch['@id']
        resource_type = self.resource_type()

        field = 'Datacant:hasNameDe'
        if keyword_dasch[field]['knora-api:valueAsString'] != self.name_de:
            field_id = keyword_dasch[field]['@id']
            value = self.name_de
            payload = body_update_simple_text(resource_id, resource_type, field, field_id, value)
            payloads.append(payload)

        field = 'Datacant:hasNameFr'
        if keyword_dasch[field]['knora-api:valueAsString'] != self.name_fr:
            field_id = keyword_dasch[field]['@id']
            value = self.name_fr
            payload = body_update_simple_text(resource_id, resource_type, field, field_id, value)
            payloads.append(payload)

        iri_current = keyword_dasch['Datacant:linkToCategoryValue']['knora-api:linkValueHasTarget']['@id']
        category_id_new = str(self.category_id)
        iri_new = dasch_db['category'][category_id_new]['@id']
        if iri_current != iri_new:
            field = 'Datacant:linkToCategoryValue'
            field_id = keyword_dasch['Datacant:linkToCategoryValue']['@id']
            payload = body_update_link(resource_id, resource_type, field, field_id, iri_new)
            payloads.append(payload)

        return payloads

    def payload_update_label(self, resource_id, last_modification):
        resource_t = self.resource_type()
        label = self.label()
        return body_update_label(resource_id, resource_t, label, last_modification)

    def resource_type(self):
        return 'Datacant:Keyword'
