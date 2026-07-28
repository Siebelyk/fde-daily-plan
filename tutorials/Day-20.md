# Day 20：性能与成本优化

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-20.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-20.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握 LLM 服务三大优化手段：语义缓存、批处理、模型路由
2. 理解 PagedAttention、连续批处理等推理优化原理
3. 实现成本优化方案：简单任务走小模型，复杂任务走大模型

## 推荐资料

- 📚 文档 [vLLM 性能优化](https://docs.vllm.ai/)
- 🛠 工具 [GPTCache 语义缓存](https://github.com/zilliztech/GPTCache)
- 📄 文章 [OpenAI - 降低 LLM 成本技巧](https://cookbook.openai.com/)

## Demo 练习：语义缓存 + 批处理 + 模型路由

上线后就是成本与性能。语义缓存+批处理+模型路由，三招把推理成本打下来——客户最关心的'用起来贵不贵'。

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 实现语义缓存：相似问题命中缓存直接返回，省一次调用
2. 实现批处理：多个请求合并处理，提升吞吐
3. 实现模型路由：简单任务路由到小模型省钱

## 保姆教程

## 原理速览
FDE 交付的最大反对意见是'太贵'。优化手段三件套：① 语义缓存（相似问题复用答案）省调用
② 批处理（合并请求）提吞吐 ③ 模型路由（简单走小模型）省钱。这三招直接关系客户买单意愿。

## 代码
```python
import time, hashlib

# 1. 语义缓存（mock：用字符相似度判断是否命中）
class SemanticCache:
    def __init__(self, threshold=0.7): self.cache=[]; self.th=threshold
    def _sim(self,a,b): return len(set(a)&set(b))/len(set(a)|set(b)) if a and b else 0
    def get(self, q):
        for cached_q, ans in self.cache:
            if self._sim(q, cached_q) >= self.th: return ans, "hit"
        return None, "miss"
    def set(self, q, ans): self.cache.append((q, ans))

cache = SemanticCache()
def llm_call(q): time.sleep(0.01); return f"答案：{q[:10]}的处理方案"

def cached_call(q):
    ans, status = cache.get(q)
    if status == "hit": return ans, status
    ans = llm_call(q); cache.set(q, ans)
    return ans, status

# 2. 批处理
def batch_call(queries):
    print(f"  批处理 {len(queries)} 个请求（一次推理）")
    return [llm_call(q) for q in queries]

# 3. 模型路由
def route_model(q):
    if len(q) < 10: return "gpt-4o-mini"   # 简单→小模型
    return "gpt-4o"                          # 复杂→大模型

print("=== 语义缓存 ===")
for q in ["怎么退款", "退款流程是什么", "北京天气"]:
    ans, st = cached_call(q); print(f"  {q} → {st}")

print("\n=== 批处理 ===")
print(batch_call(["问题1","问题2","问题3"]))

print("\n=== 模型路由 ===")
for q in ["你好", "请分析这份企业数字化转型报告并提出建议"]:
    print(f"  '{q[:12]}' → {route_model(q)}")

# 成本对比
print("\n💡 优化后：缓存命中率30%+简单任务路由小模型，综合成本可降50%+")
```
语义缓存按租户隔离防泄露；批处理需租户隔离避免交叉泄露。
语义缓存要注意：缓存的内容可能含敏感信息，命中返回给另一用户=数据泄露。
工程上缓存要按用户/租户隔离，且缓存内容做脱敏。批处理时多个租户请求合并
要注意隔离，避免交叉泄露。

## 进阶挑战

1. 接入 GPTCache 用真实 Embedding 做语义缓存，测命中率
2. 实现连续批处理（continuous batching）模拟，对比静态批处理吞吐
3. 做一个成本计算器：输入缓存命中率与路由比例，输出综合成本下降%

---

## 明日预告

**Day 21：第四周实战：生产级 LLM 服务部署**
> 🟠 部署交付与生产化 · 第 4 周
