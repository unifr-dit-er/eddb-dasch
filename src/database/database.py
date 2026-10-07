from abc import ABC, abstractmethod
import json
from itertools import batched
import os
from pathlib import Path
import requests
from urllib.parse import quote


BATCH_SIZE = 64


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
            .format(self.dsp_host, self.project_number)
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
            resources = fetch_batch(batch_iri)
            for resource in resources:
                id_eddb = resource['Datacant:hasId']['knora-api:intValueAsInt']
                resource_type = resource['@type']
                if resource_type not in expected_types:
                    raise ValueError('Unknown class')
                # TODO: write to disk (type, id_eddb) <- resource

        cantons = fetch_controlled_vocabulary(token)
        # TODO: write to disk.

    @abstractmethod
    def build_eddb_cache(self):
        pass

    def fetch_batch(self, batch):
        url = f'{self.dsp_host}/v2/resources/batch'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        data = {'resourceIris': batch}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code >= 400:
            raise RuntimeError('Cannot fetch batch resources on DaSCH')
        resp = response.json()
        # if batch contains only one element, then it is not an array.
        return resp['@graph'] if '@graph' in resp else [resp]

    def fetch_checksum(self, dasch_obj):
        if dasch_obj is None:
            return ''
        filename = dasch_obj \
            .get('knora-api:hasDocumentFileValue') \
            .get('knora-api:fileValueHasFilename')
        filename_id = filename.split('.')[0]
        url = f'{self.ingest_host}/projects/{self.project_number}/assets/{filename_id}'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            raise RuntimeError('Cannot fetch document checksum')
        checksum = response.json()['checksumOriginal']
        return checksum

    def fetch_controlled_vocabulary(self):
        '''Fetch the enumerations defined in the project.
        '''
        url = f'{self.dsp_host}/admin/lists'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        r = response.json()
        for project in r['lists']:
            if '/lists/{}/'.format(self.project_number) in project['id']:
                list_canton_iri = project['id']
                break  # There is only one controlled vocabulary.
        list_canton_iri_enc = quote(list_canton_iri, safe='')
        url = f'{self.dsp_host}/admin/lists/{list_canton_iri_enc}'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise RuntimeError('Cannot fetch resources controlled vocabulary')
        r = response.json()
        cantons = {}
        for canton in r['list']['children']:
            name = canton['name']
            cantons[name] = canton['id']
        return cantons

    def fetch_resource(self, iri):
        iri_enc = quote(iri, safe='')
        url = f'{self.dsp_host}/v2/resources/{iri_enc}'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f'Cannot fetch resource {iri}')
        return response.json()

    @abstractmethod
    def fill_iri_values(self, object_eddb):
        pass

    def get_controlled_vocabulary(self, resource_type, key):
        folder = Path(self.directory)
        file = folder / 'd_vocabularies.json'
        if file.exists():
            voc = json.loads(file.read_text(encoding='utf-8'))
            return voc[resource_type][key]
        raise ValueError()

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
        filenames = list(folder.glob(pattern))
        ret = []
        for filename in filenames:
            n = int(str(filename).rsplit("_", 1)[1].removesuffix(".json"))
            obj = json.loads(filename.read_text(encoding='utf-8'))
            ret.append((n, obj))
        return ret

    @abstractmethod
    def get_eddb(self, resource_type, eddb_id):
        pass

    @abstractmethod
    def get_eddb_items(self, resource_type):
        pass

    def label_update(self, body):
        url = f'{self.dsp_host}/v2/resources'
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
        url = f'{self.dsp_host}/v2/resources'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Error while creating resource: {response.text}')
        return response.json()['@id']

    def resource_delete(self, body):
        url = f'{self.dsp_host}/v2/resources/delete'
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

    def transform_to_rich(self, text):
        url = f'{self.dsp_host}/v2/standoff/canonicalize'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'text/plain',
        }
        response = requests.post(url, headers=headers, data=text)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot get the XML output: {response.text}')
        return response

    def value_create(body):
        url = f'{self.dsp_host}/v2/values'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot create value: {response.text}')

    def value_delete(self, body):
        url = f'{self.dsp_host}/v2/values/delete'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot delete value: {response.text}')

    def value_update(self, body):
        url = f'{self.dsp_host}/v2/values'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(f'Cannot update value: {response.text}')


    def upload_to_ingest(filename):
        url = f'{self.ingest_host}/projects/0871/assets/ingest/{filename}'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/octet-stream',
        }
        output_dir = Path('data/documents')
        filepath = output_dir / filename
        if not filepath.is_file():
            raise RuntimeError(f'File {filename} not found when uploading it')
        with open(filepath, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
            if response.status_code >= 400:
                raise RuntimeError(f'Cannot upload file {filename}: {response.text}')
            return response.json()
