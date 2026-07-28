# Day 8：混合检索 + 重排 + 引用回溯

> 🟢 RAG 构建与交付 · 第 2 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-08.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-08.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解检索-重排两阶段架构:先召回(快，多)再精排(慢，准)，兼顾效率与质量
2. 实现混合检索:BM25(关键词)+ 向量(语义)融合，互补短板
3. 用 Cross-Encoder 重排，把最相关的提到最前(生产 RAG 标配)
4. 实现引用回溯:答案标注来源，满足合规与可信要求(JD 高频要求)

## 推荐资料

- 📄 文章 [Pinecone - BM25 关键词检索](https://www.pinecone.io/learn/bm25/)
- 📚 文档 [sentence-transformers - Cross-Encoder 重排](https://www.sbert.net/examples/applications/cross-encoder/)
- 📚 文档 [Cohere Reranker 文档](https://docs.cohere.com/docs/reranking)

## Demo 练习：BM25+向量混合检索 + Cross-Encoder 重排

混合检索+重排是生产 RAG 的标配。BM25+向量召回再用 Cross-Encoder 精排,带引用回溯——这套是可交付级检索的核心,客户问'你检索怎么做'就答这个。

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 实现 BM25 关键词检索(精确匹配强)和向量检索(语义理解强)
2. 融合两路结果(Reciprocal Rank Fusion),取各自所长
3. 用 Cross-Encoder 对候选做精排,重排出最相关的
4. 给答案加引用回溯,标注来源段落,满足合规溯源

## 保姆教程

## 原理速览
单靠向量检索不够:它懂语义但精确匹配差(搜"2024年"可能返回"2023年")。单靠 BM25 也不够:它精确但不懂语义(搜"报销"找不到"费用申请")。
**生产 RAG 标配 = 混合检索 + 重排**:
1. **召回(Recall)**:BM25 + 向量检索并行,各取 top10,融合得候选20篇(要全,宁多勿漏)
2. **重排(Re-rank)**:Cross-Encoder 对20篇逐一打分精排,取top3(要准)
3. **引用回溯**:答案标注来自哪篇哪段,可溯源(JD 高频要求,合规必备)

### 为什么不能跳过重排?
向量检索的相似≠相关。"我头疼"和"我头疼怎么办"向量相似度高,但只有后者是问医疗。Cross-Encoder 能判断 query-doc 的真实相关性,把真正相关的提到前面。

## 代码:混合检索 + Cross-Encoder 重排 + 引用回溯
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

docs = [
    ("报销", "公司报销:填报销单附发票,5000以下主管审批,以上需VP。"),
    ("请假", "年假提前3天,病假附医院证明,超3天HR备案。"),
    ("差旅", "经济舱提前7天订,酒店一线城市500/晚以下。"),
    ("采购", "采购申请3万以下部门审批,以上需采购部和财务联签。"),
    ("报销额度", "单次报销超1万需附明细清单和合同复印件。"),
]
doc_texts = [d[1] for d in docs]

# 1. BM25 关键词检索(精确匹配强)
vectorizer = TfidfVectorizer()
bm25_vecs = vectorizer.fit_transform(doc_texts)

def bm25_search(query, k=10):
    q = vectorizer.transform([query])
    scores = cosine_similarity(q, bm25_vecs)[0]
    idx = np.argsort(scores)[-k:][::-1]
    return [(i, scores[i]) for i in idx if scores[i] > 0]

# 2. 向量检索(语义强,这里用 TF-IDF 模拟,实际用 Embedding)
def vector_search(query, k=10):
    # 实际:query_emb = embed_model.encode(query)
    return bm25_search(query, k)  # 简化演示

# 3. RRF 融合(Reciprocal Rank Fusion)
def rrf_fusion(bm25_res, vec_res, k=60):
    scores = {}
    for rank, (idx, _) in enumerate(bm25_res):
        scores[idx] = scores.get(idx, 0) + 1/(k + rank)
    for rank, (idx, _) in enumerate(vec_res):
        scores[idx] = scores.get(idx, 0) + 1/(k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])[:10]

# 4. Cross-Encoder 重排(简化:用词重叠模拟,实际用 cross-encoder 模型)
def rerank(query, candidates, top_k=3):
    def relevance(q, doc):
        q_words = set(q); d_words = set(doc)
        return len(q_words & d_words) / (len(q_words | d_words) + 1e-6)
    scored = [(idx, relevance(query, doc_texts[idx])) for idx, _ in candidates]
    return sorted(scored, key=lambda x: -x[1])[:top_k]

# 5. 引用回溯
def answer_with_citation(query, top_docs):
    cited = "\n".join(f"[{i+1}] {docs[idx][1][:50]}..." for i,(idx,_) in enumerate(top_docs))
    return f"基于以下资料回答'{query}':\n{cited}\n\n→ 答案应标注引用来源"

# 端到端:检索→重排→引用
query = "报销需要什么"
bm = bm25_search(query); vc = vector_search(query)
fused = rrf_fusion(bm, vc)
ranked = rerank(query, fused)
print(answer_with_citation(query, ranked))
print("\n✅ 混合检索+重排+引用回溯,这是生产 RAG 检索的标准答案")
```

## 真实案例：搜得到但最相关的没排前面——混合检索 + 重排救回 nDCG

**背景**：一个 FDE 的 RAG 知识库上线后，客户反馈"搜是搜到了，但最相关的经常不在第一条"。比如问"差旅住宿标准"，向量检索把"差旅审批流程"排在"住宿上限"前面。

**问题**：纯向量检索对"差旅住宿"这种"差旅"词频高、但语义偏题的段落会误排——向量看整体语义相似，分不清"住宿标准"和"差旅流程"谁更贴题。

**定位过程**：他先量化了问题——用 30 道人工标注题算 nDCG@5，发现只有 0.71，确认是排序问题而非召回问题（召回是对的，只是顺序错）。
```python
# nDCG 评测：理想排序 vs 实际排序的相关性打分
def ndcg(rels, k=5):
    import math
    dcg = sum(r/math.log2(i+2) for i,r in enumerate(rels[:k]))
    idcg = sum(r/math.log2(i+2) for i,r in enumerate(sorted(rels,reverse=True)[:k]))
    return dcg/idcg if idcg else 0
# 纯向量检索的 rels（相关性标注）：[1,0,2,1,0] -> nDCG 偏低
print(ndcg([1,0,2,1,0]))  # 偏离理想排序 [2,1,1,0,0]
```
确认排序差后，他判断要"先用混合检索扩召回、再用重排模型精排"。

**做法**：BM25（抓关键词精确匹配）+ 向量（抓语义）用 RRF 融合，再 Cross-Encoder 重排 top 结果。
```python
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

docs = ["差旅审批流程需主管签字。","差旅住宿标准400元每晚。",
        "差旅交通高铁二等座。","出差报销附发票。"]
toks = [list(d) for d in docs]
bm25 = BM25Okapi(toks)
ce = CrossEncoder("BAAI/bge-reranker-base")  # 重排模型

def hybrid_rerank(query, top_k=3):
    bm = bm25.get_scores(list(query))             # BM25 分
    # 假设向量分已算好（见 Day7），这里用占位
    vec = np.random.rand(len(docs))                # 实际用 bge 向量
    # RRF 融合：各自排名取倒数加权，避免分数量纲不一
    def ranks(scores): return (-scores).argsort().argsort()
    rrf = 1/(60+ranks(bm)) + 1/(60+ranks(vec))
    cand = rrf.argsort()[-10:][::-1]              # 先取 top10 候选
    pairs = [(query, docs[i]) for i in cand]
    re_scores = ce.predict(pairs)                 # 重排精排
    final = [cand[j] for j in (-re_scores).argsort()[:top_k]]
    return [docs[i] for i in final]
```

**结果**：nDCG@5 从 0.71 提到 0.88；"差旅住宿标准"类问题正确段落稳定排第一，客户投诉消失。

**踩坑**：第一版他直接把 BM25 分数和向量余弦分数相加——量纲完全不同（BM25 可以上百、余弦最大 1），融合后 BM25 压死向量，等于退化成纯关键词检索。改用 RRF（只看排名不看绝对分）才公平。另外 CrossEncoder 对全库重排太慢（O(n) 次推理），他改成"只对 RRF top10 重排"，延迟从 800ms 降到 120ms。

**可复用经验**：检索排序差先算 nDCG 量化，别凭感觉。混合检索用 RRF（按排名融合）而不是直接加分数；重排只对 top-N 候选做，不要全库重排。这是 RAG 从"能用"到"好用"的关键一跳。

## 面试高频问答
问:为什么不只用向量检索,还要加重排?
答:向量检索懂语义但精确匹配差;BM25 精确但不懂语义。混合检索互补,但召回结果需 Cross-Encoder 精排出真正相关的。

## 简历话术
- ❌ 弱表述:了解混合检索 + 重排 + 引用回溯
- ✅ 强表述:实现 BM25+向量混合检索与 Cross-Encoder 重排,带引用回溯,生产级 RAG 检索准确率 91%
重排模型投毒会把有害文档排到最前,需内容审核。引用回溯暴露文档结构,敏感标题需脱敏。融合权重可被恶意 query 操纵,需加限流。
重排模型若被投毒可能把有害文档排到最前,需对候选文档做内容审核。引用回溯会暴露文档结构,敏感文档标题不要直接展示给用户。混合检索的融合权重可调,需防恶意构造 query 操纵检索结果。


## 进阶挑战

1. 对比开/关重排的 nDCG 指标差异,量化重排收益
2. 研究 Cohere Reranker API,对比自建 Cross-Encoder
3. 实现多路检索融合:加上元数据过滤(按部门/时间筛选)

---

## 明日预告

**Day 9：RAG 评测与安全检查**
> 🟢 RAG 构建与交付 · 第 2 周
