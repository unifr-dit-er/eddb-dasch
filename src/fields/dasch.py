from abc import ABC


class DateValue(ABC):
    '''Abstract class which shapes the dates.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value


class IntValue(ABC):
    '''Abstract class which shapes the integers.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        if not isinstance(value, int):
            raise TypeError()
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, DateValue):
            return NotImplementedError()
        return self.name == other.name and self.value == other.value

    def to_knora(self):
        return {
            self.name: {
                '@type': 'knora-api:IntValue',
                'knora-api:intValueAsInt': self.value,
            }
        }


class LinkValue(ABC):
    '''Abstract class which shapes a link to another resource.
    '''

    def __init__(self, name, iri_value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.iri_value = iri_value


class ListValue(ABC):
    '''Abstract class which shapes an enumeration of a controlled vocabulary.
    '''

    def __init__(self, name, iri_value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.iri_value = iri_value


class RichTextValue(ABC):
    '''Abstract class which shapes the strings with html tags.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value


class SimpleTextValue(ABC):
    '''Abstract class which shapes the strings.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, DateValue):
            return NotImplementedError()
        return self.name == other.name and self.value == other.value

    def knora_value(self, dasch_obj):
        field_key = self.name
        return dasch_obj[field_key]['knora-api:valueAsString']

    def to_knora(self):
        return {
            self.name: {
                '@type': 'knora-api:TextValue',
                'knora-api:valueAsString': self.value,
            }
        }

    def to_knora_update(self, field_id):
        return {
            self.name: {
                '@id': field_id,
                '@type': 'knora-api:TextValue',
                'knora-api:valueAsString': self.value,
            }
        }
