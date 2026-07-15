import unittest

from helper import (
    body_delete_resource,
    is_before,
    is_class_category,
    is_class_decision,
    is_class_keyword
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

    def test_check_class(self):
        self.assertTrue(is_class_category({'@type': 'Datacant:Category'}))
        self.assertFalse(is_class_category({'@type': 'Datacant:Decisions'}))

        self.assertTrue(is_class_decision({'@type': 'Datacant:Decisions'}))
        self.assertFalse(is_class_decision({'@type': 'Datacant:Keyword'}))

        self.assertTrue(is_class_keyword({'@type': 'Datacant:Keyword'}))
        self.assertFalse(is_class_keyword({'@type': 'Datacant:Category'}))

    def test_is_before(self):
        a = '2026-07-13T12:18:57.506566376Z'
        b = '2026-02-20 13:37:26+00:00'
        self.assertFalse(is_before(a, a))
        self.assertFalse(is_before(a, b))
        self.assertTrue(is_before(b, a))
        self.assertFalse(is_before(b, b))


if __name__ == '__main__':
    unittest.main()
