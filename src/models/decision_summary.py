from fields.datacant import (
    Abstract,
    Canton,
    DateGreg,
    Description,
    DecisionDocumentLink,
    EddbId,
    KeywordLink,
)
from models.resource import Resource


class DecisionSummary(Resource):

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
        keywords_id,
        decision_document,
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
        self.keywords_id = KeywordLink(keywords_id)
        self.decision_document = DecisionDocumentLink(decision_document)

    def fields(self):
        return [
            self.eddb_id,
            self.date_issued,
            self.canton,
            self.desc_de,
            self.desc_fr,
            self.abstract_de,
            self.abstract_fr,
            self.keywords_id,
            self.decision_document,
        ]

    def fill_iri_values(self, dasch_db):
        canton_iri = dasch_db['cantons'][self.canton.value]
        self.canton.set_value_iri(canton_iri)

        tmp = [dasch_db['keyword'][k_id]['@id'] for k_id in self.keywords_id.value]
        self.keywords_id.set_value_iri(tmp)

        # TODO: add decision_document here.

    def has_attachment_field(self):
        return False

    @staticmethod
    def key_in_dasch_db():
        return 'Datacant:DecisionSummary'

    def label(self):
        return '{} {}'.format(self.canton.value, self.date_issued.value)

    @staticmethod
    def resource_type():
        return 'Datacant:DecisionSummary'

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
            'keywords_id': self.keywords_id.value,
            'decision_document': self.decision_document.value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
