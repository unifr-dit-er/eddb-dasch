from dotenv import load_dotenv
load_dotenv()

import json
import os
from pathlib import Path
from fetch import download_file, fetch_all_eddb
from helper import get_keyword_iri
from models.decision_model import Decision
from payload import body_delete_resource
from repository import (
    fetch_all_resources,
    fetch_resource,
    fetch_token,
    create_resource,
    create_value,
    delete_resource,
    delete_value,
    update_label,
    update_value,
)


USE_DASCH_CACHE = os.environ.get('USE_DASCH_CACHE') in ('true', 'True', 'TRUE')


if __name__ == '__main__':
    token = fetch_token()

    data_dasch = fetch_all_resources(token, use_cache=USE_DASCH_CACHE)
    with open('data/data_dasch.json', 'w') as f:
        f.write(json.dumps(data_dasch, indent=4))

    data_eddb = fetch_all_eddb(reset_cache=False)
    with open('data/eddb_categories.json', 'w') as f:
        tmp = {k: v.__dict__ for k, v in data_eddb['category'].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_keywords.json', 'w') as f:
        tmp = {k: v.__dict__ for k, v in data_eddb['keyword'].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_decisions.json', 'w') as f:
        tmp = {k: v.__dict__ for k, v in data_eddb['decision'].items()}
        f.write(json.dumps(tmp, indent=4))

    # Step 1: Update existing categories or add new categories.
    for cid, category_eddb in data_eddb['category'].items():
        category_dasch = data_dasch['category'].get(cid)
        has_changed = False
        if category_dasch is None:
            # Add new category.
            payload = category_eddb.payload_add()
            resource_id = create_resource(payload, token)
            has_changed = True
        else:
            # Maybe update existing category.
            resource_id = category_dasch['@id']

            label_old = category_dasch['rdfs:label']
            if category_eddb.has_label_changed(label_old):
                last_modification = \
                    category_dasch.get('knora-api:lastModificationDate', {}).get('@value')
                payload = category_eddb.payload_update_label(resource_id, last_modification)
                response = update_label(payload, token)
                has_changed = True
            payload_updates = category_eddb.payload_update_fields(category_dasch)
            for payload in payload_updates:
                update_value(payload, token)
        if has_changed or len(payload_updates) != 0:
            data_dasch['category'][cid] = fetch_resource(resource_id, token)

    # Step 2: Update existing keywords or add new keywords.
    for kid, keyword_eddb in data_eddb['keyword'].items():
        keyword_dasch = data_dasch['keyword'].get(kid)
        has_changed = False
        category_id = keyword_eddb.category_id

        if keyword_dasch is None:
            # Add new keyword.
            category_iri = data_dasch['category'][category_id]['@id']
            payload = keyword_eddb.payload_add(category_iri)
            resource_id = create_resource(payload, token)
            has_changed = True
        else:
            # Maybe update existing keyword.
            resource_id = keyword_dasch['@id']

            label_old = keyword_dasch['rdfs:label']
            if keyword_eddb.has_label_changed(label_old):
                last_modification = \
                    keyword_dasch.get('knora-api:lastModificationDate', {}).get('@value')
                payload = keyword_eddb.payload_update_label(resource_id, last_modification)
                response = update_label(payload, token)
                has_changed = True
            payload_updates = keyword_eddb.payload_update_fields(data_dasch)
            for payload in payload_updates:
                update_value(payload, token)
        if has_changed or len(payload_updates) != 0:
            data_dasch['keyword'][kid] = fetch_resource(resource_id, token)

    # Step 3: Update existing decisions or add new decisions.
    resources = []
    is_import_required = False
    for did, decision_eddb in data_eddb['decision'].items():
        decision_dasch = data_dasch['decision'].get(did)
        has_changed = False

        if decision_dasch is None:
            # Add new decision.
            is_import_required = True
            keywords_iri = []
            for eddb_id in decision_eddb.keywords_id:
                iri = get_keyword_iri(data_dasch, eddb_id)
                keywords_iri.append(iri)
            resource = decision_eddb.payload_add(keywords_iri)
            resources.append(resource)
            url_file = decision_eddb.url_file
            filename = decision_eddb.filename_eddb()
            download_file(url_file, filename)
        else:
            # Maybe update existing decision.
            resource_id = decision_dasch['@id']

            # label
            label_old = decision_dasch['rdfs:label']
            if decision_eddb.has_label_changed(label_old):
                last_modification = \
                    decision_dasch.get('knora-api:lastModificationDate', {}).get('@value')
                payload = decision_eddb.payload_update_label(resource_id, last_modification)
                response = update_label(payload, token)
                has_changed = True

            payloads = decision_eddb.payload_update_fields(data_dasch)
            (payload_updates, payload_add, payload_del) = payloads
            has_changed = has_changed or \
                len(payload_updates) != 0 or \
                len(payload_add) != 0 or \
                len(payload_del) != 0
            for payload in payload_updates:
                update_value(payload, token)
            for payload in payload_add:
                create_value(payload, token)
            for payload in payload_del:
                delete_value(payload, token)

            if has_changed:
                data_dasch['decision'][did] = fetch_resource(resource_id, token)

    if is_import_required:
        exit_code = Decision.run_cmd_import(resources)
        if exit_code != 0:
            raise RuntimeError('Error while uploading files to DaSCH')
        try:
            current_directory = Path('.')
            file = next(current_directory.glob('id2iri_*.json'))
            with file.open() as f:
                iri_id = json.load(f)
                for eddb_id_str, iri in iri_id.items():
                    eddb_id = int(eddb_id_str[2:])  # `eddb_id_str` looks like "D_<id>"
                    data_dasch['decision'][eddb_id] = fetch_resource(iri, token)
            file.unlink()
        except StopIteration:
            raise RuntimeError('Error file mapping iri and eddb id not found')

    # Step 4: Delete decisions.
    keys_to_remove = []
    for eddb_id_old, row in data_dasch['decision'].items():
        if eddb_id_old not in data_eddb['decision']:
            resource_iri = row['@id']
            resource_type = 'Datacant:Decisions'
            last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
            body = body_delete_resource(resource_iri, resource_type, last_modification)
            delete_resource(body, token)
            keys_to_remove.append(eddb_id_old)
    for k in keys_to_remove:
        data_dasch['decision'].pop(k)

    # Step 5: Delete keywords.
    keys_to_remove = []
    for eddb_id_old, row in data_dasch['keyword'].items():
        if eddb_id_old not in data_eddb['keyword']:
            resource_iri = row['@id']
            resource_type = 'Datacant:Keyword'
            last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
            body = body_delete_resource(resource_iri, resource_type, last_modification)
            delete_resource(body, token)
            keys_to_remove.append(eddb_id_old)
    for k in keys_to_remove:
        data_dasch['keyword'].pop(k)

    # Step 6: Delete categories.
    keys_to_remove = []
    for eddb_id_old, row in data_dasch['category'].items():
        if eddb_id_old not in data_eddb['category']:
            resource_iri = row['@id']
            resource_type = 'Datacant:Category'
            last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
            body = body_delete_resource(resource_iri, resource_type, last_modification)
            delete_resource(body, token)
            keys_to_remove.append(eddb_id_old)
    for k in keys_to_remove:
        data_dasch['category'].pop(k)

    # Step 7: Save data in file.
    with open('data/data_dasch.json', 'w') as f:
        f.write(json.dumps(data_dasch, indent=4))
