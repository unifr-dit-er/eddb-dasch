from models.resource import Resource
from fields.datacant import CategoryLink, EddbId, NameDe, NameFr


class Keyword(Resource):

    def __init__(self, eddb_id, category_id, name_en, name_de, name_fr):
        '''Initialization of the fields.'''
        en = (name_en or '').strip()
        if len(en) == 0:
            raise ValueError('Category name_en is not set')
        self.eddb_id = EddbId(eddb_id)
        self.category_id = CategoryLink(category_id)
        self.name_en = en
        self.name_de = NameDe(name_de)
        self.name_fr = NameFr(name_fr)

    def eddb_filename(self):
        raise RuntimeError()

    def eddb_url_file(self):
        raise RuntimeError()

    def fill_iri_values(self, dasch_db):
        category = self.category_id
        value_iri = dasch_db['category'][category.value]['@id']
        category.set_value_iri(value_iri)

    def fields(self):
        return [
            self.eddb_id,
            self.category_id,
            self.name_de,
            self.name_fr,
        ]

    def has_attachment_field(self):
        return False

    @staticmethod
    def key_in_dasch_db():
        return 'keyword'

    def label(self):
        return self.name_en

    def set_attachment(self, eddb_url, filename_dasch, sha):
        raise RuntimeError()

    @staticmethod
    def resource_type():
        return 'Datacant:Keyword'

    def to_dict(self):
        return {
            'eddb_id': self.eddb_id.value,
            'category_id': self.category_id.value,
            'name_en': self.name_en,
            'name_de': self.name_de.value,
            'name_fr': self.name_fr.value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
