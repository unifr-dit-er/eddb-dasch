import json
from pathlib import Path
import requests
from database.database import Database
from helper import markdown_to_dasch_xml
from models.datacant import Category, DecisionDocument, DecisionSummary, Keyword


PROJECT_NUMBER = '0871'


class Datacant(Database):

    def __init__(self, directory):
        '''Initialization of the fields.'''
        Database.__init__(self, directory, PROJECT_NUMBER)

    def build_eddb_cache(self, since):
        folder = Path(self.directory)
        files = list(folder.glob('e_*'))
        if len(files) == 0:
            since = '2000-01-01'
        else:
            deletion_detected = False
            if deletion_detected:
                since = '2000-01-01'
                for file in files:
                    if file.is_file():
                        file.unlink()
        self.fetch_categories()
        self.fetch_decisions(since)
        self.fetch_keywords()

    def fetch_categories(self):
        category_limit = 200
        url = self.base_url_eddb + '/api/v2/tables/mpqb34djokcbpcy/records'
        params = {'limit': category_limit}
        headers = {'xc-token': self.token_eddb}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code >= 400:
            raise RuntimeError(f'Eddb server error: {r.status_code}')
        response = r.json()
        nb_category = response['pageInfo']['totalRows']
        if category_limit < nb_category:
            raise RuntimeError('Could not fetch all the categories')
        type_in_file = self.map_type_to_file(Category.resource_type())
        for c in response['list']:
            eddb_id = c['Id']
            name_en = c['CategoryEN']
            name_de = c['CategoryDE']
            name_fr = c['CategoryFR']
            try:
                category = Category(eddb_id, name_en, name_de, name_fr)
                filename = f'e_{type_in_file}_{eddb_id}.json'
                file = Path(self.directory) / filename
                file.write_text(json.dumps(category.to_dict(), indent=4), encoding='utf-8')
            except ValueError as err:
                print(f'Category id {eddb_id}: {err}')

    def fetch_decisions(self, since):
        page = 1
        has_next_page = True
        while has_next_page:
            has_next_page = self.fetch_decisions_page(since, page)
            page += 1

    def fetch_decisions_page(self, since, page):
        url = self.base_url_eddb + '/api/v2/tables/merxbxhfvr09g66/records'
        limit = 25
        offset = (page - 1) * limit
        where = f'(CreatedAt,ge,exactDate,{since})~or(UpdatedAt,ge,exactDate,{since})'
        params = {
            'offset': offset,
            'limit': limit,
            'where': where,
            'sort': 'Id',
        }
        headers = {'xc-token': self.token_eddb}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code >= 400:
            raise RuntimeError(f'Eddb server error: {r.status_code}')
        response = r.json()
        has_next_page = not response['pageInfo']['isLastPage']
        judgments = response['list']
        type_summary = self.map_type_to_file(DecisionSummary.resource_type())
        type_document = self.map_type_to_file(DecisionDocument.resource_type())
        for j in judgments:
            eddb_id = j['Id']
            attributes_document = None
            if j['Attachment'] is not None:
                url_file = '{}/{}'.format(self.base_url_eddb, j['Attachment'][0]['path'])
                attributes_document = {
                    'eddb_id': eddb_id,
                    'eddb_url': url_file,
                    'date_issued': j['Date'],
                    'canton': j['Canton'],
                    'updated_at': j['UpdatedAt'],
                    'filename_dasch': None,
                }
            attributes_summary = {
                'eddb_id': eddb_id,
                'updated_at': j['UpdatedAt'],
                'desc_de': j['DescriptionDE'].strip(),
                'desc_fr': j['DescriptionFR'].strip(),
                'abstract_de': markdown_to_dasch_xml(j['AbstractDE']),
                'abstract_fr': markdown_to_dasch_xml(j['AbstractFR']),
                'date_issued': j['Date'],
                'canton': j['Canton'],
                'keywords_id': [],
                'decision_document': None if attributes_document is None else eddb_id,
            }

            for keyword in j['_nc_m2m_Decisions_Keywords']:
                if 'Keywords' not in keyword:
                    # keyword is no longer linked to the decision.
                    continue
                keyword_id = keyword['Keywords_id']
                attributes_summary['keywords_id'].append(keyword_id)

            try:
                decision = DecisionSummary(**attributes_summary)
                filename = f'e_{type_summary}_{eddb_id}.json'
                file = Path(self.directory) / filename
                file.write_text(json.dumps(decision.to_dict(), indent=4), encoding='utf-8')
                if attributes_document is not None:
                    doc = DecisionDocument(**attributes_document)
                    filename = f'e_{type_document}_{eddb_id}.json'
                    file = Path(self.directory) / filename
                    file.write_text(json.dumps(doc.to_dict(), indent=4), encoding='utf-8')
            except ValueError as err:
                print(f'DecisionSummary {eddb_id}: {err}')
        return has_next_page

    def fetch_keywords(self):
        keyword_limit = 1000
        url = self.base_url_eddb + '/api/v2/tables/mp7ev44j9pdsyxs/records'
        params = {'limit': keyword_limit}
        headers = {'xc-token': self.token_eddb}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code >= 400:
            raise RuntimeError(f'Eddb server error: {r.status_code}')
        response = r.json()
        nb_keyword = response['pageInfo']['totalRows']
        if keyword_limit < nb_keyword:
            raise RuntimeError('Could not fetch all the keywords')
        type_in_file = self.map_type_to_file(Keyword.resource_type())
        for k in response['list']:
            eddb_id = k['Id']
            category_id = k['Categories_id']
            name_en = k['KeywordEN']
            name_de = k['KeywordDE']
            name_fr = k['KeywordFR']
            try:
                keyword = Keyword(eddb_id, category_id, name_en, name_de, name_fr)
                filename = f'e_{type_in_file}_{eddb_id}.json'
                file = Path(self.directory) / filename
                file.write_text(json.dumps(keyword.to_dict(), indent=4), encoding='utf-8')
            except ValueError as err:
                print(f'Keyword {eddb_id}: {err}')

    def fill_iri_values(self, object_eddb):
        if isinstance(object_eddb, Category):
            pass
        elif isinstance(object_eddb, Keyword):
            category = object_eddb.category_id
            category_type = Category.resource_type()
            value_iri = self.get_dasch(category_type, category.value)['@id']
            category.set_value_iri(value_iri)
        elif isinstance(object_eddb, DecisionDocument):
            pass
        elif isinstance(object_eddb, DecisionSummary):
            r_type = 'Datacant:Cantons'
            key = object_eddb.canton.value
            canton_iri = self.get_controlled_vocabulary(r_type, key)
            object_eddb.canton.set_value_iri(canton_iri)

            acc = []
            r_type = Keyword.resource_type()
            for k_id in object_eddb.keywords_id.value:
                keyword = self.get_dasch(r_type, k_id)['@id']
                acc.append(keyword)
            object_eddb.keywords_id.set_value_iri(acc)

            r_type = DecisionDocument.resource_type()
            eddb_id = object_eddb.eddb_id.value
            doc = self.get_dasch(r_type, eddb_id)
            doc_iri = doc['@id'] if doc is not None else None
            object_eddb.decision_document.set_value_iri(doc_iri)
        else:
            raise ValueError()

    def get_eddb(self, resource_type, eddb_id):
        type_in_file = self.map_type_to_file(resource_type)
        filename = f'e_{type_in_file}_{eddb_id}.json'
        file = Path(self.directory) / filename
        if not file.exists():
            return None
        json_data = json.loads(file.read_text(encoding='utf-8'))
        if resource_type == Category.resource_type():
            return Category(**json_data)
        if resource_type == Keyword.resource_type():
            return Keyword(**json_data)
        if resource_type == DecisionDocument.resource_type():
            return DecisionDocument(**json_data)
        if resource_type == DecisionSummary.resource_type():
            return DecisionSummary(**json_data)
        return None

    def get_eddb_items(self, resource_type):
        type_in_file = self.map_type_to_file(resource_type)
        pattern = f'e_{type_in_file}*'
        folder = Path(self.directory)
        filenames = list(folder.glob(pattern))
        ret = []
        for filename in filenames:
            n = int(str(filename).rsplit("_", 1)[1].removesuffix(".json"))
            json_data = json.loads(filename.read_text(encoding='utf-8'))
            obj = self.json_to_obj(resource_type, json_data)
            ret.append((n, obj))
        return ret

    def json_to_obj(self, resource_type, json_data):
        if resource_type == Category.resource_type():
            return Category(**json_data)
        if resource_type == Keyword.resource_type():
            return Keyword(**json_data)
        if resource_type == DecisionDocument.resource_type():
            return DecisionDocument(**json_data)
        if resource_type == DecisionSummary.resource_type():
            return DecisionSummary(**json_data)
        raise ValueError(f'Unexpected type: {resource_type}')

    def resource_types(self):
        return [
            Category.resource_type(),
            Keyword.resource_type(),
            DecisionDocument.resource_type(),
            DecisionSummary.resource_type(),
        ]
