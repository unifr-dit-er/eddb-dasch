import unittest

from helper import text_to_xml


class TestHelper(unittest.TestCase):
    def setUp(self):
        pass

    def test_text_to_xml(self):
        text = ' Something '
        xml = text_to_xml(text)
        self.assertTrue(xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertTrue(xml.endswith('<text>Something</text>'))


if __name__ == '__main__':
    unittest.main()
