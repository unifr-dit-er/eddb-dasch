import json
import requests
from urllib.parse import quote
from helper import (
    is_class_category,
    is_class_decision,
    is_class_keyword,
)


def fetch_all_resources(token, use_cache):
    '''Fetch the user data and enumerations.
    '''
    if use_cache:
        with open('data/data_dasch.json', 'r') as f:
            return json.load(f)

    url = 'http://localhost:3333/v2/metadata/projects/0871/resources?format=json'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        raise RuntimeError('Cannot fetch resources on DaSCH')
    rows = response.json()
    data = build_dasch_data(rows, token)

    url = 'http://localhost:3333/admin/lists'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    r = response.json()
    list_canton_iri = r['lists'][0]['id']  # There is only one controlled vocabulary.
    list_canton_iri_enc = quote(list_canton_iri, safe='')
    url = f'http://localhost:3333/admin/lists/{list_canton_iri_enc}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError('Cannot fetch resources controlled vocabulary')
    r = response.json()
    cantons = {}
    for canton in r['list']['children']:
        name = canton['name']
        cantons[name] = canton['id']
    data['cantons'] = cantons
    return data


def fetch_resource(iri, token):
    iri_enc = quote(iri, safe='')
    url = f'http://localhost:3333/v2/resources/{iri_enc}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f'Cannot fetch resource {iri}')
    return response.json()


def fetch_token():
    url = 'http://localhost:3333/v2/authentication'
    json_data = {'email': 'root@example.com', 'password': 'test'}

    response = requests.post(url, json=json_data)

    if response.status_code != 200:
        raise RuntimeError('Cannot fetch token')
    j = response.json()
    return j['token']


def build_dasch_data(rows, token):
    data = {'category': {}, 'keyword': {}, 'decision': {}}
    for row in rows:
        if 'resourceDeletionDate' in row:
            continue
        resource_iri = row['resourceIri']
        resource = fetch_resource(resource_iri, token)
        id_eddb = resource['Datacant:hasId']['knora-api:intValueAsInt']
        id_eddb_str = str(id_eddb)
        if is_class_category(resource):
            data['category'][id_eddb_str] = resource
        elif is_class_keyword(resource):
            data['keyword'][id_eddb_str] = resource
        elif is_class_decision(resource):
            data['decision'][id_eddb_str] = resource
        else:
            raise ValueError('Unknown class')
    return data


def create_resource(body, token):
    url = 'http://localhost:3333/v2/resources'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Error while creating resource: {response.text}')
    return response.json()['@id']


def create_value(body, token):
    url = 'http://localhost:3333/v2/values'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError('Cannot create value')


def delete_value(body, token):
    url = 'http://localhost:3333/v2/values/delete'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError('Cannot delete value')


def delete_resource(body, token):
    url = 'http://localhost:3333/v2/resources/delete'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError('Cannot delete resource')


def update_label(body, token):
    url = 'http://localhost:3333/v2/resources'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.put(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError(f'Cannot update label: {response.text}')
    return response


def update_value(body, token):
    url = 'http://localhost:3333/v2/values'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    response = requests.put(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise RuntimeError('Cannot update value')
