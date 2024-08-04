import requests
from retrying import retry
from config.config import *
from utils.logger import log
from utils.dingding import send_dingtalk_message_by_sign

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_merge_request_id(branch_name, project_id):
    """
    Get the Merge Request ID for a branch in a GitLab project
    :param branch_name: The name of the branch
    :param project_id: The ID of the project
    :return: If the branch has an open MR, return the MR ID, otherwise return an empty string
    """
    # Concatenate the GitLab server URL, project ID, and branch name
    url = f"{gitlab_server_url}/api/v4/projects/{project_id}/merge_requests"

    params = {
        "source_branch": branch_name,
        "state": "opened"  # Can be opened, closed, locked, merged...
    }
    headers = {"Private-Token": gitlab_private_token}
    response = requests.get(url, params=params, headers=headers)

    # Parse the JSON response and check if there is a related Merge Request
    if response.status_code == 200:
        merge_requests = response.json()
        if len(merge_requests) > 0:
            log.info(f"Branch '{branch_name}' exists MR record.{merge_requests}")
            return merge_requests[0].get('iid')
        else:
            log.info(f"Branch '{branch_name}' has no unclosed MR.")
    else:
        log.error(f"Fetch branch'{branch_name}' failed! Status code: {response.status_code}")
    return None


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_commit_list(merge_request_iid, project_id):
    # Create API URL for the merge request commits
    api_url = f"{gitlab_server_url}/api/v4/projects/{project_id}/merge_requests/{merge_request_iid}/commits"
    # Set the private token in the header
    headers = {"PRIVATE-TOKEN": gitlab_private_token}

    # Make a GET request to the API URL
    response = requests.get(api_url, headers=headers)
    commit_list = []
    # If the response code is 200, the API call was successful
    if response.status_code == 200:
        # Get the commits from the response
        commits = response.json()
        # Iterate through the commits and print the commit ID and message
        for commit in commits:
            print(f"Commit ID: {commit['id']}, Message: {commit['message']}")
            # Append the commit ID to the list
            commit_list.append(commit['id'])
    else:
        # Log an error if the API call was unsuccessful
        log.error(f"Failed to fetch commits. Status code: {response.status_code}")
    # Return the list of commit IDs
    return commit_list


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_merge_request_changes(project_id, merge_id):
    # URL for the GitLab API endpoint
    url = f"{gitlab_server_url}/api/v4/projects/{project_id}/merge_requests/{merge_id}/changes"

    # Headers for the request
    headers = {
        "PRIVATE-TOKEN": gitlab_private_token
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["changes"]
    else:
        return None


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def add_comment_to_mr(project_id, merge_request_id, comment):
    """
    Add comments to GitLab's Merge Request

    :param gitlab_url: GitLab base URL
    :param project_id: Project ID
    :param merge_request_id: Merge Request ID
    :param token: GitLab的API token
    :param comment: The comment to be added
    :return: Response JSON
    """
    headers = {
        "Private-Token": gitlab_private_token,
        "Content-Type": "application/json"
    }

    url = f"{gitlab_server_url}/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes"
    data = {
        "body": comment
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        log.info(f"Comment message sent successfully: project_id:{project_id}  merge_request_id:{merge_request_id}")
        return response.json()
    else:
        log.error(f"Comment message sent successfully: project_id:{project_id}  merge_request_id:{merge_request_id} response:{response}")
        send_dingtalk_message_by_sign(f"Comment message sent successfully: project_id:{project_id}  merge_request_id:{merge_request_id} response:{response}")
        response.raise_for_status()



@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_mr_comment_info(project_id, mr_iid, ):
    url = f"{gitlab_server_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"

    # Add the private token in the header
    headers = {"Private-Token": gitlab_private_token}
    response = requests.get(url, headers=headers)

    comments_info = ""
    if response.status_code == 200:
        comments = response.json()
        for comment in comments:
            author = comment['author']['username']
            comment_text = comment['body']
            print(f"Author: {author}")
            print(f"Comment: {comment_text}")
            comments_info += comment_text

    else:
        print(f" Fetch mr comment failed, Status code: {response.status_code}")
    return comments_info


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_commit_change_file(push_info):
    commits = push_info['commits']
    add_file = []
    modify_file = []
    # Get the added and modified files for each commit
    for commit in commits:
        added_files = commit.get('added', [])
        modified_files = commit.get('modified', [])
        add_file += added_files
        modify_file += modified_files

    return add_file + modify_file
