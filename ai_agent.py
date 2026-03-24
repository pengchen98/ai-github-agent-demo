import os
import subprocess
import requests

# 1. 获取和 main 的 diff
diff = subprocess.check_output(
    ["git", "diff", "origin/main...HEAD"],
    text=True
)

if not diff.strip():
    print("No code changes found.")
    exit(0)

prompt = f"""
你是一名资深软件架构师和安全审查员。

请审查以下 Git diff：
- 指出潜在 bug
- 指出安全或稳定性问题
- 给出改进建议
- 不要给出是否批准
- 不要生成代码

Diff:
{diff}
"""

# 2. 调用 Azure OpenAI
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
key = os.environ["AZURE_OPENAI_KEY"]
deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01"

response = requests.post(
    url,
    headers={
        "Content-Type": "application/json",
        "api-key": key
    },
    json={
        "messages": [
            {"role": "system", "content": "你是一个谨慎的企业 AI 审查代理。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
).json()

analysis = response["choices"][0]["message"]["content"]

# 3. 在 PR 中发表评论
repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
pr_number = os.environ["GITHUB_REF"].split("/")[-2]

comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

requests.post(
    comment_url,
    headers={"Authorization": f"token {token}"},
    json={"body": f"### 🤖 AI 自动代码审查意见\n\n{analysis}"}
)
