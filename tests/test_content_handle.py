import unittest
from service.content_handle import filter_diff_content

class TestContentHandle(unittest.TestCase):

    def test_filter_diff_content_remove_minus_and_at(self):
        diff_content = '-remove this line\n@@ remove this line too\nkeep this line'
        result = filter_diff_content(diff_content)
        self.assertEqual(result, 'keep this line')

    def test_filter_diff_content_remove_plus(self):
        diff_content = '+remove plus\nkeep this line'
        result = filter_diff_content(diff_content)
        self.assertEqual(result, 'remove plus\nkeep this line')

if __name__ == '__main__':
    unittest.main()