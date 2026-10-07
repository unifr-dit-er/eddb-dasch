from database.database import Database
from models.category_model import Category
from models.decision_document import DecisionDocument
from models.decision_summary import DecisionSummary
from models.keyword_model import Keyword


PROJECT_NUMBER = '0871'


class Datacant(Database):

    def __init__(self, directory):
        '''Initialization of the fields.'''
        Database.__init__(self, directory, PROJECT_NUMBER)

    def build_eddb_cache(self):
        pass

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
        raise NotImplementedError()

    def get_eddb_items(self, resource_type):
        raise NotImplementedError()

    def resource_types(self):
        return [
            Category.resource_type(),
            Keyword.resource_type(),
            DecisionDocument.resource_type(),
            DecisionSummary.resource_type(),
        ]
