import unittest
from fields.datacant import (
    EddbId,
    NameDe,
    NameFr,
)


class TestDatacantFields(unittest.TestCase):
    def setUp(self):
        pass

    def test_eddb_id(self):
        field = EddbId(1)
        self.assertEqual(field.name, 'Datacant:hasId')
        self.assertEqual(field.value, 1)

    def test_eddb_id_fail(self):
        with self.assertRaises(TypeError):
            EddbId('1')
        with self.assertRaises(ValueError):
            EddbId(-3)

    def test_name_de(self):
        field = NameDe(' Schuldbetreibung und Konkurs ')
        self.assertEqual(field.name, 'Datacant:hasNameDe')
        self.assertEqual(field.value, 'Schuldbetreibung und Konkurs')

    def test_name_de_fail(self):
        with self.assertRaises(ValueError):
            NameDe(' ')
        with self.assertRaises(ValueError):
            NameDe(None)

    def test_name_fr(self):
        field = NameFr(' Poursuite pour dette et faillite ')
        self.assertEqual(field.name, 'Datacant:hasNameFr')
        self.assertEqual(field.value, 'Poursuite pour dette et faillite')

    def test_name_fr_fail(self):
        with self.assertRaises(ValueError):
            NameFr(' ')
        with self.assertRaises(ValueError):
            NameFr(None)


if __name__ == '__main__':
    unittest.main()
