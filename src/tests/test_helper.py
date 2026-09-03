import unittest

from helper import is_before, text_to_xml


class TestHelper(unittest.TestCase):
    def setUp(self):
        # self.calc = Calculator()
        pass

    def test_is_before(self):
        a = '2026-07-13T12:18:57.506566376Z'
        b = '2026-02-20 13:37:26+00:00'
        self.assertFalse(is_before(a, a))
        self.assertFalse(is_before(a, b))
        self.assertTrue(is_before(b, a))
        self.assertFalse(is_before(b, b))

    def test_text_to_xml(self):
        text = ' Something '
        xml = text_to_xml(text)
        self.assertTrue(xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertTrue(xml.endswith('<text>Something</text>'))


if __name__ == '__main__':
    unittest.main()
