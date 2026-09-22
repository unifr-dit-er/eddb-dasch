from abc import ABC, abstractmethod
import re


REGEX_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')


class DaschValue(ABC):
    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def is_updated(self, dasch_obj):
        pass

    @abstractmethod
    def payload_value_add(self, dasch_obj):
        pass

    @abstractmethod
    def payload_value_del(self, dasch_obj):
        pass

    @abstractmethod
    def payload_value_update(self, dasch_obj):
        pass

    def to_knora_update(self, dasch_obj):
        payloads = {'updates': [], 'add_values': [], 'del_values': []}
        if not self.is_updated(dasch_obj):
            return payloads

        is_previous_null = dasch_obj.get(self.name) is None
        is_new_null = self.value is None
        if is_new_null:
            if is_previous_null:
                raise RuntimeError('Method cannot be called when value is still null.')
            # Value must be deleted. (Note: empty array is empty and not null)
            key_value = self.payload_value_del(dasch_obj)
            payloads['del_values'].append(key_value)
            return payloads

        if isinstance(self, LinksValue):
            key_value = self.payload_value_add(dasch_obj)
            for k_v in key_value:
                payloads['add_values'].append(k_v)
            key_value = self.payload_value_del(dasch_obj)
            for k_v in key_value:
                payloads['del_values'].append(k_v)
        elif is_previous_null:
            # Then value must be created.
            key_value = self.payload_value_add(dasch_obj)
            payloads['add_values'].append(key_value)
        else:
            # Then value must be updated.
            key_value = self.payload_value_update(dasch_obj)
            payloads['updates'].append(key_value)
        return payloads


class DateValue(DaschValue):
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

    def get_type(self):
        return 'knora-api:DateValue'

    def is_updated(self, dasch_obj):
        value_old = dasch_obj[self.name]['knora-api:valueAsString']
        return self.value not in value_old

    def payload_value_add(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_del(self, dasch_obj):
        raise NotImplementedError()

    def to_knora(self):
        year = int(self.value[:4])
        month = int(self.value[5:7])
        day = int(self.value[8:])
        return {
            self.name: {
                '@type': self.get_type(),
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

    def payload_value_update(self, dasch_obj):
        field_id = dasch_obj[self.name]['@id']
        key_value = self.to_knora()
        key_value[self.name]['@id'] = field_id
        return key_value


class DocumentFileValue(DaschValue):
    '''Abstract class which shapes the document files.
    '''

    def __init__(self, name, value, checksum, updated_at, licens, cpyright, authors):
        '''Initialization of the fields and inputs validation.'''
        self.name = name
        self.value = value
        self.checksum = checksum
        self.updated_at = updated_at
        self.license = licens
        self.copyright = cpyright
        self.authors = authors

    def __eq__(self, other):
        if not isinstance(other, DocumentFileValue):
            return TypeError()
        return self.name == other.name and self.value == other.value

    def get_type(self):
        return 'knora-api:DocumentFileValue'

    def is_updated(self, dasch_obj):
        # Note: we don't want to download files if it is not necessary.
        # But we also consider the dates and not only the checksum.
        if dasch_obj is None:
            return True
        dasch_date = dasch_obj[self.name]['knora-api:valueCreationDate']['@value']
        update_based_on_date = dasch_date < self.updated_at

        checksum_old = dasch_obj \
            .get('Datacant:hasChecksum', {}) \
            .get('knora-api:valueAsString')
        same_checksum = self.checksum == checksum_old
        return update_based_on_date or not same_checksum

    def to_knora(self):
        return {
            self.name: {
                '@type': self.get_type(),
                'knora-api:fileValueHasFilename': self.value,
                'knora-api:hasLicense': {'@id': self.license},
                'knora-api:hasCopyrightHolder': self.copyright,
                'knora-api:hasAuthorship': self.authors
            }
        }

    def payload_value_add(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_del(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_update(self, dasch_obj):
        raise NotImplementedError()


class IntValue(DaschValue):
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

    def get_type(self):
        return 'knora-api:IntValue'

    def is_updated(self, dasch_obj):
        # TODO
        return False

    def to_knora(self):
        return {
            self.name: {
                '@type': self.get_type(),
                'knora-api:intValueAsInt': self.value,
            }
        }

    def payload_value_add(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_del(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_update(self, dasch_obj):
        raise NotImplementedError()


class LinkValue(DaschValue):
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

    def get_type(self):
        return 'knora-api:LinkValue'

    def is_updated(self, dasch_obj):
        is_previous_null = dasch_obj.get(self.name) is None
        is_new_null = self.value is None
        if is_previous_null and is_new_null:
            return False
        if is_previous_null ^ is_new_null:
            return True
        link_target = dasch_obj[self.name].get('knora-api:linkValueHasTarget')
        if link_target is None:
            link_target = dasch_obj[self.name]['knora-api:linkValueHasTargetIri']
        value_old = link_target['@id']
        return self.value_iri != value_old

    def set_value_iri(self, value_iri):
        self.value_iri = value_iri

    def to_knora(self):
        if self.value is None:
            return {}
        if self.value_iri is None:
            raise RuntimeError('Method cannot be called when `iri` is not set')
        return {
            self.name: {
                '@type': self.get_type(),
                'knora-api:linkValueHasTargetIri': {
                    '@id': self.value_iri
                }
            }
        }

    def payload_value_add(self, dasch_obj):
        return {
            self.name: {
                '@type': self.get_type(),
                'knora-api:linkValueHasTargetIri': {
                    '@id': self.value_iri
                }
            }
        }

    def payload_value_del(self, dasch_obj):
        link_id = dasch_obj[self.name]['@id']
        return {
            self.name: {
                '@id': link_id,
                '@type': self.get_type(),
            }
        }

    def payload_value_update(self, dasch_obj):
        field_id = dasch_obj[self.name]['@id']
        return {
            self.name: {
                '@id': field_id,
                '@type': self.get_type(),
                'knora-api:linkValueHasTargetIri': {
                    '@id': self.value_iri
                }
            }
        }


class LinksValue(DaschValue):
    '''Abstract class which shapes multiple links to another resource.
    '''

    def __init__(self, name, value):
        '''Initialization of the fields and inputs validation.'''
        if not isinstance(value, list):
            raise TypeError()
        self.name = name
        self.value = value
        self.value_iri = None

    def __eq__(self, other):
        if not isinstance(other, LinksValue):
            return TypeError()
        return self.name == other.name and self.value == other.value

    def get_type(self):
        return 'knora-api:LinkValue'

    def is_updated(self, dasch_obj):
        links = dasch_obj[self.name]
        is_list = isinstance(links, list)
        if not is_list:
            # When only a single keyword
            links = [links]
        links_old = []
        for link in links:
            node = link.get('knora-api:linkValueHasTarget')
            if node is None:
                node = link.get('knora-api:linkValueHasTargetIri')
            links_old.append(node['@id'])
        return set(self.value_iri) != set(links_old)

    def set_value_iri(self, value_iri):
        self.value_iri = value_iri

    def to_knora(self):
        links_iri = []
        for keyword_iri in self.value_iri:
            chunk = {
                '@type': self.get_type(),
                'knora-api:linkValueHasTargetIri': {
                    '@id': keyword_iri
                }
            }
            links_iri.append(chunk)
        return {self.name: links_iri}

    def payload_value_add(self, dasch_obj):
        links = dasch_obj[self.name]
        is_list = isinstance(links, list)
        if not is_list:
            # When only a single keyword
            links = [links]
        links_iri_new = set(self.value_iri)
        links_iri_old = set()
        for link in links:
            iri = link['knora-api:linkValueHasTarget']['@id']
            links_iri_old.add(iri)
        link_iri_to_add = list(links_iri_new - links_iri_old)
        add_list = []
        for link_iri in link_iri_to_add:
            add_list.append({
                self.name: {
                    '@type': self.get_type(),
                    'knora-api:linkValueHasTargetIri': {
                        '@id': link_iri
                    }
                }
            })
        return add_list

    def payload_value_del(self, dasch_obj):
        links = dasch_obj[self.name]
        is_list = isinstance(links, list)
        if not is_list:
            # When only a single keyword
            links = [links]
        links_iri_new = set(self.value_iri)
        links_iri_old = set()
        for link in links:
            iri = link['knora-api:linkValueHasTarget']['@id']
            links_iri_old.add(iri)
        link_iri_to_del = list(links_iri_old - links_iri_new)
        del_list = []
        for link in links:
            link_iri = link['@id']
            target_iri = link['knora-api:linkValueHasTarget']['@id']
            if target_iri in link_iri_to_del:
                del_list.append({
                    self.name: {
                        '@id': link_iri,
                        '@type': self.get_type(),
                    }
                })
        return del_list

    def payload_value_update(self, dasch_obj):
        raise RuntimeError('This method should not be called.')


class ListValue(DaschValue):
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

    def get_type(self):
        return 'knora-api:ListValue'

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
                '@type': self.get_type(),
                'knora-api:listValueAsListNode': {
                    '@id': self.value_iri,
                },
            }
        }

    def payload_value_add(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_del(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_update(self, dasch_obj):
        field_id = dasch_obj[self.name]['@id']
        return {
            self.name: {
                '@id': field_id,
                '@type': self.get_type(),
                'knora-api:listValueAsListNode': {
                    '@id': self.value_iri
                }
            }
        }


class RichTextValue(DaschValue):
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

    def get_type(self):
        return 'knora-api:TextValue'

    def is_updated(self, dasch_obj):
        # Note: we cannot compare the new with old value because DaSCH
        # transforms the input. Therefore, we assume a change based on a date.
        dasch_date = dasch_obj[self.name]['knora-api:valueCreationDate']['@value']
        # TODO: check the update using the api.
        return dasch_date < self.updated_at

    def to_knora(self):
        return {
            self.name: {
                '@type': self.get_type(),
                # TODO: check if processing is required.
                'knora-api:textValueAsXml': self.value,
                'knora-api:textValueHasMapping': {
                    '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping'
                }
            }
        }

    def payload_value_add(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_del(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_update(self, dasch_obj):
        field_id = dasch_obj[self.name]['@id']
        return {
            self.name: {
                '@id': field_id,
                '@type': self.get_type(),
                # TODO: check if processing is required.
                'knora-api:textValueAsXml': self.value,
                'knora-api:textValueHasMapping': {
                    '@id': None,  # Will be set later.
                }
            }
        }


class SimpleTextValue(DaschValue):
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

    def get_type(self):
        return 'knora-api:TextValue'

    def is_updated(self, dasch_obj):
        value_old = dasch_obj[self.name]['knora-api:valueAsString']
        return self.value != value_old

    def to_knora(self):
        return {
            self.name: {
                '@type': self.get_type(),
                'knora-api:valueAsString': self.value,
            }
        }

    def payload_value_add(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_del(self, dasch_obj):
        raise NotImplementedError()

    def payload_value_update(self, dasch_obj):
        field_id = dasch_obj[self.name]['@id']
        key_value = self.to_knora()
        key_value[self.name]['@id'] = field_id
        return key_value
