# model list
model_quester_anster = "text-davinci-003"
model_gpt_35_turbo = "gpt-3.5-turbo"
model_programming_translate = "code-davinci-002"

# gpt key
openai_api_key = "your openai key"

# openai api
# openai_baseurl = "https://api.openai.com/v1"
openai_baseurl = "http://127.0.0.1:8089/v1"

# gpt model
# openai_model_name = model_gpt_35_turbo
# Use Llamafile
openai_model_name = "LLaMA_CPP"

# 2. Prompt
gpt_message = """
        You are a senior programming expert, and the branch code changes of gitlab will be provided in the form of a git diff string. Please help review this code. Then the return content of your review must strictly follow the following format, including the title content. The variable content explanation in the template: Variable 5 is the advantage in the code Variable 1 is the score for the review, the score range is 0~100 points. Variable 2 is the problem points found by the code review. Variable 3 is the specific modification suggestion. Variable 4 is the modified code you give.
        Requirements: 1. Point out the existing problems in concise language and strict tone. 2. Your feedback content must be in a rigorous markdown format 3. Do not carry variable content explanation information. 4. Have a clear title structure.
Return format is strictly as follows:
### 😀Code rating: {variable 1}

#### ✅Code advantages:
{variable 5}

#### 🤔Problem points:
{variable 2}

#### 🎯Modification suggestions:
{variable 3}

#### 💻Modified code:
```python
{variable 4}

"""

# -------------Gitlab info------------------
# Gitlab url
gitlab_server_url = "https://gitlab.com/"
WEBHOOK_VERIFY_TOKEN = "glpat-s8nz5-UknzG2FYaBx9cC"

# Gitlab private token
gitlab_private_token = WEBHOOK_VERIFY_TOKEN

# Gitlab modifies the maximum number of files
maximum_files = 50



