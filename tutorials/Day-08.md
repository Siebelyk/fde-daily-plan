# Day 8：检索与重排：混合检索 + Cross-Encoder 重排

> 🟢 RAG 构建与交付 · 第 2 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-08.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-08.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解稀疏检索（BM25）与密集检索（向量）的互补性，掌握混合检索
2. 掌握 Cross-Encoder 重排：先用向量粗召回，再用重排模型精排
3. 实现引用回溯：答案标注来自哪个文档块，增强可信度

## 推荐资料

- 📄 文章 [BM25 检索算法](https://www.pinecone.io/learn/bm25/)
- 📄 文章 [Cross-Encoder 重排](https://www.sbert.net/examples/applications/cross-encoder/)
- 📝 论文 [Hybrid Retrieval 混合检索](https://arxiv.org/abs/2210.01467)

## Demo 练习：混合检索 + 重排 + 引用回溯

实现 BM25+向量混合召回，再用 Cross-Encoder mock 重排，最后输出带引用的答案

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 实现 BM25 稀疏检索 + 模拟向量密集检索
2. 用 RRF（Reciprocal Rank Fusion）融合两路结果
3. 实现 Cross-Encoder 重排（mock）+ 引用回溯标注

## 保姆教程

## 原理速览
单靠向量检索会漏掉关键词精确匹配，单靠 BM25 不懂语义。生产 RAG 通常两路召回再融合（RRF），
然后过一遍 Cross-Encoder 重排（query 与每个文档逐对打分，更准但更慢），最后 Top-K 生成。
这是 FDE 提升 RAG 效果的关键工程手段。

## 代码
```python
import math
from collections import Counter, defaultdict

docs = ["退款政策7天内可退需订单号", "保修1年免费维修", "配送3到5个工作日",
        "客服热线4001234", "退换货需保留原包装"]

# 1. BM25 稀疏检索
def bm25(query, docs, k1=1.5, b=0.75):
    N = len(docs)
    dl = [len(d) for d in docs]
    avgdl = sum(dl)/N
    df = defaultdict(int)
    for d in docs:
        for w in set(d): df[w]+=1
    scores = []
    qw = list(query)
    for i, d in enumerate(docs):
        cnt = Counter(d)
        s = 0
        for w in qw:
            if w not in cnt: continue
            idf = math.log((N-df[w]+0.5)/(df[w]+0.5)+1)
            s += idf*(cnt[w]*(k1+1))/(cnt[w]+k1*(1-b+b*dl[i]/avgdl))
        scores.append((s, i))
    scores.sort(reverse=True)
    return [i for _,i in scores[:5]]

# 2. 模拟向量密集检索（真实场景用 Embedding + 余弦相似度）
def vector_search(query, docs):
    # mock：按字符重叠度模拟相似度
    return sorted(range(len(docs)), key=lambda i: len(set(query)&set(docs[i])), reverse=True)[:5]

# 3. RRF 融合
def rrf(*rankings, k=60):
    scores = defaultdict(float)
    for ranking in rankings:
        for r, idx in enumerate(ranking):
            scores[idx] += 1/(k+r)
    return [i for i,_ in sorted(scores.items(), key=lambda x:-x[1])]

# 4. Cross-Encoder 重排（mock：query 与 doc 字符重合度）
def rerank(query, candidates):
    return sorted(candidates, key=lambda i: len(set(query)&set(docs[i])), reverse=True)

query = "保修期多久能修"
bm = bm25(query, docs)
vec = vector_search(query, docs)
fused = rrf(bm, vec)
final = rerank(query, fused)[:2]
print(f"查询: {query}")
print(f"BM25: {[docs[i] for i in bm[:3]]}")
print(f"向量: {[docs[i] for i in vec[:3]]}")
print(f"RRF融合后重排 Top2: {[docs[i] for i in final]}")

# 5. 引用回溯
print(f"\n答案: 保修期为1年含免费维修 [来源: doc{final[0]}]")
```
重排环节对每候选拼接送模型，存在 DoS 与注入放大风险，需限制候选数与并发。
重排阶段每个候选都要与 query 拼接送模型，恶意 query 可在重排环节触发额外开销
（DoS）。工程上要限制候选数量与重排并发，并对 query 做长度/内容过滤。

## 进阶挑战

1. 用 sentence-transformers 实现真实 Cross-Encoder 重排，对比 mock 效果
2. 引入 MMR（最大边际相关性）做多样性重排，避免答案重复
3. 实现引用置信度评分：低于阈值的回答标注'资料不足'而非编造

---

## 明日预告

**Day 9：RAG 评测与安全检查点**
> 🟢 RAG 构建与交付 · 第 2 周
