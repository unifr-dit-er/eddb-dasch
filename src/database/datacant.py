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

    def resource_types(self):
        return [
            Category.resource_type(),
            Keyword.resource_type(),
            DecisionDocument.resource_type(),
            DecisionSummary.resource_type(),
        ]
