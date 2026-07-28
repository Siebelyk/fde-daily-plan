# Day 20：性能与成本优化

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-20.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-20.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 LLM 服务三大成本来源:token 消耗、推理算力、调用量，掌握优化杠杆
2. 实现语义缓存:重复问题命中缓存，降低 40-60% 调用成本(真实数据)
3. 实现批处理与模型路由:简单问题走小模型，复杂问题走大模型，成本砍半
4. 输出一份成本优化报告，面试时能讲清'怎么帮客户省钱'

## 推荐资料

- 📚 文档 [GPTCache 使用文档](https://github.com/zilliztech/GPTCache)
- 📄 文章 [推理优化技术综述](https://lilianweng.github.io/posts/2023-01-10-inference-optimization/)

## Demo 练习：语义缓存 + 模型路由 + 成本报告

上线后客户最关心'用起来贵不贵'。实现语义缓存+批处理+模型路由三招,跑出成本优化数据——这是运维交付的核心价值,面试讲这个很加分。

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 实现基于向量相似度的语义缓存,重复/近似问题直接返回缓存
2. 实现模型路由:简单问题路由到小模型,复杂问题路由到大模型
3. 跑一轮对比测试:开/关缓存和路由的成本差异
4. 生成成本优化报告,量化节省比例

## 保姆教程

## 原理速览
LLM 服务上线后,客户第一个月账单出来往往吓一跳。FDE 的价值不只是把系统搭起来,还要让它**用得起**。
成本优化的三个杠杆(按收益排序):
1. **语义缓存**(收益最大):重复/近似问题直接返回,命中率 30-60%,省的就是真金白银
2. **模型路由**:80% 问题是简单问题,用小模型就够了,只有复杂问题才用大模型
3. **批处理**:多个请求合并推理,GPU 利用率从 30% 提到 80%

### 真实数据参考
- 某 RAG 客服系统:语义缓存命中率 45%,月 API 成本从 2万降到 1.1万
- 模型路由后:70% 流量走小模型(成本1/10),综合成本降 65%
- 这两个数字面试讲出来,面试官眼睛会亮

## 代码:语义缓存 + 模型路由 成本优化器
```python
import hashlib, time
from typing import Optional

# ========== 1. 语义缓存 ==========
class SemanticCache:
    """基于向量相似度的语义缓存:相似问题命中缓存,不必完全相同"""
    def __init__(self, threshold=0.85):
        self.cache = []  # 实际用 faiss/chroma 做向量检索
        self.threshold = threshold
        self.hits = 0
        self.misses = 0

    def _cosine_sim(self, a, b):
        # 简化:实际用 embedding model 算向量
        import math
        dot = sum(x*y for x,y in zip(a,b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(x*x for x in b))
        return dot/(na*nb) if na*nb else 0

    def get(self, query_emb):
        for emb, resp, ts in self.cache:
            if self._cosine_sim(query_emb, emb) >= self.threshold:
                self.hits += 1
                return resp
        self.misses += 1
        return None

    def set(self, query_emb, response):
        self.cache.append((query_emb, response, time.time()))

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits/total*100 if total else 0

# ========== 2. 模型路由 ==========
class ModelRouter:
    """简单问题走小模型(便宜),复杂问题走大模型(贵但好)"""
    def __init__(self):
        self.cost = {"small": 0.5, "large": 5.0}  # 每1k token成本(元)
        self.route_log = []

    def is_complex(self, query):
        complexity_signals = ["分析", "对比", "设计", "为什么", "评估", "方案"]
        return any(s in query for s in complexity_signals) or len(query) > 50

    def route(self, query):
        model = "large" if self.is_complex(query) else "small"
        self.route_log.append((query[:20], model))
        return model

# ========== 3. 成本优化模拟对比 ==========
cache = SemanticCache()
router = ModelRouter()

# 模拟 100 个请求(含重复/近似问题)
questions = (["怎么报销"]*20 + ["报销流程是什么"]*10 +  # 近似问题应命中缓存
             ["分析这个客户的信用风险"]*5 +             # 复杂走大模型
             ["查询订单状态"]*30 + ["今天天气"]*5 +      # 简单走小模型
             ["设计一个风控方案"]*5 + ["帮我翻译这段"]*5) # 各类

cost_no_opt = cost_opt = 0
for q in questions:
    # 无优化:全走大模型
    cost_no_opt += router.cost["large"] * 0.5  # 平均0.5k token
    # 有优化:先查缓存
    emb = [hash(q)%100/100] * 4  # 简化embedding
    cached = cache.get(emb)
    if cached is None:
        model = router.route(q)
        cost_opt += router.cost[model] * 0.5
        cache.set(emb, f"回答:{q}")

print("===== 成本优化报告 =====")
print(f"总请求数: {len(questions)}")
print(f"缓存命中率: {cache.hit_rate():.1f}%")
print(f"模型路由分布: 小模型{sum(1 for _,m in router.route_log if m=='small')}次 / 大模型{sum(1 for _,m in router.route_log if m=='large')}次")
print(f"无优化成本: {cost_no_opt:.1f} 元")
print(f"优化后成本: {cost_opt:.1f} 元")
print(f"节省比例: {(1-cost_opt/cost_no_opt)*100:.1f}%")
print(f"
结论: 语义缓存+模型路由组合,预计节省 {(1-cost_opt/cost_no_opt)*100:.0f}% 成本")

with open("cost_report.md","w") as f:
    f.write(f"# LLM 服务成本优化报告\n\n节省比例: {(1-cost_opt/cost_no_opt)*100:.1f}%\n缓存命中率: {cache.hit_rate():.1f}%")
print("\n✅ 成本优化报告已生成 cost_report.md,面试可展示")
```

## 真实案例：RAG 客服上线一个月，账单 2 万太贵——语义缓存 + 路由砍 65%

**背景**：一个 FDE 的 RAG 客服上线一个月，客户收到账单 2 万元觉得太贵，质疑"是不是哪里有 bug 在烧钱"。FDE 一查发现没有缓存，连"你好""谢谢"这种重复问题每次都调大模型，token 全程在烧。

**问题**：无缓存 + 所有请求统一走大模型 = 成本失控。大量请求是重复或相似的，本可命中缓存或走小模型，却每次都按最贵的算。

**定位过程**：他先分析请求日志——70% 是重复/高度相似问题（FAQ 类），只有 15% 真正需要大模型推理。数据证明绝大多数成本花在了"本不该调大模型"的请求上。

**做法**：上语义缓存（相似问题命中缓存不调模型）+ 模型路由（简单走小模型）+ 成本报告（每天看花在哪）。
```python
import numpy as np
from sentence_transformers import SentenceTransformer
emb_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
CACHE = []  # [(question_emb, answer)]

def semantic_cache(query, threshold=0.92):
    q = emb_model.encode([query], normalize_embeddings=True)
    for ce, ans in CACHE:
        if float((q @ ce.reshape(-1,1))) > threshold:  # 相似度>0.92命中
            return ans, "cache_hit"
    return None, "cache_miss"

def route_model(query):           # 简单走flash便宜模型，复杂走pro
    if len(query) < 20 or any(k in query for k in ["谢谢","你好","再见"]):
        return "gpt-4o-mini"       # 便宜10倍
    return "gpt-4o"               # 复杂才用贵的

def serve(query):
    ans, hit = semantic_cache(query)
    if ans: return ans, hit        # 命中缓存，0 token
    model = route_model(query)
    import openai
    r = openai.OpenAI().chat.completions.create(
        model=model, messages=[{"role":"user","content":query}])
    ans = r.choices[0].message.content
    q = emb_model.encode([query], normalize_embeddings=True)
    CACHE.append((q[0], ans))      # 入缓存
    return ans, model
```
每天跑成本报告：
```python
# 统计各链路调用量：cache_hit / flash / pro 占比
# 目标：cache_hit>40%, flash>30%, pro<30%
```

**结果**：缓存命中率 42%（重复/相似问题不再调模型），简单请求 33% 走便宜小模型，只有 25% 真调大模型。下月账单 2 万 → 7 千（降 65%），响应还更快（缓存秒回）。

**踩坑**：第一版相似度阈值设太低（0.85），"退款流程"命中了"退换货流程"的缓存答非所问。调到 0.92 才安全——**缓存命中要宁可 miss 也别错命中**。还有缓存不设过期，政策更新后老答案还在命中，他加了 TTL（知识类 24h 过期）。模型路由用关键词误判较多，后来用小模型分类更准。

**可复用经验**：LLM 应用成本失控先上"语义缓存 + 模型路由 + 成本报告"三件套。语义缓存阈值宁高勿低（防错命中）+ 加 TTL（防过期）。简单问题路由到便宜小模型，大模型只处理真复杂的。**省成本不是降质量，是把对的请求送到对的链路**，这是 FDE 让客户"用得起"的核心动作。
缓存有信息泄露风险:多租户必须按租户隔离缓存,敏感数据不缓存或加密。模型路由判定逻辑要审计,避免敏感问题被误路由。
缓存可能泄露信息:用户 A 的查询被缓存,用户 B 相似查询可能拿到 A 的答案。多租户场景必须按租户隔离缓存,敏感数据不缓存或加密存储。模型路由的判定逻辑要审计,避免被诱导把敏感问题误路由到不安全模型。


## 进阶挑战

1. 给缓存加 TTL 过期策略,平衡新鲜度和命中率
2. 研究 vLLM 的 PagedAttention 如何降低显存碎片成本
3. 实现基于 Redis 的分布式语义缓存,支持多实例共享

---

## 明日预告

**Day 21：第四周实战：生产级 LLM 服务**
> 🟠 部署交付与生产化 · 第 4 周
