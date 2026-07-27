# Day 43: vLLM 服务安全与模型部署

> 部署与运维安全 | 第 7 周

## Demo: vLLM 安全部署实验：从默认配置到安全加固

部署 vLLM 推理服务，检查默认配置的安全风险，实施安全加固方案

- 难度：进阶
- 预计时间：2.5h

## 复现步骤

- 1. 部署 vLLM 基础服务
- 2. 检查默认端口/认证/API 风险
- 3. 实施 API 认证+速率限制
- 4. 配置 CORS 和日志
- 5. 安全加固验证

## 保姆教程

## vLLM 安全加固清单

### 1. 默认配置风险
\`\`\`bash
# 不安全的默认启动
python -m vllm.entrypoints.openai.api_server   --model meta-llama/Llama-2-7b-chat-hf
# 问题：无认证、无CORS限制、无速率限制、端口暴露
\`\`\`

### 2. 安全加固启动
\`\`\`bash
python -m vllm.entrypoints.openai.api_server   --model meta-llama/Llama-2-7b-chat-hf   --host 127.0.0.1 \           # 仅本地监听
  --port 8000 \                # 自定义端口
  --api-key sk-secure-key \    # 启用API Key认证
  --disable-log-requests \     # 不记录请求内容
  --max-num-batched-tokens 4096 \  # 限制批处理
  --max-model-len 4096         # 限制上下文长度
\`\`\`

### 3. Nginx 反向代理加固
\`\`\`nginx
server {
    listen 443 ssl;
    server_name llm.internal;

    ssl_certificate /etc/ssl/llm.crt;
    ssl_certificate_key /etc/ssl/llm.key;

    location /v1/ {
        # 速率限制
        limit_req zone=llm_limit burst=10 nodelay;
        # 仅允许内网
        allow 10.0.0.0/8;
        deny all;
        # 请求体大小限制
        client_max_body_size 1m;
        # 超时设置
        proxy_read_timeout 30s;
        proxy_pass http://127.0.0.1:8000;
    }
}
\`\`\`

### 4. 安全检查脚本
~~~python
import requests, sys

def check_vllm_security(url, api_key=None):
    issues = []
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # 1. 检查是否需要认证
    r = requests.get(f"{url}/v1/models", timeout=5)
    if r.status_code == 200 and not api_key:
        issues.append("HIGH: 无需认证即可访问API")

    # 2. 检查模型列表泄露
    if r.status_code == 200:
        models = r.json().get("data", [])
        if len(models) > 0:
            issues.append(f"MED: 模型列表泄露 ({len(models)}个模型)")

    # 3. 检查速率限制
    for _ in range(20):
        r = requests.post(f"{url}/v1/completions",
            json={"model":"test","prompt":"hi","max_tokens":1},
            headers=headers, timeout=5)
    if r.status_code == 200:
        issues.append("HIGH: 无速率限制，可被滥用")

    return issues

print("安全检查脚本已就绪")
print("运行: python check_security.py http://localhost:8000")
~~~

## 安全分析
vLLM 安全加固 = 监听限制+API认证+速率限制+反代+请求脱敏
