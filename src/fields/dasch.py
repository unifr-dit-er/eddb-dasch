from abc import ABC, abstractmethod
import re


REGEX_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')


class DateValue(ABC):
    '''Abstract class which shapes the dates.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        if not REGEX_DATE.match(value):
            raise TypeError()
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, DateValue):
            return TypeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

    def is_updated(self, dasch_obj):
        value_old = dasch_obj[self.name]['knora-api:valueAsString']
        return self.value != value_old
        

    def to_knora(self):
        year = int(self.value[:4])
        month = int(self.value[5:7])
        day = int(self.value[8:])
        return {
            self.name: {
                '@type': 'knora-api:DateValue',
                'knora-api:dateValueHasStartYear': year,
                'knora-api:dateValueHasEndYear': year,
                'knora-api:dateValueHasStartMonth': month,
                'knora-api:dateValueHasEndMonth': month,
                'knora-api:dateValueHasStartDay': day,
                'knora-api:dateValueHasEndDay': day,
                'knora-api:dateValueHasStartEra': 'CE',
                'knora-api:dateValueHasEndEra': 'CE',
                'knora-api:dateValueHasCalendar': 'GREGORIAN'
            }
        }

    def to_knora_update(self, field_id):
        year = int(self.value[:4])
        month = int(self.value[5:7])
        day = int(self.value[8:])
        return {
            self.name: {
                '@id': field_id,
                '@type': 'knora-api:DateValue',
                'knora-api:dateValueHasStartYear': year,
                'knora-api:dateValueHasEndYear': year,
                'knora-api:dateValueHasStartMonth': month,
                'knora-api:dateValueHasEndMonth': month,
                'knora-api:dateValueHasStartDay': day,
                'knora-api:dateValueHasEndDay': day,
                'knora-api:dateValueHasStartEra': 'CE',
                'knora-api:dateValueHasEndEra': 'CE',
                'knora-api:dateValueHasCalendar': 'GREGORIAN'
            }
        }


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
            return TypeError()
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
    '''Abstract class which shapes a (single) link to another resource.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value
        self.value_iri = None

    def __eq__(self, other):
        if not isinstance(other, LinkValue):
            return TypeError()
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


class LinksValue(ABC):
    '''Abstract class which shapes multiple links to another resource.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value
        self.value_iri = None

    def __eq__(self, other):
        if not isinstance(other, LinkValue):
            return TypeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

    def is_updated(self, dasch_obj):
        raise NotImplementedError()

    def set_value_iri(self, value_iri):
        self.value_iri = value_iri

    def to_knora(self):
        keywords_iri = []
        for keyword_iri in self.value_iri:
            chunk = {
                '@type': 'knora-api:LinkValue',
                'knora-api:linkValueHasTargetIri': {
                    '@id': keyword_iri
                }
            }
            keywords_iri.append(chunk)
        return {self.name: keywords_iri}

    def to_knora_update(self, field_id):
        raise NotImplementedError()


class ListValue(ABC):
    '''Abstract class which shapes an enumeration of a controlled vocabulary.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value
        self.value_iri = None

    def __eq__(self, other):
        if not isinstance(other, ListValue):
            return TypeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

    def is_updated(self, dasch_obj):
        value_old = dasch_obj[self.name]['knora-api:listValueAsListNode']['@id']
        return self.value_iri != value_old

    def set_value_iri(self, value_iri):
        self.value_iri = value_iri

    def to_knora(self):
        if self.value_iri is None:
            raise RuntimeError('Method cannot be called when `iri` is not set')
        return {
            self.name: {
                '@type': 'knora-api:ListValue',
                'knora-api:listValueAsListNode': {
                    '@id': self.value_iri,
                },
            }
        }

    def to_knora_update(self, field_id):
        if self.value_iri is None:
            raise RuntimeError('Method cannot be called when `iri` is not set')
        return {
            self.name: {
                '@id': field_id,
                '@type': 'knora-api:ListValue',
                'knora-api:listValueAsListNode': {
                    '@id': self.value_iri
                }
            }
        }


class RichTextValue(ABC):
    '''Abstract class which shapes the strings with html tags.
    '''

    def __init__(self, name, value, updated_at):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value
        self.updated_at = updated_at

    def __eq__(self, other):
        if not isinstance(other, RichTextValue):
            return TypeError()
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def is_constant(self):
        pass

    def is_updated(self, dasch_obj):
        # Note: we cannot compare the new with old value because DaSCH
        # transforms the input. Therefore, we assume a change based on a date.
        dasch_date = dasch_obj[self.name]['knora-api:valueCreationDate']['@value']
        return dasch_date < self.updated_at

    def to_knora(self):
        return {
            self.name: {
                '@type': 'knora-api:TextValue',
                'knora-api:textValueAsXml': self.value,  # TODO: check if processing is required.
                'knora-api:textValueHasMapping': {
                    '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping'
                }
            }
        }

    def to_knora_update(self, field_id):
        raise NotImplementedError()


class SimpleTextValue(ABC):
    '''Abstract class which shapes the strings.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, SimpleTextValue):
            return TypeError()
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
