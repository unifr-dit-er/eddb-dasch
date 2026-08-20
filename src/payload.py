import os

DATACANT_CONTEXT = os.environ.get('DATACANT_CONTEXT')
RDFH_PROJECT_URL = os.environ.get('RDFH_PROJECT_URL')


def body_add_link(resource_id, resource_type, field, iri_value):
    return {
        "@id": resource_id,
        "@type": resource_type,
        field: {
            "@type": "knora-api:LinkValue",
            "knora-api:linkValueHasTargetIri": {
              "@id": iri_value,
            }
        },
        "@context": {
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }


def body_unlink_keyword(decision_iri, link_iri, target_iri):
    return {
        "@id": decision_iri,
        "@type": "Datacant:Decisions",
        "Datacant:linkToKeywordValue": [
            {
                "@id": link_iri,
                "@type": "knora-api:LinkValue",
                "knora-api:linkValueHasTargetIri": {
                  "@id": target_iri
                }
            }
        ],
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "Datacant": DATACANT_CONTEXT
        }
    }


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


def body_create_decision(did, label, date, filename, filename_tmp, canton_iri, desc_de, desc_fr, abstract_de, abstract_fr, category_iri):
    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:])
    categories = []
    for iri in category_iri:
        category = {
            "@type": "knora-api:LinkValue",
            "knora-api:linkValueHasTargetIri": {
                "@id": iri
            }
        }
        categories.append(category)
    return {
      "@type": "Datacant:Decisions",
      "knora-api:hasDocumentFileValue": {
          "@type": "knora-api:DocumentFileValue",
          "knora-api:fileValueHasFilename": filename_tmp,
          "knora-api:hasLicense": {"@id": "http://rdfh.ch/licenses/public-domain"},
          "knora-api:hasCopyrightHolder": "Public Domain - Not Protected by Copyright",
          "knora-api:hasAuthorship": ["Swiss court"]
      },
      "Datacant:hasId": {
          "@type": "knora-api:IntValue",
          "knora-api:intValueAsInt": did,
      },
      "Datacant:hasCantonList": {
          "@type": "knora-api:ListValue",
          "knora-api:listValueAsListNode": {
              "@id": canton_iri,
          },
      },
      "Datacant:hasDateIssued": {
          "@type": "knora-api:DateValue",
          "knora-api:dateValueHasStartYear": year,
          "knora-api:dateValueHasEndYear": year,
          "knora-api:dateValueHasStartMonth": month,
          "knora-api:dateValueHasEndMonth": month,
          "knora-api:dateValueHasStartDay": day,
          "knora-api:dateValueHasEndDay": day,
          "knora-api:dateValueHasStartEra": "CE",
          "knora-api:dateValueHasEndEra": "CE",
          "knora-api:dateValueHasCalendar": "GREGORIAN"
      },
      "Datacant:linkToKeywordValue": categories,
      "Datacant:hasDescriptionDe": {
          "@type": "knora-api:TextValue",
          "knora-api:valueAsString": desc_de
      },
      "Datacant:hasDescriptionFr": {
          "@type": "knora-api:TextValue",
          "knora-api:valueAsString": desc_fr
      },
      "Datacant:hasAbstractDe": {
          "@type": "knora-api:TextValue",
          "knora-api:textValueAsXml": abstract_de,
          "knora-api:textValueHasMapping": {
            "@id": "http://rdfh.ch/standoff/mappings/StandardMapping"
          }
      },
      "Datacant:hasAbstractFr": {
          "@type": "knora-api:TextValue",
          "knora-api:textValueAsXml": abstract_fr,
          "knora-api:textValueHasMapping": {
            "@id": "http://rdfh.ch/standoff/mappings/StandardMapping"
          }
      },
      "Datacant:hasFileName": {
          "@type": "knora-api:TextValue",
          "knora-api:valueAsString": filename
      },
      "knora-api:attachedToProject": {
          "@id": RDFH_PROJECT_URL
      },
      "rdfs:label": label,
      "@context": {
          "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
          "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
          "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
          "xsd": "http://www.w3.org/2001/XMLSchema#",
          "Datacant": DATACANT_CONTEXT
      }
    }


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


def body_update_link(resource_id, resource_type, field, field_id, value):
    '''Link like a foreign key.'''
    return {
        "@id": resource_id,
        "@type": resource_type,
        field: {
            "@id": field_id,
            "@type": "knora-api:LinkValue",
            "knora-api:linkValueHasTargetIri": {
                "@id": value,
            },
        },
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }


def body_update_date(resource_id, resource_type, field, field_id, value):
    year = int(value[:4])
    month = int(value[5:7])
    day = int(value[8:])
    return {
        "@id": resource_id,
        "@type": resource_type,
        field: {
            "@id": field_id,
            "@type": "knora-api:DateValue",
            "knora-api:dateValueHasStartYear": year,
            "knora-api:dateValueHasEndYear": year,
            "knora-api:dateValueHasStartMonth": month,
            "knora-api:dateValueHasEndMonth": month,
            "knora-api:dateValueHasStartDay": day,
            "knora-api:dateValueHasEndDay": day,
            "knora-api:dateValueHasStartEra": "CE",
            "knora-api:dateValueHasEndEra": "CE",
            "knora-api:dateValueHasCalendar": "GREGORIAN"
        },
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }


def body_update_rich_text(resource_id, resource_type, field, field_id, value):
    return {
        "@id": resource_id,
        "@type": resource_type,
        field: {
            "@id": field_id,
            "@type": "knora-api:TextValue",
            "knora-api:textValueAsXml": value,
            "knora-api:textValueHasMapping": {
              "@id": RDFH_PROJECT_URL
            }
        },
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }


def body_update_simple_text(resource_id, resource_type, field, field_id, value):
    return {
        "@id": resource_id,
        "@type": resource_type,
        field: {
            "@id": field_id,
            "@type": "knora-api:TextValue",
            "knora-api:valueAsString": value
        },
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
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


def body_update_list(resource_id, field_id, iri_value):
    '''Related to controlled vocabulary'''
    return {
        "@id": resource_id,
        "@type": "Datacant:Decisions",
        "Datacant:hasCantonList": {
            "@id": field_id,
            "@type": "knora-api:ListValue",
            "knora-api:listValueAsListNode": {
                "@id": iri_value,
            },
        },
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "Datacant": DATACANT_CONTEXT
        }
    }
