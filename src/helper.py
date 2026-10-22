import markdown
from bs4 import BeautifulSoup


ALLOWED = {
    'p', 'em', 'strong', 'u', 'sub', 'sup', 'strike', 'a',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'br', 'hr', 'pre', 'cite', 'blockquote', 'code',
}
RENAME = {'b': 'strong', 'i': 'em', 'del': 'strike', 's': 'strike'}


def markdown_to_dasch_xml(md_text):
    if md_text is None:
        return None
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all(True):
        tag.name = RENAME.get(tag.name, tag.name)

        if tag.name == 'img':  # no images in the mapping
            tag.replace_with(tag.get('alt', ''))
            continue
        if tag.name not in ALLOWED:  # drop the tag, keep its text
            tag.unwrap()
            continue

        if tag.name == 'a':
            href = tag.get('href', '')
            tag.attrs = {'href': href}
            if href.startswith('http://rdfh.ch/'):  # link to a DSP resource
                tag['class'] = 'salsah-link'
        else:
            tag.attrs = {}  # strip class, id, align, etc.

    body = soup.decode(formatter='minimal')
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<text>{body}</text>'
