import concurrent.futures
import threading
import openai
from openai import OpenAIError
from app.gitlab_utils import *
from config.config import gitlab_server_url, gitlab_private_token, openai_api_key, openai_baseurl, openai_model_name
from service.content_handle import filter_diff_content
from utils.logger import log

headers = {
    "PRIVATE-TOKEN": gitlab_private_token,
}


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def post_comments(project_id, commit_id, content):
    """
    add comment for gitlab's commits
    :param project_id: gitlab peoject id
    :param commit_id: gitlab commit id
    :param content: comment info
    :return: None
    """
    data = {
        'note': content
    }
    comments_url = f'{gitlab_server_url}/api/v4/projects/{project_id}/repository/commits/{commit_id}/comments'
    response = requests.post(comments_url, headers=headers, json=data)
    log.debug(f"Request result: {response.json}")
    if response.status_code == 201:
        comment_data = response.json()
        log.info(f"Created comment successfully, comment ID is: {comment_data}")
    else:
        log.error(f"Request failed, Status code: {response.status_code}")


def wait_and_retry(exception):
    return isinstance(exception, OpenAIError)


@retry(retry_on_exception=wait_and_retry, stop_max_attempt_number=3, wait_fixed=60000)
def generate_review_note(change):
    try:
        content = filter_diff_content(change['diff'])
        openai.api_key = openai_api_key
        openai.api_base = openai_baseurl
        messages = [
            {"role": "system",
             "content": gpt_message
             },
            {"role": "user",
             "content": f"Please review this part of code change{content}",
             },
        ]
        log.info(f"Send to LLM, content is: {messages}")
        response = openai.ChatCompletion.create(
            model=openai_model_name,
            messages=messages,
        )
        new_path = change['new_path']
        log.info(f'Reviewing the: {new_path} ...')
        response_content = response['choices'][0]['message']['content'].replace('\n\n', '\n')
        total_tokens = response['usage']['total_tokens']
        review_note = f'# 📚`{new_path}`' + '\n\n'
        review_note += f'({total_tokens} tokens) {"LLM review got the result as following:"}' + '\n\n'
        review_note += response_content + """
    ----
    ----
    ----
    ----
    ----
    ----
    ----
        """
        log.info(f'Review {new_path} ends')
        return review_note
    except Exception as e:
        log.error(f"GPT error:{e}")


def chat_review(index, project_id, project_commit_id, content, context, merge_comment_info):
    log.info('Start code review')
    if index:
        review_info = f"\n# {index}.commit_id {project_commit_id} \n"
    else:
        log.info(f"🚚 mr_changes{content}")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        result_lock = threading.Lock()

        def process_input(val):
            result = generate_review_note(val)
            with result_lock:
                results.append(result)

        futures = []
        for change in content:
            if any(change["new_path"].endswith(ext) for ext in ['.py', '.java', '.class', '.vue', ".go"]) and not any(
                change["new_path"].endswith(ext) for ext in ["mod.go"]):
                futures.append(executor.submit(process_input, change))
            else:
                log.info(f"{change['new_path']} not the detection object target!")

        concurrent.futures.wait(futures)

    return "\n\n".join(results) if results else ""


# Code review for each commit
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def review_code(project_id, project_commit_id, merge_id, context):
    review_info = ""
    index = 0
    for commit_id in project_commit_id:
        index += 1
        url = f'{gitlab_server_url}/api/v4/projects/{project_id}/repository/commits/{commit_id}/diff'
        log.info(f"Start to request gitlab {url}   ,commit: {commit_id} diff info")

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            log.info(f"Start to process all requests: {content}")
            review_info += chat_review(index, project_id, commit_id, content, context, "")

        else:
            log.error(f"Request gitlab的{url}commit failed, Status code:{response.status_code}")
            raise Exception(f"请求gitlab的{url}commit失败, Status code:{response.status_code}")
    add_comment_to_mr(project_id, merge_id, review_info)


# CR for merge request
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def review_code_for_mr(project_id, merge_id, gitlab_message):
    # Get the modified file list of the diff branch
    changes = get_merge_request_changes(project_id, merge_id)
    log.info(changes)

    if changes and len(changes) <= maximum_files:
        # Code Review info
        review_info = chat_review("", project_id, "", changes, "", "")
        if review_info:
            add_comment_to_mr(project_id, merge_id, review_info)
            log.info("Already review")
        else:
            log.info("Do not have review_info")
    elif changes and len(changes) > maximum_files:
        log.info("Do not CR when the number of files is greater than 50")
    else:
        log.error(f"Get merge_request information failed, project_id:{project_id} | merge_id{merge_id}")
        raise Exception(f"Get merge_request information failed, project_id:{project_id} | merge_id{merge_id}")


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def review_code_for_add_commit(project_id, merge_id, commit_change_files, gitlab_message):
    """
    code review for gitlab commit
    :param project_id:
    :param merge_id:
    :param commit_change_files:
    :param gitlab_message:
    :return: 
    """
    if len(commit_change_files) > 50:
        log.info(f"gitlab_message:{gitlab_message['project']['name']} \n Note: (incremental commit) Modified files {len(commit_change_files)} > 50 files are not reviewed ⚠️ \n Branch name: {gitlab_message.get('ref')}")
        
    # Get the modified file list of the diff branch
    merge_change_files = get_merge_request_changes(project_id, merge_id)

    # Filter the files modified by the merge request based on the incremental commit modified file list
    change_files = [file_content for file_content in merge_change_files if
                    file_content["new_path"] in commit_change_files]

    log.info("😊incremental commit, modified the file list", change_files)
    if len(change_files) <= 50:
        review_info = chat_review("", project_id, "", change_files, "", "")
        if review_info:
            add_comment_to_mr(project_id, merge_id, review_info)
            log.info(f"project_name:{gitlab_message['project']['name']}\n Incremental commit, modified file count: {len(change_files)}\n Code review status: ✅")

    else:
        log.info(f"project_name:{gitlab_message['project']['name']}\n Note: (incremental commit) Modified files {len(change_files)} > 50 files are not reviewed ⚠️ \n Branch name: {gitlab_message.get('ref')}")



