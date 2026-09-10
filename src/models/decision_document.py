from fields.datacant import (
    Attachment,
    Checksum,
    EddbId,
    FileName,
)
from models.resource import Resource


class DecisionDocument(Resource):

    def __init__(
        self,
        eddb_id,
        updated_at,
        date_issued,
        canton,
        eddb_url,
        checksum,
        filename_dasch,
    ):
        '''Initialization of the fields.'''
        self.eddb_id = EddbId(eddb_id)
        self.updated_at = updated_at
        self.date_issued = date_issued
        self.canton = canton
        self.attachment = Attachment(eddb_url, filename_dasch, checksum, updated_at)

    def eddb_filename(self):
        return self.attachment.eddb_url.split('/')[-1]

    def eddb_url_file(self):
        return self.attachment.eddb_url

    def fields(self):
        return [
            self.eddb_id,
            FileName(self.filename()),
            self.attachment,
            Checksum(self.attachment.checksum),
        ]

    def filename(self):
        return '{}_{}.pdf'.format(self.canton, self.date_issued)

    def fill_iri_values(self, dasch_db):
        pass

    def has_attachment_field(self):
        return True

    def label(self):
        return '{} {}'.format(self.canton, self.date_issued)

    @staticmethod
    def resource_type():
        return 'Datacant:DecisionDocument'

    def to_dict(self):
        return {
            'eddb_id': self.eddb_id.value,
            'updated_at': self.updated_at,
            'date_issued': self.date_issued,
            'canton': self.canton,
            'eddb_url': self.attachment.eddb_url,
            'filename_dasch': self.attachment.filename_dasch,
            'checksum': self.attachment.checksum,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
