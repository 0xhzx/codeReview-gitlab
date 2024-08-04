import json
import threading
from os import abort
from flask import Blueprint, request, jsonify
from config.config import WEBHOOK_VERIFY_TOKEN
from service.chat_review import review_code, review_code_for_mr, review_code_for_add_commit
from utils.logger import log
from app.gitlab_utils import get_commit_list, get_merge_request_id, get_commit_change_file

git = Blueprint('git', __name__)


@git.route('/api')
def question():
    return 'hello world'


@git.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Get the token from the header of the Gitlab request
        verify_token = request.headers.get('X-Gitlab-Token')

        # gitlab webhook token verification
        if verify_token == WEBHOOK_VERIFY_TOKEN:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'bad token'}), 401

    elif request.method == 'POST':
        """
        The main logic of the webhook, get the push information of gitlab
        """
        gitlab_message = request.data.decode('utf-8')
        gitlab_message = json.loads(gitlab_message)
        log.info(f"🌈 : {gitlab_message}")
        object_kind = gitlab_message.get('object_kind')

        # Triggered when the merge request is first initiated
        if object_kind == 'merge_request' and gitlab_message.get("object_attributes").get(
            "state") == "opened" and gitlab_message.get("object_attributes").get("merge_status") == "checking":
            # Pass the verification and get the commit information
            log.info("首次merge_request ", gitlab_message)
            project_id = gitlab_message.get('project')['id']
            merge_id = gitlab_message.get("object_attributes")["iid"]

            thread = threading.Thread(target=review_code_for_mr, args=(project_id, merge_id, gitlab_message))
            thread.start()

            return jsonify({'status': 'success'}), 200
        elif object_kind == 'push':
            merge_id = get_merge_request_id(gitlab_message.get('ref').split("/")[-1], gitlab_message.get("project_id"))
            project_id = gitlab_message.get('project')['id']
            if not merge_id:
                return jsonify({'status': f'非存在MR分支,{gitlab_message}'}), 200
            change_files = get_commit_change_file(gitlab_message)
            thread = threading.Thread(target=review_code_for_add_commit,
                                      args=(project_id, merge_id, change_files, gitlab_message))
            thread.start()
            return jsonify({'status': 'success'}), 200

        else:
            log.error("Not merge")
            # return jsonify({'status': 'Operation is not push'}), 200
            return jsonify({'status': f'No match rules,{gitlab_message}'}), 200

    else:
        abort(400)

