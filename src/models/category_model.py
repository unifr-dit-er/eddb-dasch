from helper import (
    body_create_category,
    body_update_label,
    body_update_simple_text,
)


class Category():

    def __init__(self, eddb_id, name_en, name_de, name_fr):
        '''Initialization of the fields.'''
        en = (name_en or '').strip()
        de = (name_de or '').strip()
        fr = (name_fr or '').strip()
        if len(en) == 0:
            raise ValueError('Category name_en is not set')
        if len(de) == 0:
            raise ValueError('Category name_de is not set')
        if len(fr) == 0:
            raise ValueError('Category name_fr is not set')
        self.eddb_id = eddb_id
        self.name_en = en
        self.name_de = de
        self.name_fr = fr

    def has_label_changed(self, label_old):
        return self.label() != label_old

    def label(self):
        return self.name_en

    def payload_add(self):
        eddb_id = self.eddb_id
        label = self.label()
        name_de = self.name_de
        name_fr = self.name_fr
        return body_create_category(eddb_id, label, name_de, name_fr)

    def payload_update_fields(self, dasch):
        payloads = []
        resource_id = dasch['@id']
        resource_type = self.resource_type()

        field = 'Datacant:hasNameDe'
        if dasch[field]['knora-api:valueAsString'] != self.name_de:
            field_id = dasch[field]['@id']
            value = self.name_de
            payload = body_update_simple_text(resource_id, resource_type, field, field_id, value)
            payloads.append(payload)

        field = 'Datacant:hasNameFr'
        if dasch[field]['knora-api:valueAsString'] != self.name_fr:
            field_id = dasch[field]['@id']
            value = self.name_fr
            payload = body_update_simple_text(resource_id, resource_type, field, field_id, value)
            payloads.append(payload)

        return payloads

    def payload_update_label(self, resource_id, last_modification):
        resource_t = self.resource_type()
        label = self.label()
        return body_update_label(resource_id, resource_t, label, last_modification)

    def resource_type(self):
        return 'Datacant:Category'
