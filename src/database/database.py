from abc import ABC, abstractmethod
import json
import os
from pathlib import Path
import requests


class Database(ABC):
    '''Abstract class which shapes the databases.
    '''

    def __init__(self, directory, project_number):
        self.directory = directory
        self.dsp_host = os.environ.get('DSP_HOST')
        self.ingest_host = os.environ.get('INGEST_HOST')
        self.project_number = project_number
        self.set_token_dasch()
        self.set_token_eddb()

    @staticmethod
    def all_projects():
        return ['Datacant']

    def build_dasch_cache(self):
        url = '{}/v2/metadata/projects/{}/resources?format=json' \
            .format(self.DSP_HOST, self.project_number)
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            raise RuntimeError('Cannot fetch resources on DaSCH:', response.text)
        rows = response.json()

        iris = []
        for row in rows:
            if 'resourceDeletionDate' not in row:
                iris.append(row['resourceIri'])
        expected_types = self.resource_types()
        for batch_iri in batched(iris, BATCH_SIZE):
            resources = fetch_batch(batch_iri, token)
            for resource in resources:
                id_eddb = resource['Datacant:hasId']['knora-api:intValueAsInt']
                resource_type = resource['@type']
                if resource_type not in expected_types:
                    raise ValueError('Unknown class')
                # TODO: write to disk (type, id_eddb) <- resource
        # TODO: vocabularies
        data['Datacant:Cantons'] = fetch_controlled_vocabulary(token)

    @abstractmethod
    def build_eddb_cache(self):
        pass

    def get_dasch(self, resource_type, eddb_id):
        type_in_file = self.map_type_to_file(resource_type)
        filename = f'd_{type_in_file}_{eddb_id}.json'
        file = Path(self.directory) / filename
        if file.exists():
            return json.loads(file.read_text(encoding='utf-8'))
        return None

    def get_dasch_items(self, resource_type):
        type_in_file = self.map_type_to_file(resource_type)
        pattern = f'd_{type_in_file}*'
        folder = Path(self.directory)
        return folder.glob(pattern)

    def get_eddb(self, resource_type, eddb_id):
        type_in_file = self.map_type_to_file(resource_type)
        filename = f'e_{type_in_file}_{eddb_id}.json'
        file = Path(self.directory) / filename
        if file.exists():
            return json.loads(file.read_text(encoding='utf-8'))
        return None

    def get_eddb_items(self, resource_type):
        type_in_file = self.map_type_to_file(resource_type)
        pattern = f'e_{type_in_file}*'
        folder = Path(self.directory)
        return folder.glob(pattern)

    def label_update(self, body):
        url = f'{DSP_HOST}/v2/resources'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot update label: {response.text}')
        return response

    @abstractmethod
    def resource_types(self):
        '''The order matters and must follow the order of SQL table creation.
        '''
        pass

    def map_type_to_file(self, t):
        index = 1 + t.find(':')
        return t[index:].lower()

    def resource_create(self, body):
        url = f'{DSP_HOST}/v2/resources'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Error while creating resource: {response.text}')
        return response.json()['@id']

    def resource_delete(self, body):
        url = f'{DSP_HOST}/v2/resources/delete'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot delete resource: {response.text}')

    def set_token_dasch(self):
        url = f'{self.dsp_host}/v2/authentication'
        json_data = {
            'email': os.environ.get('DSP_EMAIL'),
            'password': os.environ.get('DSP_PASSWORD'),
        }
        response = requests.post(url, json=json_data)
        if response.status_code != 200:
            raise RuntimeError(f'Cannot fetch token: {response.text}')
        j = response.json()
        self.token_dasch = j['token']

    def set_token_eddb(self):
        self.token_eddb = os.environ.get('EDDB_TOKEN')

    def value_create(body):
        url = f'{DSP_HOST}/v2/values'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot create value: {response.text}')

    def value_delete(self, body):
        url = f'{DSP_HOST}/v2/values/delete'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot delete value: {response.text}')

    def value_update(self, body):
        url = f'{DSP_HOST}/v2/values'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot update value: {response.text}')
