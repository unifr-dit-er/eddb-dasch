# Datacant (0871): sync EDDB with DaSCH

Users work with EDDB to manage their data. This script syncs EDDB with DaSCH which is a repository for the long-term preservation and reuse of data in the humanities.

## General workflow

### Design the entities

As in SQL, the data model must define the entities and the relationships between them. These entities are called ressources in the context of DaSCH.

Once the structure of the data is defined, it is possible to export it into a json file:
```
dsp-tools get -P 0871 project_definition.json
```

### Interact with the database

Data is typically managed through the application's web-based user interface. In our case, however, a script is required because the data is already maintained in EDDB.

The implementation relies on both the API and Dsp-Tools. The API handles standard CRUD (Create, Read, Update, Delete) operations, while DSP-Tools is the recommended tool for uploading files.

### Syncing algorithm

Unfortunately, synchronization is not as straightforward as it may seem. Consider a keyword that has been deleted in EDDB. It cannot always be removed from the target system because it may still be referenced by an associated decision. As a result, a naive synchronization strategy that performs operations in a random order is not sufficient.

Fortunately, a valid stratgy is straightforward to implement:
1. Add new or update existing categories.
2. Add new or update existing keywords.
3. Add new or update existing decisions.
4. Delete decisions.
5. Delete keywords.
6. Delete categories.

## Getting started

Make sure Docker (not Podman) is installed. The library [Dsp-Tools](https://pypi.org/project/dsp-tools/) requires Python 3.12 or above.

Create a virtual environment:
```
virtualenv venv --python=python3.12
```

Then download the dependencies:
```
(venv) pip3 install -r requirements.txt
```

If the system is restarted, the containers must be started again.
```
docker start start-stack-app-1
docker start start-stack-ingest-1
docker start start-stack-db-1
docker start start-stack-api-1
docker start start-stack-sipi-1
```

## Reset a local instance of DaSCH

Shut down .
```
dsp-tools stop-stack
```

Import the project definition:
```
dsp-tools create project_definition.json
```

## Useful links

* https://docs.dasch.swiss/latest/
* https://api.dasch.swiss/api/docs/#/
