import json
from itertools import batched
import os
from pathlib import Path
import requests
from urllib.parse import quote
from helper import (
    is_class_category,
    is_class_decision,
    is_class_keyword,
)


BATCH_SIZE = 64
DSP_HOST = os.environ.get('DSP_HOST')
DSP_EMAIL = os.environ.get('DSP_EMAIL')
DSP_PASSWORD = os.environ.get('DSP_PASSWORD')


def fetch_batch(batch, token):
    url = f'{DSP_HOST}/v2/resources/batch'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    data = {'resourceIris': batch}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code >= 400:
        raise RuntimeError('Cannot fetch batch resources on DaSCH')
    resp = response.json()
    # if batch contains only one element, then it is not an array.
    return resp['@graph'] if '@graph' in resp else [resp]


def fetch_all_resources(token, use_cache):
    '''Fetch the user data and enumerations.
    '''
    if use_cache:
        dasch_db_file = Path('data/data_dasch.json')
        if dasch_db_file.exists():
            data = json.loads(dasch_db_file.read_text(encoding='utf-8'))
            data['category'] = {int(k): v for k, v in data['category'].items()}
            data['keyword'] = {int(k): v for k, v in data['keyword'].items()}
            data['decision'] = {int(k): v for k, v in data['decision'].items()}
            return data

    url = f'{DSP_HOST}/v2/metadata/projects/0871/resources?format=json'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        raise RuntimeError('Cannot fetch resources on DaSCH')
    rows = response.json()
    data = build_dasch_data(rows, token)

    data['cantons'] = fetch_controlled_vocabulary(token)
    return data


def fetch_controlled_vocabulary(token):
    '''Fetch the enumerations defined in the project.
    '''
    url = f'{DSP_HOST}/admin/lists'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    r = response.json()
    for project in r['lists']:
        if '/lists/0871/' in project['id']:
            list_canton_iri = project['id']
            break  # There is only one controlled vocabulary.
    list_canton_iri_enc = quote(list_canton_iri, safe='')
    url = f'{DSP_HOST}/admin/lists/{list_canton_iri_enc}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError('Cannot fetch resources controlled vocabulary')
    r = response.json()
    cantons = {}
    for canton in r['list']['children']:
        name = canton['name']
        cantons[name] = canton['id']
    return cantons


def fetch_resource(iri, token):
    iri_enc = quote(iri, safe='')
    url = f'{DSP_HOST}/v2/resources/{iri_enc}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f'Cannot fetch resource {iri}')
    return response.json()


def fetch_token():
    url = f'{DSP_HOST}/v2/authentication'
    json_data = {'email': DSP_EMAIL, 'password': DSP_PASSWORD}

    response = requests.post(url, json=json_data)

    if response.status_code != 200:
        raise RuntimeError(f'Cannot fetch token: {response.text}')
    j = response.json()
    return j['token']


def build_dasch_data(rows, token):
    data = {'category': {}, 'keyword': {}, 'decision': {}}
    iris = []
    for row in rows:
        if 'resourceDeletionDate' not in row:
            iris.append(row['resourceIri'])
    for batch_iri in batched(iris, BATCH_SIZE):
        resources = fetch_batch(batch_iri, token)
        for resource in resources:
            id_eddb = resource['Datacant:hasId']['knora-api:intValueAsInt']
            if is_class_category(resource):
                data['category'][id_eddb] = resource
            elif is_class_keyword(resource):
                data['keyword'][id_eddb] = resource
            elif is_class_decision(resource):
                data['decision'][id_eddb] = resource
            else:
                raise ValueError('Unknown class')
    return data


def create_resource(body, token):
    url = f'{DSP_HOST}/v2/resources'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Error while creating resource: {response.text}')
    return response.json()['@id']


def create_value(body, token):
    url = f'{DSP_HOST}/v2/values'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot create value: {response.text}')


def delete_value(body, token):
    url = f'{DSP_HOST}/v2/values/delete'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot delete value: {response.text}')


def delete_resource(body, token):
    url = f'{DSP_HOST}/v2/resources/delete'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot delete resource: {response.text}')


def update_label(body, token):
    url = f'{DSP_HOST}/v2/resources'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.put(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot update label: {response.text}')
    return response


def update_value(body, token):
    url = f'{DSP_HOST}/v2/values'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.put(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot update value: {response.text}')
