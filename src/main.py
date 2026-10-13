from dotenv import load_dotenv
load_dotenv()

from datetime import date, timedelta
import logging
import os
from database.datacant import Datacant
import payload as pload


logger = logging.getLogger(__name__)

NB_DAYS_LAST_INGESTION = 60


if __name__ == '__main__':
    logging.basicConfig(filename='data/app.log', level=logging.INFO)
    logger.info('Start the process!')

    USE_DASCH_CACHE = os.environ.get('USE_DASCH_CACHE') in ('true', 'True')

    db = Datacant('data/datacant')
    if not USE_DASCH_CACHE:
        db.build_dasch_cache()

    since = date.today() - timedelta(days=NB_DAYS_LAST_INGESTION)
    # since = '2000-01-01'
    db.build_eddb_cache(since)

    resource_types = db.resource_types()

    # Step 1: Handle the attachments.
    for key_in_db in resource_types:
        for eddb_id, object_eddb in db.get_eddb_items(key_in_db):
            object_dasch = db.get_dasch(key_in_db, eddb_id)
            attachment = object_eddb.file_field()
            if attachment is not None:
                is_new = object_dasch is None
                maybe_updated = attachment.is_updated(object_dasch)
                if is_new or maybe_updated:
                    filename = object_eddb.eddb_filename()
                    url_file = object_eddb.eddb_url_file()
                    db.download_file(url_file, filename)
                    if db.is_upload_needed(object_dasch, filename):
                        response = db.upload_to_ingest(filename)
                        filename_dasch = response['internalFilename']
                        attachment.set_value(filename_dasch)
                        db.overwrite_cache_eddb(object_eddb, key_in_db, eddb_id)

    # Step 2: Update existing resources  or add new resources.
    for key_in_db in resource_types:
        for eddb_id, object_eddb in db.get_eddb_items(key_in_db):
            object_dasch = db.get_dasch(key_in_db, eddb_id)
            db.fill_iri_values(object_eddb)
            is_created = False
            is_updated = False
            if object_dasch is None:
                payload = object_eddb.payload_create()
                resource_id = db.resource_create(payload)
                is_created = True
                logger.info(f'Add new {key_in_db} (id={eddb_id})')
            else:
                # Maybe update existing category.
                payload_label = object_eddb.payload_update_label(object_dasch)
                if payload_label is not None:
                    response = db.label_update(payload_label)
                    logger.info(f'{key_in_db} (id={eddb_id}) label has been updated')

                payloads = object_eddb.payload_update_fields(db)
                for payload in payloads['updates']:
                    db.value_update(payload)
                for payload in payloads['add_values']:
                    db.value_create(payload)
                for payload in payloads['del_values']:
                    db.value_delete(payload)

                nb_field_change = sum(map(len, payloads.values()))
                is_updated = payload_label is not None or nb_field_change != 0
                if is_updated:
                    resource_id = object_dasch['@id']
                    logger.info(f'{key_in_db} (id={eddb_id}) field(s) have been updated')
            if is_created or is_updated:
                object_dasch = db.fetch_resource(resource_id)
                db.overwrite_cache_dasch(object_dasch, key_in_db, eddb_id)

    # Step 3: Delete resources if not found in EDDB.
    resource_types.reverse()

    for resource_type in resource_types:
        for eddb_id_old, row in db.get_dasch_items(resource_type):
            if db.get_eddb(resource_type, eddb_id_old) is None:
                resource_iri = row['@id']
                last_modif = row.get('knora-api:lastModificationDate', {}).get('@value')
                body = pload.delete(resource_iri, resource_type, last_modif)
                db.resource_delete(resource_type, eddb_id_old, body)
                logger.info(f'Delete {resource_type} (id={eddb_id_old})')

    logger.info('Finished!')
