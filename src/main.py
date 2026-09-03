from dotenv import load_dotenv
load_dotenv()

import json
import logging
import os
from fetch import download_file, fetch_all_eddb
from models.decision_document import DecisionDocument
from models.decision_summary import DecisionSummary
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
    with open('data/eddb_decisions_document.json', 'w') as f:
        key = DecisionDocument.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_decisions_summary.json', 'w') as f:
        key = DecisionSummary.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))

    # Step 0: Download new files.

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

    # Step 3: Update existing decisions document or add new documents.
    key_in_db = DecisionDocument.resource_type()
    for did, decision_eddb in data_eddb[key_in_db].items():
        decision_dasch = data_dasch[key_in_db].get(did)
        decision_eddb.fill_iri_values(data_dasch)
        is_created = False
        is_updated = False

        if decision_dasch is None:
            logger.info(f'Add new DecisionDoc (id={did})')

            if decision_eddb.has_attachment_field():
                # Upload to ingest.
                # TODO move the download to fetch.py
                filename = decision_eddb.eddb_filename()
                url_file = decision_eddb.eddb_url_file()
                download_file(url_file, filename)
                response = upload_to_ingest(filename, token)
                filename_dasch = response['internalFilename']
                checksum = response['checksumOriginal']
                decision_eddb.set_attachment(url_file, filename_dasch, checksum)

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

            # TODO: add a special bloc to compare

            payloads = decision_eddb.payload_update_fields(data_dasch)
            (payload_updates, _, _) = payloads
            for payload in payload_updates:
                update_value(payload, token)

            is_updated = payload_label is not None or len(payload_updates) != 0
            if is_updated:
                logger.info(f'DecisionDoc (id={did}) field(s) have been updated')

        if is_created or is_updated:
            logger.info(f'DecisionDocument (id={did}) has been updated')
            data_dasch['Datacant:DecisionDocument'][did] = fetch_resource(resource_id, token)

    # Step 4: Update existing decisions summary or add new summaries.
    # for did, decision_eddb in data_eddb['decision_summary'].items():
    #     decision_dasch = data_dasch['Datacant:DecisionSummary'].get(did)
    #     decision_eddb.fill_iri_values(data_dasch)
    #     is_created = False
    #     is_updated = False

    #     if decision_dasch is None:
    #         logger.info(f'Add new DecisionSummary (id={did})')

    #         # Create the resource.
    #         payload = decision_eddb.payload_create()
    #         resource_id = create_resource(payload, token)
    #         is_created = True
    #     else:
    #         # Maybe update existing decision.
    #         resource_id = decision_dasch['@id']
    #         payload_label = decision_eddb.payload_update_label(decision_dasch)
    #         if payload_label is not None:
    #             logger.info(f'DecisionSummary (id={did}) label has been updated')
    #             response = update_label(payload_label, token)

    #         payloads = decision_eddb.payload_update_fields(data_dasch)
    #         (payload_updates, payload_add, payload_del) = payloads
    #         for payload in payload_updates:
    #             update_value(payload, token)
    #         for payload in payload_add:
    #             create_value(payload, token)
    #         for payload in payload_del:
    #             delete_value(payload, token)

    #         is_updated = payload_label is not None or \
    #             len(payload_updates) != 0 or \
    #             len(payload_add) != 0 or \
    #             len(payload_del) != 0
    #         if is_updated:
    #             logger.info(f'DecisionSummary (id={did}) field(s) have been updated')

    #     if is_created or is_updated:
    #         logger.info(f'DecisionSummary (id={did}) has been updated')
    #         data_dasch['Datacant:DecisionSummary'][did] = fetch_resource(resource_id, token)

    # Step 5: Delete decisions summary.
    keys_to_remove = []
    resource_type = 'Datacant:DecisionSummary'
    for eddb_id_old, row in data_dasch[resource_type].items():
        if eddb_id_old not in data_eddb[resource_type]:
            logger.info(f'Delete decision summary (id={eddb_id_old})')
            resource_iri = row['@id']
            last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
            body = body_delete_resource(resource_iri, resource_type, last_modification)
            delete_resource(body, token)
            keys_to_remove.append(eddb_id_old)
    for k in keys_to_remove:
        data_dasch[resource_type].pop(k)

    # Step 6: Delete decisions document.
    keys_to_remove = []
    resource_type = 'Datacant:DecisionDocument'
    for eddb_id_old, row in data_dasch[resource_type].items():
        if eddb_id_old not in data_eddb[resource_type]:
            logger.info(f'Delete decision document (id={eddb_id_old})')
            resource_iri = row['@id']
            last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
            body = body_delete_resource(resource_iri, resource_type, last_modification)
            delete_resource(body, token)
            keys_to_remove.append(eddb_id_old)
    for k in keys_to_remove:
        data_dasch[resource_type].pop(k)

    # Step 7: Delete keywords.
    keys_to_remove = []
    resource_type = 'Datacant:Keyword'
    for eddb_id_old, row in data_dasch['keyword'].items():
        if eddb_id_old not in data_eddb['keyword']:
            logger.info(f'Delete keyword (id={eddb_id_old})')
            resource_iri = row['@id']
            last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
            body = body_delete_resource(resource_iri, resource_type, last_modification)
            delete_resource(body, token)
            keys_to_remove.append(eddb_id_old)
    for k in keys_to_remove:
        data_dasch['keyword'].pop(k)

    # Step 8: Delete categories.
    keys_to_remove = []
    resource_type = 'Datacant:Category'
    for eddb_id_old, row in data_dasch['category'].items():
        if eddb_id_old not in data_eddb['category']:
            logger.info(f'Delete category (id={eddb_id_old})')
            resource_iri = row['@id']
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
