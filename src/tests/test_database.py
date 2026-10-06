import unittest
import json
from database.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        pass

    def test_all_projects(self):
        projects = Database.all_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0], 'Datacant')


if __name__ == '__main__':
    unittest.main()
