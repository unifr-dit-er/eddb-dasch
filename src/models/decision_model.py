from fields.datacant import (
    Abstract,
    Canton,
    DateGreg,
    Description,
    DocumentFile,
    EddbId,
    FileName,
    KeywordLink,
)
from models.resource import Resource


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
        keywords_id,
        dasch_filename_tmp=None
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
        self.dasch_filename_tmp = DocumentFile(dasch_filename_tmp)

    def eddb_filename(self):
        return self.url_file.split('/')[-1]

    def eddb_url_file(self):
        return self.url_file

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
            self.dasch_filename_tmp,
        ]

    def filename(self):
        return '{}_{}.pdf'.format(self.canton.value, self.date_issued.value)

    def fill_iri_values(self, dasch_db):
        canton_iri = dasch_db['cantons'][self.canton.value]
        self.canton.set_value_iri(canton_iri)

        tmp = [dasch_db['keyword'][k_id]['@id'] for k_id in self.keywords_id.value]
        self.keywords_id.set_value_iri(tmp)

    def has_file_field(self):
        return True

    def has_label_changed(self, label_old):
        return self.label() != label_old

    @staticmethod
    def key_in_dasch_db():
        return 'decision'

    def label(self):
        return '{} {}'.format(self.canton.value, self.date_issued.value)

    @staticmethod
    def resource_type():
        return 'Datacant:Decisions'

    def set_dasch_filename_tmp(self, filename):
        self.dasch_filename_tmp = DocumentFile(filename)

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
