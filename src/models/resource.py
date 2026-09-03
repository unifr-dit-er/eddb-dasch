from abc import ABC, abstractmethod
import payload
from fields.dasch import LinkValue, LinksValue


class Resource(ABC):
    '''Abstract class which shapes the resources.
    '''

    def __init__(self):
        pass

    @abstractmethod
    def fill_iri_values(self, dasch_db):
        pass

    @abstractmethod
    def fields(self):
        pass

    @abstractmethod
    def has_attachment_field(self):
        pass

    def has_label_changed(self, label_old):
        return self.label() != label_old

    @abstractmethod
    def key_in_dasch_db():
        pass

    @abstractmethod
    def label():
        pass

    def payload_create(self):
        resource_type = self.resource_type()
        label = self.label()
        payload_chunks = [field.to_knora() for field in self.fields()]
        return payload.create(resource_type, label, payload_chunks)

    def payload_update_fields(self, dasch_db):
        payloads = []
        payloads_add_links = []
        payloads_del_links = []
        key_in_dasch_db = self.key_in_dasch_db()
        eddb_id = self.eddb_id.value
        dasch_obj = dasch_db[key_in_dasch_db].get(eddb_id)
        if dasch_obj is None:
            raise RuntimeError(f'Updated resource (id={eddb_id}) not found')
        resource_id = dasch_obj['@id']
        resource_type = self.resource_type()

        for field in self.fields():
            if field.is_constant():
                continue
            if field.is_updated(dasch_obj):
                if isinstance(field, LinksValue):
                    add_links, del_links = field.to_knora_update(dasch_obj)
                    for link in add_links:
                        p = payload.add_link(resource_id, resource_type, link)
                        payloads_add_links.append(p)
                    for link in del_links:
                        p = payload.del_link(resource_id, resource_type, link)
                        payloads_del_links.append(p)
                elif isinstance(field, LinkValue):
                    field_key = field.name
                    field_id = dasch_obj[field_key]['@id']
                    key_value = field.to_knora_update(field_id)
                    p = payload.add_link(resource_id, resource_type, key_value)
                    payloads.append(p)
                else:
                    field_key = field.name
                    field_id = dasch_obj[field_key]['@id']
                    key_value = field.to_knora_update(field_id)
                    p = payload.update(resource_id, resource_type, key_value)
                    payloads.append(p)

        return payloads, payloads_add_links, payloads_del_links

    def payload_update_label(self, dasch_obj):
        label_old = dasch_obj['rdfs:label']
        label = self.label()
        if label == label_old:
            return None
        resource_id = dasch_obj['@id']
        last_modif = dasch_obj.get('knora-api:lastModificationDate', {}).get('@value')
        resource_type = self.resource_type()
        return payload.update_label(resource_id, resource_type, label, last_modif)

    @abstractmethod
    def resource_type():
        pass
