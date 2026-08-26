from dotenv import load_dotenv
load_dotenv()

import json
import logging
import os
from fetch import download_file, fetch_all_eddb
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
    upload_to_ingest,
)


USE_DASCH_CACHE = os.environ.get('USE_DASCH_CACHE') in ('true', 'True', 'TRUE')
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(filename='data/app.log', level=logging.INFO)
    logger.info('Start the process!')

    token = fetch_token()

    data_dasch = fetch_all_resources(token, use_cache=USE_DASCH_CACHE)
    with open('data/data_dasch.json', 'w') as f:
        f.write(json.dumps(data_dasch, indent=4))

    data_eddb = fetch_all_eddb(reset_cache=False)
    with open('data/eddb_categories.json', 'w') as f:
        tmp = {k: v.to_dict() for k, v in data_eddb['category'].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_keywords.json', 'w') as f:
        tmp = {k: v.to_dict() for k, v in data_eddb['keyword'].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_decisions.json', 'w') as f:
        tmp = {k: v.to_dict() for k, v in data_eddb['decision'].items()}
        f.write(json.dumps(tmp, indent=4))

    # Step 1: Update existing categories or add new categories.
    for cid, category_eddb in data_eddb['category'].items():
        category_dasch = data_dasch['category'].get(cid)
        is_created = False
        is_updated = False
        if category_dasch is None:
            logger.info(f'Add new category (id={cid})')
            payload = category_eddb.payload_create()
            resource_id = create_resource(payload, token)
            is_created = True
        else:
            # Maybe update existing category.
            payload_label = category_eddb.payload_update_label(category_dasch)
            if payload_label is not None:
                logger.info(f'Category (id={cid}) label has been updated')
                response = update_label(payload_label, token)

            payloads = category_eddb.payload_update_fields(data_dasch)
            (payload_updates, _, _) = payloads
            for payload in payload_updates:
                update_value(payload, token)

            is_updated = payload_label is not None or len(payload_updates) != 0
            if is_updated:
                resource_id = category_dasch['@id']
                logger.info(f'Category (id={cid}) field(s) have been updated')
        if is_created or is_updated:
            data_dasch['category'][cid] = fetch_resource(resource_id, token)

    # Step 2: Update existing keywords or add new keywords.
    for kid, keyword_eddb in data_eddb['keyword'].items():
        keyword_dasch = data_dasch['keyword'].get(kid)
        keyword_eddb.fill_iri_values(data_dasch)
        is_created = False
        is_updated = False
        if keyword_dasch is None:
            logger.info(f'Add new keyword (id={kid})')
            payload = keyword_eddb.payload_create()
            resource_id = create_resource(payload, token)
            is_created = True
        else:
            # Maybe update existing keyword.
            payload_label = keyword_eddb.payload_update_label(keyword_dasch)
            if payload_label is not None:
                logger.info(f'Keyword (id={kid}) label has been updated')
                response = update_label(payload_label, token)

            payloads = keyword_eddb.payload_update_fields(data_dasch)
            (payload_updates, _, _) = payloads
            for payload in payload_updates:
                update_value(payload, token)

            is_updated = payload_label is not None or len(payload_updates) != 0
            if is_updated:
                resource_id = keyword_dasch['@id']
                logger.info(f'keyword (id={kid}) field(s) have been updated')

        if is_created or is_updated:
            data_dasch['keyword'][kid] = fetch_resource(resource_id, token)

    # Step 3: Update existing decisions or add new decisions.
    for did, decision_eddb in data_eddb['decision'].items():
        decision_dasch = data_dasch['decision'].get(did)
        decision_eddb.fill_iri_values(data_dasch)
        is_created = False
        is_updated = False

        if decision_dasch is None:
            logger.info(f'Add new decision (id={did})')

            if decision_eddb.has_file_field():
                # Upload to ingest.
                filename = decision_eddb.eddb_filename()
                url_file = decision_eddb.eddb_url_file()
                download_file(url_file, filename)
                response = upload_to_ingest(filename, token)
                filename_tmp_dasch = response['internalFilename']
                decision_eddb.set_dasch_filename_tmp(filename_tmp_dasch)
                checksum = response['checksumOriginal']  # TODO

            # Create the resource.
            payload = decision_eddb.payload_create()
            resource_id = create_resource(payload, token)
            is_created = True
        else:
            # Maybe update existing decision.
            resource_id = decision_dasch['@id']
            payload_label = decision_eddb.payload_update_label(decision_dasch)
            if payload_label is not None:
                logger.info(f'Decision (id={did}) label has been updated')
                response = update_label(payload_label, token)

            payloads = decision_eddb.payload_update_fields(data_dasch)
            (payload_updates, payload_add, payload_del) = payloads
            for payload in payload_updates:
                update_value(payload, token)
            for payload in payload_add:
                create_value(payload, token)
            for payload in payload_del:
                delete_value(payload, token)

            is_updated = payload_label is not None or \
                len(payload_updates) != 0 or \
                len(payload_add) != 0 or \
                len(payload_del) != 0
            if is_updated:
                logger.info(f'Decision (id={did}) field(s) have been updated')

        if is_created or is_updated:
            logger.info(f'Decision (id={did}) has been updated')
            data_dasch['decision'][did] = fetch_resource(resource_id, token)

    # Step 4: Delete decisions.
    keys_to_remove = []
    for eddb_id_old, row in data_dasch['decision'].items():
        if eddb_id_old not in data_eddb['decision']:
            logger.info(f'Delete decision (id={eddb_id_old})')
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
            logger.info(f'Delete keyword (id={eddb_id_old})')
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
            logger.info(f'Delete category (id={eddb_id_old})')
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
    logger.info('Finished!')
