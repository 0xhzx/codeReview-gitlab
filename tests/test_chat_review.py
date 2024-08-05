import unittest
from unittest.mock import patch, Mock
from service.chat_review import (
    post_comments,
    generate_review_note,
    chat_review,
    review_code,
    review_code_for_mr,
    OpenAIError,
)

class TestChatReview(unittest.TestCase):
    @patch('service.chat_review.filter_diff_content', return_value='filtered content')
    @patch('service.chat_review.openai.ChatCompletion.create')
    def test_generate_review_note_success(self, mock_create, mock_filter):
        mock_create.return_value = {
            "choices": [{"message": {"content": "generated note"}}],
            "usage": {"total_tokens": 50}
        }
        change = {'diff': 'diff content', 'new_path': 'path/to/file.py'}
        result = generate_review_note(change)
        expected = result
        self.assertEqual(result, expected)

    @patch('service.chat_review.filter_diff_content', return_value='filtered content')
    @patch('service.chat_review.openai.ChatCompletion.create')
    def test_generate_review_note_openai_error(self, mock_create, mock_filter):
        mock_create.side_effect = OpenAIError("Error")
        change = {'diff': 'diff content', 'new_path': 'path/to/file.py'}
        result = generate_review_note(change)
        self.assertIsNone(result)

    @patch('service.chat_review.requests.post')
    def test_post_comments_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 123}
        post_comments(1, "abc123", "Test comment")
        mock_post.assert_called_once()

    @patch('service.chat_review.requests.post')
    def test_post_comments_failure(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.json.return_value = {"message": "error"}
        post_comments(1, "abc123", "Test comment")
        mock_post.assert_called_once()

    @patch('service.chat_review.get_merge_request_changes', return_value=[{'new_path': 'file.py'}])
    @patch('service.chat_review.chat_review', return_value='Review result')
    @patch('service.chat_review.add_comment_to_mr')
    def test_review_code_for_mr_success(self, mock_add_comment, mock_chat_review, mock_get_changes):
        review_code_for_mr(1, 1, "test message")
        mock_get_changes.assert_called_once()
        mock_chat_review.assert_called_once()
        mock_add_comment.assert_called_once_with(1, 1, 'Review result')

    @patch('service.chat_review.get_merge_request_changes')
    @patch('service.chat_review.requests.get')
    @patch('service.chat_review.chat_review', return_value='Review result')
    def test_review_code_success(self, mock_chat_review, mock_get, mock_get_changes):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{'new_path': 'file.py', 'diff': 'diff content'}]
        mock_get_changes.return_value = [{'new_path': 'file.py', 'diff': 'diff content'}]

        with patch('service.chat_review.add_comment_to_mr') as mock_add_comment:
            review_code(1, ['commit1'], 1, "context")
            mock_get.assert_called_once()
            mock_chat_review.assert_called_once()
            mock_add_comment.assert_called_once()

    @patch('service.chat_review.get_merge_request_changes')
    @patch('service.chat_review.requests.get')
    @patch('service.chat_review.chat_review')
    def test_review_code_failure(self, mock_chat_review, mock_get, mock_get_changes):
        mock_get.return_value.status_code = 403
        mock_get_changes.return_value = []

        with self.assertRaises(Exception) as context:
            review_code(1, ['commit1'], 1, "context")
        self.assertIn("Request gitlab的", str(context.exception))

if __name__ == '__main__':
    unittest.main()