import os

DATACANT_CONTEXT = os.environ.get('DATACANT_CONTEXT')
RDFH_PROJECT_URL = os.environ.get('RDFH_PROJECT_URL')


def create(resource_type, label, chunks):
    '''Payload that creates a resource.
    '''
    tmp = {
        '@type': resource_type,
        'knora-api:attachedToProject': {
            '@id': RDFH_PROJECT_URL
        },
        'rdfs:label': label,
        '@context': {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'knora-api': 'http://api.knora.org/ontology/knora-api/v2#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'Datacant': DATACANT_CONTEXT
        }
    }
    chunks.append(tmp)
    return {k: v for d in chunks for k, v in d.items()}


def update(resource_id, resource_type, key_value):
    '''Payload that updates a resource.
    '''
    tmp = {
        "@id": resource_id,
        "@type": resource_type,
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }
    inner_set = next(iter(key_value.values()))
    field_rich = inner_set.get('knora-api:textValueHasMapping')
    if field_rich is not None:
        # TODO: check if the value id is correct.
        field_rich['@id'] = 'http://rdfh.ch/standoff/mappings/StandardMapping'
    tmp.update(key_value)
    return tmp


def add_link(resource_id, resource_type, key_value):
    tmp = {
        "@id": resource_id,
        "@type": resource_type,
        "@context": {
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }
    tmp.update(key_value)
    return tmp


def del_link(resource_id, resource_type, key_value):
    tmp = {
        "@id": resource_id,
        "@type": resource_type,
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "Datacant": DATACANT_CONTEXT
        }
    }
    tmp.update(key_value)
    return tmp


def body_delete_resource(resource_iri, resource_type, last_modification):
    return {
        "@id": resource_iri,
        "@type": resource_type,
        "knora-api:lastModificationDate": {
            "@type": "xsd:dateTimeStamp",
            "@value": last_modification
        },
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "Datacant": DATACANT_CONTEXT
        }
    }


def update_label(resource_id, resource_type, value, last_modification_date):
    return {
        '@id': resource_id,
        '@type': resource_type,
        'rdfs:label': value,
        'knora-api:lastModificationDate': {
            '@type': 'xsd:dateTimeStamp',
            '@value': last_modification_date
        },
        '@context': {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'knora-api': 'http://api.knora.org/ontology/knora-api/v2#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'Datacant': DATACANT_CONTEXT
        }
    }
