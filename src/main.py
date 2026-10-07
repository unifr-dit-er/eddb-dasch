from dotenv import load_dotenv
load_dotenv()

import hashlib
import json
import logging
import os
from pathlib import Path
from database.datacant import Datacant
from fetch import download_file, fetch_all_eddb
from models.category_model import Category
from models.decision_document import DecisionDocument
from models.decision_summary import DecisionSummary
from models.keyword_model import Keyword
import payload as pload


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(filename='data/app.log', level=logging.INFO)
    logger.info('Start the process!')

    USE_DASCH_CACHE = os.environ.get('USE_DASCH_CACHE') in ('true', 'True')

    db = Datacant('data/datacant')
    if not USE_DASCH_CACHE:
        db.build_dasch_cache()

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

    resource_types = db.resource_types()

    # Step 1: Handle the attachments.
    for key_in_db in resource_types:
        for eddb_id, object_eddb in data_eddb[key_in_db].items():
            object_dasch = data_dasch[key_in_db].get(eddb_id)
            attachment = object_eddb.file_field()
            if attachment is not None:
                is_new = object_dasch is None
                maybe_updated = attachment.is_updated(object_dasch)

                if is_new or maybe_updated:
                    # Download required.
                    filename = object_eddb.eddb_filename()
                    url_file = object_eddb.eddb_url_file()
                    download_file(url_file, filename)
                    path_to_file = Path('data/documents') / filename
                    with open(path_to_file, 'rb', buffering=0) as f:
                        checksum_new = hashlib.file_digest(f, 'sha256').hexdigest()
                        checksum_old = db.fetch_checksum(object_dasch)
                        is_upload_needed = checksum_new != checksum_old
                        filename_dasch = None
                        if is_upload_needed:
                            response = db.upload_to_ingest(filename)
                            filename_dasch = response['internalFilename']
                            attachment.set_value(filename_dasch)

    # Step 2: Update existing resources  or add new resources.
    for key_in_db in resource_types:
        for eddb_id, object_eddb in data_eddb[key_in_db].items():
            object_dasch = data_dasch[key_in_db].get(eddb_id)
            object_eddb.fill_iri_values(data_dasch)
            is_created = False
            is_updated = False
            if object_dasch is None:
                payload = object_eddb.payload_create()
                resource_id = db.create_resource(payload)
                is_created = True
                logger.info(f'Add new {key_in_db} (id={eddb_id})')
            else:
                # Maybe update existing category.
                payload_label = object_eddb.payload_update_label(object_dasch)
                if payload_label is not None:
                    response = db.update_label(payload_label)
                    logger.info(f'{key_in_db} (id={eddb_id}) label has been updated')

                payloads = object_eddb.payload_update_fields(data_dasch)
                for payload in payloads['updates']:
                    db.update_value(payload)
                for payload in payloads['add_values']:
                    db.create_value(payload)
                for payload in payloads['del_values']:
                    db.delete_value(payload)

                nb_field_change = sum(map(len, payloads.values()))
                is_updated = payload_label is not None or nb_field_change != 0
                if is_updated:
                    resource_id = object_dasch['@id']
                    logger.info(f'{key_in_db} (id={eddb_id}) field(s) have been updated')
            if is_created or is_updated:
                data_dasch[key_in_db][eddb_id] = db.fetch_resource(resource_id)

    # Step 3: Delete resources if not found in EDDB.
    resource_types.reverse()

    for resource_type in resource_types:
        keys_to_remove = []
        for eddb_id_old, row in data_dasch[resource_type].items():
            if eddb_id_old not in data_eddb[resource_type]:
                resource_iri = row['@id']
                last_modification = row.get('knora-api:lastModificationDate', {}).get('@value')
                body = pload.delete(resource_iri, resource_type, last_modification)
                db.delete_resource(body)
                keys_to_remove.append(eddb_id_old)
                logger.info(f'Delete {resource_type} (id={eddb_id_old})')
        for k in keys_to_remove:
            data_dasch[resource_type].pop(k)

    logger.info('Finished!')
