# Day 19：K8s 部署与 LLM 服务监控

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-19.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-19.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 LLM 服务在 K8s 上的部署形态：Deployment/Service/HPA/GPU 调度
2. 掌握私有化交付清单：客户内网部署 LLM 服务需要哪些组件与配置
3. 生成可交付的 K8s 部署 YAML 与私有化交付检查清单
4. 理解 LLM 服务的可观测性三支柱：Metrics、Logs、Traces
5. 掌握关键监控指标：QPS、延迟P99、token用量、成本、错误率、GPU利用率
6. 实现用量统计与成本告警，FDE 交付必备的运营数据

## 推荐资料

- 📚 文档 [Kubernetes 官方文档](https://kubernetes.io/docs/)
- 📄 文章 [K8s 部署 LLM 推理服务](https://kubernetes.io/blog/)
- 🛠 工具 [Helm 包管理](https://helm.sh/)
- 📚 文档 [Prometheus 监控](https://prometheus.io/docs/)
- 🛠 工具 [Grafana 可视化](https://grafana.com/)
- 📄 文章 [LLM 可观测性实践](https://www.datadoghq.com/)

## Demo 练习：生成 K8s 部署 YAML + 私有化交付清单 + LLM 服务监控：指标导出 + 用量统计 + 成本告警

用脚本生成 LLM 服务的 K8s 部署清单，并输出私有化交付检查清单

**第二部分：** 实现 Prometheus 风格的指标导出，统计 token 用量与成本，触发成本告警

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 约 4.5h |

### 复现步骤

1. 生成 Deployment + Service + HPA + ConfigMap YAML
2. 配置 GPU 资源请求与就绪探针
3. 生成私有化交付检查清单（网络/存储/镜像/密钥/监控）
4. 实现 Counter/Histogram 指标导出（Prometheus 格式）
5. 统计每用户/每模型的 token 用量与成本
6. 实现成本告警：日预算超阈值触发通知

## 保姆教程

## 原理速览
私有化是 FDE 高频需求（3/6 JD 要求私有化部署）：客户内网部署 LLM，数据不出域。
K8s 是事实标准。本实验用脚本生成部署清单，理解每段 YAML 作用，而非手写易错的配置。

## 代码
```python
def gen_k8s_manifest(image="vllm/vllm:latest", replicas=2, gpu=1):
    return f"""# llm-serving.yaml —— 由脚本生成，请勿手改
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-serving
  labels: {{app: llm-serving}}
spec:
  replicas: {replicas}
  selector: {{matchLabels: {{app: llm-serving}}}}
  template:
    metadata: {{labels: {{app: llm-serving}}}}
    spec:
      containers:
      - name: vllm
        image: {image}
        ports: [{{containerPort: 8000}}]
        resources:
          requests: {{cpu: "4", memory: "16Gi", nvidia.com/gpu: "{gpu}"}}
          limits: {{nvidia.com/gpu: "{gpu}"}}
        readinessProbe: {{httpGet: {{path: /health, port: 8000}}, initialDelaySeconds: 30}}
        env:
        - {{name: MODEL_NAME, valueFrom: {{secretKeyRef: {{name: llm-secret, key: model}}}}}}
---
apiVersion: v1
kind: Service
metadata: {{name: llm-serving}}
spec:
  selector: {{app: llm-serving}}
  ports: [{{port: 80, targetPort: 8000}}]
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: {{name: llm-hpa}}
spec:
  scaleTargetRef: {{apiVersion: apps/v1, kind: Deployment, name: llm-serving}}
  minReplicas: {replicas}
  maxReplicas: 6
  metrics: [{{type: Resource, resource: {{name: cpu, target: {{type: Utilization, averageUtilization: 70}}}}}}]
"""

print(gen_k8s_manifest())

CHECKLIST = [
    "网络：确认内网可达，出口代理白名单，DNS 解析",
    "存储：模型权重持久卷(PVC)挂载，日志卷独立",
    "镜像：私有镜像仓库可拉取，离线镜像包已导入",
    "密钥：API Key/模型路径用 Secret 注入，不入镜像",
    "GPU：nvidia.com/gpu 可调度，驱动版本匹配",
    "监控：Prometheus 抓取 /metrics，Grafana 看板就绪",
    "就绪探针：/health 通过才接流量",
    "回滚：保留上一版本镜像，可快速回退",
]
print("\n=== 私有化交付检查清单 ===")
for i, c in enumerate(CHECKLIST, 1):
    print(f"  ☐ {i}. {c}")
```
Secret 不入镜像；镜像签名校验；就绪探针门控；最小权限 RBAC。
私有化部署的安全要点：Secret 不入镜像（避免镜像仓库泄露=密钥泄露），
镜像来源可追溯（签名校验），就绪探针通过才接流量避免半启动服务暴露，
最小权限 RBAC 限制各组件能力。

---

## 第二部分：LLM 服务监控：指标导出 + 用量统计 + 成本告警

## 原理速览
FDE 交付后最怕'交付了但没法证明价值'。监控就是量化证明：服务用了多少、多快、多省钱。
JD 反复要求'跟踪业务指标'（交付周期、代码采纳率、效率提升），监控是数据来源。

## 代码
```python
from collections import defaultdict
import time

class Metrics:
    """Prometheus 风格指标"""
    def __init__(self):
        self.requests = 0
        self.latencies = []
        self.tokens_in = 0
        self.tokens_out = 0
        self.errors = 0
        self.usage_by_user = defaultdict(lambda: {"in":0,"out":0,"cost":0.0})
    def record(self, user, in_tok, out_tok, latency_ms, ok=True, model="gpt-4o-mini"):
        self.requests += 1
        self.latencies.append(latency_ms)
        self.tokens_in += in_tok; self.tokens_out += out_tok
        if not ok: self.errors += 1
        p = {"gpt-4o-mini":{"in":0.00105,"out":0.0042}}.get(model,{"in":0,"out":0})
        cost = in_tok/1000*p["in"] + out_tok/1000*p["out"]
        self.usage_by_user[user]["in"] += in_tok
        self.usage_by_user[user]["out"] += out_tok
        self.usage_by_user[user]["cost"] += cost
    def p99(self):
        s = sorted(self.latencies)
        return s[int(len(s)*0.99)] if s else 0
    def export(self):
        return f"""# HELP llm_requests_total Total requests
# TYPE llm_requests_total counter
llm_requests_total {self.requests}
llm_errors_total {self.errors}
llm_tokens_in_total {self.tokens_in}
llm_tokens_out_total {self.tokens_out}
llm_latency_p99_ms {self.p99()}"""

m = Metrics()
for u, it, ot, lat in [("alice",100,200,300),("bob",50,80,250),("alice",200,300,500),("bob",30,50,200)]:
    m.record(u, it, ot, lat)
print("=== /metrics ===")
print(m.export())
print("\n=== 用量与成本 ===")
for u, v in m.usage_by_user.items():
    print(f"  {u}: in={v['in']} out={v['out']} cost=${v['cost']:.4f}")

# 成本告警
def cost_alert(usage, daily_budget=1.0):
    total = sum(v["cost"] for v in usage.values())
    if total > daily_budget:
        return f"⚠ 成本告警：当日 ${total:.4f} 超预算 ${daily_budget}"
    return f"✅ 当日成本 ${total:.4f} 在预算内"
print(cost_alert(m.usage_by_user, daily_budget=0.0001))
```
日志含 prompt/output 敏感数据，需 PII 脱敏+访问审计+保留期控制；指标不存明文。
日志中可能含用户 prompt 与模型输出（敏感数据），日志收集与留存要合规：
PII 脱敏、访问审计、保留期控制。监控指标本身也应不含明文 prompt，只统计量级。

## 进阶挑战

1. 用 Helm 把上面的 YAML 模板化，参数化 image/replicas/gpu
2. 加一个 NetworkPolicy 限制只有 API 网关能访问 LLM 服务
3. 实现滚动更新 + 就绪探针门控，确保零停机部署
4. 接入真实 prometheus_client，把指标暴露到 /metrics 被 Prometheus 抓取
5. 实现 P50/P95/P99 多分位延迟直方图
6. 对接企业微信：成本超预算时自动推送告警（复用你的 webhook）

---

## 明日预告

**Day 20：性能与成本优化**
> 🟠 部署交付与生产化 · 第 4 周
