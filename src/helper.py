def is_before(d1, d2):
    return d1 < d2


def text_to_xml(text):
    return '<?xml version="1.0" encoding="UTF-8"?>\n' \
        f'<text>{text.strip()}</text>'
