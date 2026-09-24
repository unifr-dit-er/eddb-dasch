import os
import requests


DSP_HOST = os.environ.get('DSP_HOST')


def text_to_xml(text):
    return '<?xml version="1.0" encoding="UTF-8"?>\n' \
        f'<text>{text.strip()}</text>'


def transform_to_rich(text, token):
    url = f'{DSP_HOST}/v2/standoff/canonicalize'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain',
    }
    response = requests.post(url, headers=headers, data=text)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot get the XML output: {response.text}')
    return response
