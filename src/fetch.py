from datetime import date, timedelta
import json
import os
from pathlib import Path
import requests
from models.category_model import Category
from models.decision_model import Decision
from models.keyword_model import Keyword

EDDB_TOKEN = os.environ.get('EDDB_TOKEN')
NB_DAYS_LAST_INGESTION = 60


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
        eddb_id = c['Id']
        name_en = c['CategoryEN']
        name_de = c['CategoryDE']
        name_fr = c['CategoryFR']
        try:
            category = Category(eddb_id, name_en, name_de, name_fr)
            rows[eddb_id] = category
        except ValueError as err:
            print(f'Category id {eddb_id}: {err}')
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
        eddb_id = k['Id']
        category_id = k['Categories_id']
        name_en = k['KeywordEN']
        name_de = k['KeywordDE']
        name_fr = k['KeywordFR']
        try:
            keyword = Keyword(eddb_id, category_id, name_en, name_de, name_fr)
            rows[eddb_id] = keyword
        except ValueError as err:
            print(f'Keyword {eddb_id}: {err}')
    return rows


def fetch_eddb_decisions(reset_cache):
    decisions = {}
    date_start = '2000-01-01'
    if not reset_cache:
        date_start = date.today() - timedelta(days=NB_DAYS_LAST_INGESTION)
    page = 1
    has_next_page = True
    while has_next_page:
        decisions_page, has_next_page = fetch_eddb_decisions_page(date_start, page)
        decisions.update(decisions_page)
        page += 1
    return decisions


def fetch_eddb_decisions_page(date_start, page):
    url = 'https://eddb.unifr.ch/noco/api/v2/tables/merxbxhfvr09g66/records'
    limit = 25
    offset = (page - 1) * limit
    where = f'(CreatedAt,ge,exactDate,{date_start})~or(UpdatedAt,ge,exactDate,{date_start})'
    params = {
        'offset': offset,
        'limit': limit,
        'where': where,
        'sort': 'Id',
    }
    headers = {'xc-token': EDDB_TOKEN}
    r = requests.get(url, params=params, headers=headers)
    response = r.json()
    has_next_page = not response['pageInfo']['isLastPage']
    judgments = response['list']
    rows = {}
    for j in judgments:
        url_file = 'https://eddb.unifr.ch/noco/{}'.format(j['Attachment'][0]['path'])
        eddb_id = j['Id']
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
            rows[eddb_id] = Decision(**attributes)
        except ValueError as err:
            print(f'Decision {eddb_id}: {err}')
    return rows, has_next_page


def fetch_all_eddb(reset_cache):
    data = {'category': {}, 'keyword': {}, 'decision': {}}

    category_file = Path('data/eddb_categories.json')
    if category_file.exists():
        tmp = json.loads(category_file.read_text(encoding='utf-8'))
        data['category'] = {int(k): Category(**v) for k, v in tmp.items()}

    keyword_file = Path('data/eddb_keywords.json')
    if keyword_file.exists():
        tmp = json.loads(keyword_file.read_text(encoding='utf-8'))
        data['keyword'] = {int(k): Keyword(**v) for k, v in tmp.items()}

    decision_file = Path('data/eddb_decisions.json')
    if decision_file.exists():
        tmp = json.loads(decision_file.read_text(encoding='utf-8'))
        data['decision'] = {int(k): Decision(**v) for k, v in tmp.items()}

    data['category'].update(fetch_eddb_categories())
    data['keyword'].update(fetch_eddb_keywords())
    data['decision'].update(fetch_eddb_decisions(reset_cache))
    return data
