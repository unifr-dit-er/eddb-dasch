from dotenv import load_dotenv
load_dotenv()

import hashlib
import json
import logging
import os
from pathlib import Path
from fetch import download_file, fetch_all_eddb
from models.category_model import Category
from models.decision_document import DecisionDocument
from models.decision_summary import DecisionSummary
from models.keyword_model import Keyword
import payload as pload
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
        key = Category.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_keywords.json', 'w') as f:
        key = Keyword.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_decisions_document.json', 'w') as f:
        key = DecisionDocument.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))
    with open('data/eddb_decisions_summary.json', 'w') as f:
        key = DecisionSummary.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))

    # Step 1: Handle the attachments.
    key_in_db = DecisionDocument.resource_type()
    for did, doc_eddb in data_eddb[key_in_db].items():
        doc_dasch = data_dasch[key_in_db].get(did)

        is_new = doc_dasch is None
        maybe_updated = doc_eddb.attachment.is_updated(doc_dasch)

        if is_new or maybe_updated:
            # Download required.
            filename = doc_eddb.eddb_filename()
            url_file = doc_eddb.eddb_url_file()
            download_file(url_file, filename)
            path_to_file = Path('data/documents') / filename
            with open(path_to_file, 'rb', buffering=0) as f:
                checksum = hashlib.file_digest(f, 'sha256').hexdigest()
                same_checksum = checksum == doc_dasch \
                    .get('Datacant:hasChecksum', {}) \
                    .get('knora-api:valueAsString')
                filename_dasch = None
                if not same_checksum:
                    response = upload_to_ingest(filename, token)
                    filename_dasch = response['internalFilename']
                doc_eddb.attachment.set_value(url_file, filename_dasch, checksum)

    resource_types = [
        Category.resource_type(),
        Keyword.resource_type(),
        DecisionDocument.resource_type(),
        # DecisionSummary.resource_type(),
    ]

    # Step 2: Update existing resources  or add new resources.
    for key_in_db in resource_types:
        for eddb_id, object_eddb in data_eddb[key_in_db].items():
            object_dasch = data_dasch[key_in_db].get(eddb_id)
            object_eddb.fill_iri_values(data_dasch)
            is_created = False
            is_updated = False
            if object_dasch is None:
                logger.info(f'Add new {key_in_db} (id={eddb_id})')
                payload = object_eddb.payload_create()
                resource_id = create_resource(payload, token)
                is_created = True
            else:
                # Maybe update existing category.
                payload_label = object_eddb.payload_update_label(object_dasch)
                if payload_label is not None:
                    logger.info(f'{key_in_db} (id={eddb_id}) label has been updated')
                    response = update_label(payload_label, token)

                # TODO: add a special bloc to compare attachment.

                payloads = object_eddb.payload_update_fields(data_dasch)
                (payload_updates, _, _) = payloads
                for payload in payload_updates:
                    update_value(payload, token)

                is_updated = payload_label is not None or len(payload_updates) != 0
                if is_updated:
                    resource_id = object_dasch['@id']
                    logger.info(f'{key_in_db} (id={eddb_id}) field(s) have been updated')
            if is_created or is_updated:
                data_dasch[key_in_db][eddb_id] = fetch_resource(resource_id, token)

    # Step 4: Update existing decisions summary or add new summaries.
    key_in_db = DecisionSummary.resource_type()
    for did, decision_eddb in data_eddb[key_in_db].items():
        decision_dasch = data_dasch[key_in_db].get(did)
        decision_eddb.fill_iri_values(data_dasch)
        is_created = False
        is_updated = False

        if decision_dasch is None:
            logger.info(f'Add new DecisionSummary (id={did})')

            # Create the resource.
            payload = decision_eddb.payload_create()
            resource_id = create_resource(payload, token)
            is_created = True
        else:
            # Maybe update existing decision.
            resource_id = decision_dasch['@id']
            payload_label = decision_eddb.payload_update_label(decision_dasch)
            if payload_label is not None:
                logger.info(f'DecisionSummary (id={did}) label has been updated')
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
                logger.info(f'DecisionSummary (id={did}) field(s) have been updated')

        if is_created or is_updated:
            data_dasch[key_in_db][did] = fetch_resource(resource_id, token)

    # Step 5: Delete resources if not found in EDDB.
    resource_types = [
        DecisionSummary.resource_type(),
        DecisionDocument.resource_type(),
        Keyword.resource_type(),
        Category.resource_type(),
    ]
    for resource_type in resource_types:
        keys_to_remove = []
        for eddb_id_old, row in data_dasch[resource_type].items():
            if eddb_id_old not in data_eddb[resource_type]:
                logger.info(f'Delete {resource_type} (id={eddb_id_old})')
                resource_iri = row['@id']
                last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
                body = pload.delete(resource_iri, resource_type, last_modification)
                delete_resource(body, token)
                keys_to_remove.append(eddb_id_old)
        for k in keys_to_remove:
            data_dasch[resource_type].pop(k)

    # Step 7: Save data in file.
    with open('data/data_dasch.json', 'w') as f:
        f.write(json.dumps(data_dasch, indent=4))
    with open('data/eddb_decisions_document.json', 'w') as f:
        key = DecisionDocument.resource_type()
        tmp = {k: v.to_dict() for k, v in data_eddb[key].items()}
        f.write(json.dumps(tmp, indent=4))
    logger.info('Finished!')
