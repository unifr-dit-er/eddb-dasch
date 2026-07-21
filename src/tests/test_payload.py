import unittest

from payload import (
    body_delete_resource,
)


class TestHelper(unittest.TestCase):
    def setUp(self):
        # self.calc = Calculator()
        pass

    def test_body_delete_decision(self):
        iri = 'http://rdfh.ch/0750/QDxKoIdaQL2iWHITt1jmyg'
        resource_type = 'Datacant:Decisions'
        last_modification = '2019-02-05T17:05:35.776747Z'
        body = body_delete_resource(iri, resource_type, last_modification)
        self.assertEqual(body['@id'], iri)
        self.assertEqual(body['@type'], resource_type)


if __name__ == '__main__':
    unittest.main()
