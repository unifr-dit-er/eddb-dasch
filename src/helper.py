def get_keyword_iri(dasch, eddb_id_str):
    return dasch['keyword'][eddb_id_str]['@id']


def is_before(d1, d2):
    return d1 < d2


def is_class_category(fields):
    return fields['@type'] == 'Datacant:Category'


def is_class_decision(fields):
    return fields['@type'] == 'Datacant:Decisions'


def is_class_keyword(fields):
    return fields['@type'] == 'Datacant:Keyword'
