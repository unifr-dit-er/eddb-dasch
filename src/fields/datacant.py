from fields.dasch import (
    DateValue,
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

    def is_constant(self):
        return False


class Canton(ListValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:hasCantonList'
        LinkValue.__init__(self, name, value)

    def is_constant(self):
        return False


class CategoryLink(LinkValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:linkToCategoryValue'
        LinkValue.__init__(self, name, value)

    def is_constant(self):
        return False


class DateGreg(DateValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:hasDateIssued'
        DateValue.__init__(self, name, value)

    def is_constant(self):
        return False


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

    def is_constant(self):
        return False


class EddbId(IntValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        if value <= 0:
            raise ValueError('EDDB id must be greater than 0')
        name = f'{PROJECT_NAME}:hasId'
        IntValue.__init__(self, name, value)

    def is_constant(self):
        return True

class FileName(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Filename must be set')
        name = f'{PROJECT_NAME}:hasFileName'
        SimpleTextValue.__init__(self, name, v)

    def is_constant(self):
        return False


class KeywordLink(LinksValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:linkToKeywordValue'
        LinksValue.__init__(self, name, value)

    def is_constant(self):
        return False


class NameDe(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Name in German must be set')
        name = f'{PROJECT_NAME}:hasNameDe'
        SimpleTextValue.__init__(self, name, v)

    def is_constant(self):
        return False


class NameFr(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Name in French must be set')
        name = f'{PROJECT_NAME}:hasNameFr'
        SimpleTextValue.__init__(self, name, v)

    def is_constant(self):
        return False
