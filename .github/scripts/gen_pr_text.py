import os, json, subprocess, requests

def sh(cmd):
    return subprocess.check_output(cmd, text=True).strip()

# 用 commit log + diff 生成 PR 描述（建议限制长度，避免 token 爆炸）
log = sh(["git", "log", "--oneline", "-20", "origin/main..HEAD"])
diff = sh(["git", "diff", "--stat", "origin/main...HEAD"])

prompt = f"""
你是企业级代码变更审阅助理，请为将 development 合入 main 的 PR 生成：
1) 简洁标题（<= 80 字）
2) 结构化描述：变更摘要、影响范围、风险点、回滚方案、需要重点 review 的文件
注意：只输出文本，不要生成代码，不要建议自动合并。

Commit log:
{log}

Diff stat:
{diff}
"""

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_KEY"]
deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01"
headers = {"Content-Type": "application/json", "api-key": api_key}
payload = {
    "messages": [
        {"role": "system", "content": "你是谨慎的企业 AI 助理，偏安全与可审计。"},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.2
}

r = requests.post(url, headers=headers, json=payload)
r.raise_for_status()
content = r.json()["choices"][0]["message"]["content"]

# 你可以让模型按 JSON 输出更稳定；这里为了简单做轻量解析
title = "Auto PR: development -> main"
body = content

print(json.dumps({"title": title, "body": body}, ensure_ascii=False))
