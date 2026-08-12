def get_keyword_iri(dasch, eddb_id_int):
    return dasch['keyword'][eddb_id_int]['@id']


def is_before(d1, d2):
    return d1 < d2


def is_class_category(fields):
    return fields['@type'] == 'Datacant:Category'


def is_class_decision(fields):
    return fields['@type'] == 'Datacant:Decisions'


def is_class_keyword(fields):
    return fields['@type'] == 'Datacant:Keyword'


def text_to_xml(text):
    return '<?xml version="1.0" encoding="UTF-8"?>\n' \
        f'<text>{text.strip()}</text>'
