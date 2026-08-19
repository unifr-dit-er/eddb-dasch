from models.resource import Resource
from fields.datacant import EddbId, NameDe, NameFr


class Category(Resource):

    def __init__(self, eddb_id, name_en, name_de, name_fr):
        '''Initialization of the fields.'''
        en = (name_en or '').strip()
        if len(en) == 0:
            raise ValueError('Category name_en is not set')
        self.eddb_id = EddbId(eddb_id)
        self.name_en = en
        self.name_de = NameDe(name_de)
        self.name_fr = NameFr(name_fr)

    def fill_iri_values(self, dasch_db):
        pass

    def fields(self):
        return [
            self.eddb_id,
            self.name_de,
            self.name_fr,
        ]

    @staticmethod
    def key_in_dasch_db():
        return 'category'

    def label(self):
        return self.name_en

    @staticmethod
    def resource_type():
        return 'Datacant:Category'

    def to_dict(self):
        return {
            'eddb_id': self.eddb_id.value,
            'name_en': self.name_en,
            'name_de': self.name_de.value,
            'name_fr': self.name_fr.value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
