import os
from pathlib import Path
import requests
from models.category_model import Category
from models.decision_model import Decision
from models.keyword_model import Keyword

EDDB_TOKEN = os.environ.get('EDDB_TOKEN')


def download_file(url, filename):
    if Path(f'documents/{filename}').is_file():
        return

    r = requests.get(url)
    if not r.ok:
        raise RuntimeError(f'Error while downloading file: {url}')
    with open('documents/{}'.format(filename), 'wb') as f:
        f.write(r.content)


def fetch_eddb_categories():
    category_limit = 200
    url = 'https://eddb.unifr.ch/datacant/api/nocodb/api/v2/tables/mpqb34djokcbpcy/records'
    params = {'limit': category_limit}
    headers = {'xc-token': EDDB_TOKEN}
    r = requests.get(url, params=params, headers=headers)
    response = r.json()
    nb_category = response['pageInfo']['totalRows']
    if category_limit < nb_category:
        raise RuntimeError('Could not fetch all the categories in EDDB: increase the limit')
    rows = {}
    for c in response['list']:
        eddb_id_str = str(c['Id'])
        eddb_id = int(eddb_id_str)
        name_en = c['CategoryEN']
        name_de = c['CategoryDE']
        name_fr = c['CategoryFR']
        try:
            category = Category(eddb_id, name_en, name_de, name_fr)
            rows[eddb_id_str] = category
        except ValueError:
            print(f'Category ({eddb_id}) fails')
    return rows


def fetch_eddb_keywords():
    keyword_limit = 1000
    url = 'https://eddb.unifr.ch/datacant/api/nocodb/api/v2/tables/mp7ev44j9pdsyxs/records'
    params = {'limit': keyword_limit}
    headers = {'xc-token': EDDB_TOKEN}
    r = requests.get(url, params=params, headers=headers)
    response = r.json()
    nb_keyword = response['pageInfo']['totalRows']
    if keyword_limit < nb_keyword:
        raise RuntimeError('Could not fetch all the keywords in EDDB: increase the limit')
    rows = {}
    for k in response['list']:
        eddb_id_str = str(k['Id'])
        eddb_id = int(k['Id'])
        category_id = k['Categories_id']
        name_en = k['KeywordEN']
        name_de = k['KeywordDE']
        name_fr = k['KeywordFR']
        try:
            keyword = Keyword(eddb_id, category_id, name_en, name_de, name_fr)
            rows[eddb_id_str] = keyword
        except ValueError:
            print(f'Keyword ({eddb_id}) fails')
    return rows


def fetch_eddb_decisions():
    decisions = {}
    page = 1
    has_next_page = True
    while has_next_page:
        decisions_page, has_next_page = fetch_eddb_decisions_page(page)
        decisions.update(decisions_page)
        page += 1
    return decisions


def fetch_eddb_decisions_page(page):
    url = 'https://eddb.unifr.ch/noco/api/v2/tables/merxbxhfvr09g66/records'
    limit = 25
    offset = (page - 1) * limit
    params = {'offset': offset, 'limit': limit, 'where': ''}
    headers = {'xc-token': EDDB_TOKEN}
    r = requests.get(url, params=params, headers=headers)
    response = r.json()
    has_next_page = not response['pageInfo']['isLastPage']
    judgments = response['list']
    rows = {}
    for j in judgments:
        url_file = 'https://eddb.unifr.ch/noco/{}'.format(j['Attachment'][0]['path'])
        eddb_id_str = str(j['Id'])
        eddb_id = int(eddb_id_str)
        attributes = {
            'url_file': url_file,
            'eddb_id': eddb_id,
            'updated_at': j['UpdatedAt'],
            'desc_de': j['DescriptionDE'].strip(),
            'desc_fr': j['DescriptionFR'].strip(),
            'abstract_de': j['AbstractDE'].strip(),
            'abstract_fr': j['AbstractFR'].strip(),
            'date_issued': j['Date'],
            'canton': j['Canton'],
            'keywords_id': [],
        }

        for keyword in j['_nc_m2m_Decisions_Keywords']:
            # TODO: check that condition below.
            if 'Keywords' not in keyword:
                print('Decision keywords not found:', keyword)
                continue
            keyword_id = keyword['Keywords_id']
            attributes['keywords_id'].append(keyword_id)

        try:
            rows[eddb_id_str] = Decision(**attributes)
        except ValueError:
            print(f'Decision ({eddb_id}) fails')
    return rows, has_next_page


def fetch_all_eddb():
    data = {}
    data['category'] = fetch_eddb_categories()
    data['keyword'] = fetch_eddb_keywords()
    data['decision'] = fetch_eddb_decisions()
    return data
