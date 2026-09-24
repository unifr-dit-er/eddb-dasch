from fields.dasch import (
    DateValue,
    DocumentFileValue,
    IntValue,
    LinkValue,
    LinksValue,
    ListValue,
    RichTextValue,
    SimpleTextValue,
)


PROJECT_NAME = 'Datacant'


class Abstract(RichTextValue):

    def __init__(self, value, language, updated_at):
        '''Initialization of the fields.'''
        if language not in ['de', 'fr']:
            raise ValueError('Invalid language')
        name = f'{PROJECT_NAME}:hasAbstract{language.title()}'
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Abstract must be set')
        RichTextValue.__init__(self, name, v, updated_at)


class Attachment(DocumentFileValue):

    def __init__(self, eddb_url, updated_at):
        '''Initialization of the fields.'''
        self.eddb_url = eddb_url
        name = 'knora-api:hasDocumentFileValue'
        value = None
        lic = 'http://rdfh.ch/licenses/public-domain'
        cpyright = 'Public Domain - Not Protected by Copyright'
        authors = ['Swiss court']
        DocumentFileValue.__init__(self, name, value, updated_at, lic, cpyright, authors)


class Canton(ListValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:hasCantonList'
        ListValue.__init__(self, name, value)


class CategoryLink(LinkValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:linkToCategoryValue'
        LinkValue.__init__(self, name, value)


# TODO: Delete this class.
class Checksum(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:hasChecksum'
        v = (value or '').strip()
        SimpleTextValue.__init__(self, name, v)

    def is_updated(self, obj):
        return False


class DateGreg(DateValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:hasDateIssued'
        DateValue.__init__(self, name, value)


class DecisionDocumentLink(LinkValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:linkToDocumentValue'
        LinkValue.__init__(self, name, value)


class Description(SimpleTextValue):

    def __init__(self, value, language):
        '''Initialization of the fields.'''
        if language not in ['de', 'fr']:
            raise ValueError('Invalid language')
        name = f'{PROJECT_NAME}:hasDescription{language.title()}'
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Description must be set')
        SimpleTextValue.__init__(self, name, v)


class EddbId(IntValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        if value <= 0:
            raise ValueError('EDDB id must be greater than 0')
        name = f'{PROJECT_NAME}:hasId'
        IntValue.__init__(self, name, value)


class FileName(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Filename must be set')
        name = f'{PROJECT_NAME}:hasFileName'
        SimpleTextValue.__init__(self, name, v)


class KeywordLink(LinksValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:linkToKeywordValue'
        LinksValue.__init__(self, name, value)


class Name(SimpleTextValue):

    def __init__(self, value, language):
        '''Initialization of the fields.'''
        if language not in ['de', 'fr']:
            raise ValueError('Invalid language')
        name = f'{PROJECT_NAME}:hasName{language.title()}'
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Name must be set')
        SimpleTextValue.__init__(self, name, v)
