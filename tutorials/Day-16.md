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


## 真实案例：TGI 压测一上并发就崩，换 vLLM 后 QPS 翻 8 倍

**背景**：一个 FDE 用 HuggingFace TGI 部署 LLM 服务，单测没问题，但用 50 并发一压测，延迟从 1 秒飙到 30 秒、显存爆 OOM，服务直接 502。客户验收压测不过关。

**问题**：TGI 在高并发下显存碎片化严重，KV cache 分配不连续，并发一上来就 OOM、吞吐崩塌。生产场景不能靠"单测没问题"蒙混过关。

**定位过程**：他先用压测工具量化瓶颈——固定 50 并发跑 1 分钟，记录 QPS、p99 延迟、显存占用，确认是推理引擎并发能力而非模型本身的问题。
```python
# 压测脚本（locust 或简单 asyncio 并发）
import asyncio, aiohttp, time
async def one(session, i):
    async with session.post("http://localhost:8000/v1/chat/completions",
        json={"model":"qwen2-7b","messages":[{"role":"user","content":"你好"}]}) as r:
        await r.json()
async def main(n=50):
    async with aiohttp.ClientSession() as s:
        t=time.time()
        await asyncio.gather(*[one(s,i) for i in range(n)])
        print(f"50并发 QPS={n/(time.time()-t):.1f}")
asyncio.run(main())
# TGI: QPS≈12, p99=30s, 偶发OOM
```

**做法**：换 vLLM，靠 PagedAttention（分页管理 KV cache，消除显存碎片）+ 连续批处理（动态拼批），显著提升并发吞吐。
```bash
# vLLM 启动：开启 PagedAttention + 连续批处理
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2-7B-Instruct \
  --tensor-parallel-size 1 --max-model-len 4096 \
  --enable-prefix-caching          # 前缀缓存，重复 system prompt 提速
```
```python
# 同样压测对比
# vLLM: QPS≈96, p99=1.8s, 无OOM
```

**结果**：QPS 从 12 提到 96（8 倍），p99 延迟 30s → 1.8s，并发 50 无 OOM。客户压测通过验收。同样的 A100，换引擎吞吐翻 8 倍，相当于省了 7 张卡的硬件成本。

**踩坑**：他一开始只换引擎没调 `--max-model-len`，默认 32k 把显存吃光反而更易 OOM；按业务实际（对话最长 4k）设成 4096，显存留出余量给并发。还有 prefix caching 对"每轮都重发同一 system prompt"的多轮场景提速明显，但对全随机 prompt 没用——要按场景开。

**可复用经验**：部署 LLM 服务先压测再交付，别只做单测。高并发场景优先 vLLM（PagedAttention 解显存碎片 + 连续批处理提吞吐），按业务设 `max-model-len` 别用默认值。**同样的卡，换对引擎吞吐能差 8 倍**——这是 FDE 部署最值钱的一笔优化。

## 面试高频问答
问:vLLM 和 SGLang 怎么选?
答:vLLM 生态成熟、PagedAttention 稳定,适合通用部署;SGLang 在结构化生成和复杂程序上更快。通用场景 vLLM,复杂推理 SGLang。

## 简历话术
- ❌ 弱表述:了解推理引擎部署
- ✅ 强表述:部署 vLLM 推理服务,PagedAttention 优化 QPS 从 5 到 40;对比 SGLang 选型适配场景
vLLM 部署交付要点：API 认证 + 速率限制 + 输出过滤 + 日志审计 + 资源隔离，生产加反向代理做 TLS。

## 进阶挑战

1. 用 Docker Compose 部署 vLLM + nginx + Redis 做完整安全栈
2. 研究 vLLM 的 PagedAttention 对安全的影响
3. 实现 vLLM 的 Prometheus 指标导出

---

## 明日预告

**Day 17：流式输出：SSE 实时返回**
> 🟠 部署交付与生产化 · 第 4 周
