# Day 21：第四周实战：生产级 LLM 服务部署

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-21.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-21.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 整合本周所学：部署+流式+容器+K8s+监控+优化，交付生产级服务
2. 构建一个可交付的 LLM 服务骨架（FastAPI+流式+缓存+监控）
3. 输出交付清单：从部署到运维的一站式交付物

## 推荐资料

- 📚 文档 [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- 📚 文档 [Docker Compose 部署](https://docs.docker.com/compose/)
- 📄 文章 [LangChain 生产部署指南](https://python.langchain.com/docs/tutorials/rag/)

## Demo 练习：生产级 LLM 服务骨架（FastAPI+流式+缓存+监控）

第四周收尾：一套生产级 LLM 服务骨架(FastAPI+流式+缓存+监控)。这是你能直接交付、面试演示的完整后端。

| 难度 | 预计时间 |
|------|----------|
| 项目 | 3h |

### 复现步骤

1. FastAPI 服务：/chat /stream /metrics 三个端点
2. 集成语义缓存 + 用量统计 + 健康检查
3. 输出 docker-compose 一键部署与交付清单

## 保姆教程

## 原理速览
W4 收口：把你这周学的部署/流式/容器/监控/优化拼成一个可交付的生产级服务。
这是 FDE 的'交付单元'——客户拿到这个，能跑、能监控、能算成本、能扩展。

## 代码
```python
# llm_service.py —— 生产级 LLM 服务骨架
# 安装: pip install fastapi uvicorn prometheus-client
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time, json
from collections import defaultdict

app = FastAPI(title="FDE LLM 服务")

# 缓存 + 监控
cache = {}
metrics = {"requests":0, "tokens":0, "cache_hits":0, "latency":[]}

def llm_generate(prompt):
    return f"基于'{prompt}'的专业回答（mock）"

@app.get("/health")
def health():
    return {"status":"ok", "cache_size":len(cache), "req":metrics["requests"]}

@app.post("/chat")
def chat(prompt: str):
    metrics["requests"] += 1
    t0 = time.time()
    key = prompt[:50]
    if key in cache:
        metrics["cache_hits"] += 1
        return {"answer": cache[key], "cached": True}
    ans = llm_generate(prompt)
    cache[key] = ans
    metrics["latency"].append((time.time()-t0)*1000)
    metrics["tokens"] += len(prompt)
    return {"answer": ans, "cached": False}

@app.get("/stream")
def stream(prompt: str):
    """流式输出"""
    def gen():
        for ch in llm_generate(prompt):
            yield json.dumps({"token": ch})
            time.sleep(0.02)
    return StreamingResponse(gen(), media_type="application/json")

@app.get("/metrics")
def get_metrics():
    lat = sorted(metrics["latency"])
    p99 = lat[int(len(lat)*0.99)] if lat else 0
    return {
        "requests": metrics["requests"],
        "cache_hits": metrics["cache_hits"],
        "hit_rate": metrics["cache_hits"]/max(metrics["requests"],1),
        "p99_ms": p99,
    }

# 启动: uvicorn llm_service:app --host 0.0.0.0 --port 8000
# 一键部署: docker-compose up（见下方）
```
```yaml
# docker-compose.yml
services:
  llm:
    build: .
    ports: ["8000:8000"]
    environment: [MODEL=gpt-4o-mini]
    healthcheck: {test: ["CMD","curl","-f","http://localhost:8000/health"]}
    deploy: {resources: {limits: {memory: 2g}}}
  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
```
上线必带：API认证+速率限制+输出过滤+审计日志+资源限制（详见W5安全周）。
生产服务上线前必做：API 认证（无 key 不让调）、速率限制（防刷爆）、
输出过滤（拦敏感内容）、审计日志（合规追溯）、资源限制（OOM 防护）。
这些在 W5 安全周会系统讲，但交付时至少要带上认证与限流。

## 进阶挑战

1. 接入真实 vLLM 后端替换 mock，跑通端到端推理
2. 加 API Key 认证中间件 + 令牌桶限流
3. 用 docker-compose 一键起 服务+Prometheus+Grafana，截图作为交付物

---

## 明日预告

**Day 22：Prompt Injection 与 API 安全攻防**
> 🔴 AI 安全攻防（差异化能力） · 第 5 周
