from abc import ABC, abstractmethod
import payload
from fields.dasch import RichTextValue
from helper import transform_to_rich


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
    def label():
        pass

    def payload_create(self):
        resource_type = self.resource_type()
        label = self.label()
        payload_chunks = [field.to_knora() for field in self.fields()]
        return payload.create(resource_type, label, payload_chunks)

    def payload_update_fields(self, dasch_db):
        payloads = {'updates': [], 'add_values': [], 'del_values': []}
        resource_type = self.resource_type()
        eddb_id = self.eddb_id.value
        dasch_obj = dasch_db[resource_type].get(eddb_id)
        if dasch_obj is None:
            raise RuntimeError(f'Updated resource (id={eddb_id}) not found')
        resource_id = dasch_obj['@id']

        for field in self.fields():
            f_payloads = field.to_knora_update(dasch_obj)
            if isinstance(field, RichTextValue):
                # `Method is_updated` does a parital comparison for `RichText` type.
                if field.is_updated(dasch_obj):
                    dasch_xml = dasch_obj[field.name]['knora-api:textValueAsXml']
                    response = transform_to_rich(field.value, dasch_db['token'])
                    if dasch_xml == response.text:
                        continue
            for key in ['updates', 'add_values', 'del_values']:
                for key_value in f_payloads[key]:
                    p = payload.update(resource_id, resource_type, key_value)
                    payloads[key].append(p)
        return payloads

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
