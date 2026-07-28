# Day 16：推理引擎部署：vLLM 与 SGLang

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-16.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-16.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 vLLM/SGLang 推理引擎的工作原理与部署架构
2. 掌握 LLM 服务部署：从零搭建可交付的推理 API
3. 理解 PagedAttention/连续批处理等推理优化

## 推荐资料

- 📚 文档 [vLLM 官方文档](https://docs.vllm.ai/)
- 📚 文档 [SGLang 官方文档](https://docs.sglang.ai/)
- 📚 文档 [HuggingFace TGI 文档](https://huggingface.co/docs/text-generation-inference/en/)

## Demo 练习：vLLM 服务搭建 + SGLang 对比

vLLM 是推理部署的事实标准。从零起一个 vLLM 服务，对比 SGLang——JD 明确要求 vLLM/SGLang，部署岗必考。

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 了解 vLLM 默认配置的安全风险
2. 实现 API Key 认证和速率限制
3. 配置模型访问控制和输出过滤
4. 实现日志审计和监控

## 保姆教程

## 环境准备
```bash
# 安装 vLLM（需要 GPU）
pip install vllm
# 或用 Docker: docker run --gpus all vllm/vllm-openai:latest --model meta-llama/Llama-2-7b-chat-hf
```

## 原理速览
vLLM = 高性能 LLM 推理引擎，兼容 OpenAI API。
默认配置的安全风险：
1. 无认证：任何人都能访问 API
2. 无速率限制：容易被 DDoS
3. 无输出过滤：可能输出有害内容
4. 日志不足：无法追溯攻击

## 配置对比

### 不安全配置（默认）
```bash
# ❌ 不安全：无认证、无限流、无日志
python -m vllm.entrypoints.openai.api_server   --model meta-llama/Llama-2-7b-chat-hf   --port 8000
```

### 安全配置（加固后）
```bash
# ✅ 安全：认证 + 限流 + 过滤 + 日志
python -m vllm.entrypoints.openai.api_server   --model meta-llama/Llama-2-7b-chat-hf   --port 8000   --api-key YOUR_SECURE_API_KEY   --max-num-seqs 64   --max-model-len 4096   --disable-log-requests   --chat-template ./safe_template.jinja
```

## 代码：安全配置验证脚本
```python
import requests, json, subprocess, time

VLLM_URL = "http://localhost:8000"
API_KEY = "YOUR_SECURE_API_KEY"

def check_security_config():
    """检查 vLLM 实例的安全配置"""
    checks = []

    # 1. 认证检查
    try:
        r = requests.post(f"{VLLM_URL}/v1/chat/completions",
                         json={"model": "meta-llama/Llama-2-7b-chat-hf",
                               "messages": [{"role": "user", "content": "hi"}]})
        if r.status_code == 401:
            checks.append(("API Auth", True, "Unauthorized without key"))
        else:
            checks.append(("API Auth", False, f"No auth required (status={r.status_code})"))
    except:
        checks.append(("API Auth", False, "Cannot connect"))

    # 2. 带认证的请求
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        r = requests.post(f"{VLLM_URL}/v1/chat/completions",
                         headers=headers,
                         json={"model": "meta-llama/Llama-2-7b-chat-hf",
                               "messages": [{"role": "user", "content": "hi"}],
                               "max_tokens": 10})
        checks.append(("API Call", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        checks.append(("API Call", False, str(e)[:50]))

    # 3. 速率限制检查
    responses = []
    for i in range(20):
        r = requests.post(f"{VLLM_URL}/v1/chat/completions",
                         headers=headers,
                         json={"model": "meta-llama/Llama-2-7b-chat-hf",
                               "messages": [{"role": "user", "content": "hi"}],
                               "max_tokens": 5})
        responses.append(r.status_code)
    unique = set(responses)
    if 429 in unique:
        checks.append(("Rate Limit", True, "429 returned"))
    else:
        checks.append(("Rate Limit", False, "No rate limiting"))

    # 4. 模型信息泄露
    try:
        r = requests.get(f"{VLLM_URL}/v1/models", headers=headers)
        models = r.json()
        if "data" in models and len(models["data"]) > 0:
            checks.append(("Model Info", False, f"Model list exposed: {[m['id'] for m in models['data']]}"))
        else:
            checks.append(("Model Info", True, "Model list hidden"))
    except:
        checks.append(("Model Info", True, "Cannot access"))

    print("=== vLLM Security Config Check ===
")
    for name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status:4s}] {name:15s} {detail}")

# 运行检查（需要 vLLM 在 localhost:8000 运行）
# check_security_config()
```

## 安全分析
vLLM 部署交付要点：API 认证 + 速率限制 + 输出过滤 + 日志审计 + 资源隔离，生产加反向代理做 TLS。

## 进阶挑战

1. 用 Docker Compose 部署 vLLM + nginx + Redis 做完整安全栈
2. 研究 vLLM 的 PagedAttention 对安全的影响
3. 实现 vLLM 的 Prometheus 指标导出

---

## 明日预告

**Day 17：流式输出：SSE 实时返回**
> 🟠 部署交付与生产化 · 第 4 周
