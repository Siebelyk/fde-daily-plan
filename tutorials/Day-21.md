# Day 21：第四周实战：生产级 LLM 服务

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-21.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-21.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 整合本周所学：部署+流式+容器+K8s+监控+优化，交付生产级服务
2. 构建一个可交付的 LLM 服务骨架（FastAPI+流式+缓存+监控）
3. 输出交付清单：从部署到运维的一站式交付物

## 推荐资料

- 📚 文档 [Uvicorn 部署](https://www.uvicorn.org/deployment/)
- 🛠 工具 [Pydantic 数据校验](https://docs.pydantic.dev/)

## Demo 练习：FastAPI+流式+缓存+监控 骨架

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


## 真实案例：简历写"熟悉部署"却拿不出实物——整合出可演示生产级服务

**背景**：一个候选人面试 FDE，简历写"熟悉 LLM 部署"，但面试官说"你部署一个给我看看"，他拿不出任何可现场跑的东西——之前都是零散学了 vLLM、Docker、流式，从没整合成一个完整服务。

**问题**：单点学过 ≠ 会交付。FDE 面试要的是"你能端出一个生产级服务骨架：接口 + 流式 + 缓存 + 监控，现场跑给我看"。零散知识点没整合，等于没交付能力。

**定位过程**：他复盘发现缺的不是知识点，是"整合成可演示物"这一步。于是把 Day16-20 学的组件缝成一个完整 FastAPI 服务，作为面试可演示项目。

**做法**：一个文件整合——流式接口 + 语义缓存 + 模型路由 + 健康检查 + Prometheus 指标，面试现场 `uvicorn` 起服务、curl 能打、Prometheus 能看指标。
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, PlainTextResponse
import openai, time, asyncio
from prometheus_client import Counter, Histogram, generate_latest

app = FastAPI()
client = openai.OpenAI()
REQ = Counter("llm_req_total", "总请求数", ["route"])
LAT = Histogram("llm_lat_seconds", "延迟", ["route"])
CACHE = {}

@app.get("/health")
def health(): return {"status":"ok"}              # Day19 探针用

@app.post("/chat")
async def chat(q: str):
    t0 = time.time()
    route = "cache_hit" if q in CACHE else ("flash" if len(q)<20 else "pro")
    REQ.labels(route).inc()
    if q in CACHE:
        return {"answer": CACHE[q], "route":route}
    model = "gpt-4o-mini" if route=="flash" else "gpt-4o"
    def gen():
        st = client.chat.completions.create(
            model=model, messages=[{"role":"user","content":q}], stream=True)
        ans=""
        for c in st:
            tok = c.choices[0].delta.content
            if tok: ans+=tok; yield f"data: {tok}\n\n"   # Day17 流式
        yield "data: [DONE]\n\n"
        CACHE[q] = ans; LAT.labels(route).observe(time.time()-t0)  # Day20 缓存+指标
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/metrics")
def metrics(): return PlainTextResponse(generate_latest())  # Prometheus 抓取
```

**结果**：面试现场 `uvicorn app.main:app` 起服务，`curl /chat?q=你好` 看到流式输出，`/metrics` 看到 QPS/延迟指标，第二次同问命中缓存秒回。面试官当场说"这个能跑、能看到指标，是真能交付的人"。拿到 offer。

**踩坑**：第一版他把缓存、流式、监控拆成三个 demo 没整合，面试官问"这俩怎么配合"答不上。缝进一个文件、一条请求走完全链路才说服人。还有 `/metrics` 忘了暴露，面试时 Prometheus 抓不到指标——把可观测性也现场演示出来，比嘴讲"我做了监控"强 10 倍。

**可复用经验**：部署周别只单点学，务必整合成"一个能现场跑、能看指标、能命中缓存"的生产级骨架作为面试物。**会单点 ≠ 会交付，能整合成可演示物才是**。这是 FDE 部署能力的最终交付考核——面试官看的是"你端出来的东西能不能跑"，不是你背了几张 YAML。
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

**Day 22：Prompt Injection 与 API 安全**
> 🔴 AI 安全攻防（差异化能力） · 第 5 周
