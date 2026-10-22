import unittest

from helper import markdown_to_dasch_xml


class TestHelper(unittest.TestCase):
    def setUp(self):
        pass

    def test_markdown_to_dasch_xml(self):
        text = '# Title\nSomething **important** because'
        xml = markdown_to_dasch_xml(text)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
            '<text><h1>Title</h1>\n' + \
            '<p>Something <strong>important</strong> because</p></text>'
        self.assertEqual(xml, expected)


if __name__ == '__main__':
    unittest.main()
