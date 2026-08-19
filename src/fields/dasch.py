from abc import ABC, abstractmethod


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
        if not isinstance(other, IntValue):
            return RuntimeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

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

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value
        self.value_iri = None

    def __eq__(self, other):
        if not isinstance(other, LinkValue):
            return RuntimeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

    def is_updated(self, dasch_obj):
        link_target = dasch_obj[self.name].get('knora-api:linkValueHasTarget')
        if link_target is None:
            link_target = dasch_obj[self.name]['knora-api:linkValueHasTargetIri']
        value_old = link_target['@id']
        return self.value_iri != value_old

    def set_value_iri(self, value_iri):
        self.value_iri = value_iri

    def to_knora(self):
        if self.value_iri is None:
            raise RuntimeError('Method cannot be called when `iri` is not set')
        return {
            self.name: {
                '@type': 'knora-api:LinkValue',
                'knora-api:linkValueHasTargetIri': {
                    '@id': self.value_iri
                }
            }
        }

    def to_knora_update(self, field_id):
        if self.value_iri is None:
            raise RuntimeError('Method cannot be called when `iri` is not set')
        return {
            self.name: {
                '@id': field_id,
                '@type': 'knora-api:LinkValue',
                'knora-api:linkValueHasTargetIri': {
                    '@id': self.value_iri
                }
            }
        }


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
        if not isinstance(other, SimpleTextValue):
            return RuntimeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

    def is_updated(self, dasch_obj):
        value_old = dasch_obj[self.name]['knora-api:valueAsString']
        return self.value != value_old

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
