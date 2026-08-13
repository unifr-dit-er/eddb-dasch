from fields.dasch import (
    DateValue,
    IntValue,
    LinkValue,
    ListValue,
    RichTextValue,
    SimpleTextValue,
)


PROJECT_NAME = 'Datacant'


class CategoryLink(LinkValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        name = f'{PROJECT_NAME}:linkToCategoryValue'
        LinkValue.__init__(self, name, value)


class EddbId(IntValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        if value <= 0:
            raise ValueError('EDDB id must be greater than 0')
        name = f'{PROJECT_NAME}:hasId'
        IntValue.__init__(self, name, value)


class NameDe(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Name in German must be set')
        name = f'{PROJECT_NAME}:hasNameDe'
        SimpleTextValue.__init__(self, name, v)


class NameFr(SimpleTextValue):

    def __init__(self, value):
        '''Initialization of the fields.'''
        v = (value or '').strip()
        if len(v) == 0:
            raise ValueError('Name in French must be set')
        name = f'{PROJECT_NAME}:hasNameFr'
        SimpleTextValue.__init__(self, name, v)
