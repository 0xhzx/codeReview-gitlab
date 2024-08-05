import unittest
from unittest.mock import patch, Mock
from service.get_url_raw import get_gitlab_file_content

class TestURLServices(unittest.TestCase):

    @patch('requests.get')
    def test_get_gitlab_file_content_success(self, mock_get):
        mock_resp_instance = Mock()
        mock_resp_instance.status_code = 200
        mock_resp_instance.text = 'file content'
        mock_get.return_value = mock_resp_instance

        result = get_gitlab_file_content('project_id', 'file_path', 'version')
        self.assertEqual(result, 'file content')

    @patch('requests.get')
    def test_get_gitlab_file_content_failure(self, mock_get):
        mock_resp_instance = Mock()
        mock_resp_instance.status_code = 404
        mock_get.return_value = mock_resp_instance

        result = get_gitlab_file_content('project_id', 'file_path', 'version')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()