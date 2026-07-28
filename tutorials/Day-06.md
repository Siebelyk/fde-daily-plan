# Day 6：RAG 基础与架构

> 🟢 RAG 构建与交付 · 第 2 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-06.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-06.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 RAG（检索增强生成）全流程：加载→分块→嵌入→检索→重排→生成→引用
2. 理解为什么 RAG 是 FDE 最高频交付场景（6/6 JD 要求）
3. 从零实现一个最简 RAG，跑通完整闭环

## 推荐资料

- 📝 论文 [RAG 原始论文 (Lewis et al.)](https://arxiv.org/abs/2005.11401)
- 📄 文章 [Pinecone - RAG 从零讲清](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- 📚 文档 [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)

## Demo 练习：最简 RAG：从零跑通检索增强生成闭环

30 行代码跑通 RAG 全闭环。用 OpenAI Embedding + Chroma 向量库，给模型'喂'外部知识——RAG 是 6/6 岗位的必考题。

| 难度 | 预计时间 |
|------|----------|
| 入门 | 2h |

### 复现步骤

1. 实现文档加载与分块（固定长度 + 重叠）
2. 实现 TF-IDF 检索：对查询返回 Top-K 相关文档块
3. 拼装 Prompt（检索结果+问题）→ mock 生成 → 输出带引用的答案

## 保姆教程

## 原理速览
RAG = 先检索后生成。模型本身不存最新知识，靠"检索相关文档塞进上下文"来回答。
FDE 落地 80% 场景是 RAG：企业知识库问答、政策检索、产品手册问答。本实验从零跑通闭环。

## 代码
```python
import math
from collections import Counter, defaultdict

# 1. 文档分块（固定长度 + 重叠）
def chunk(text, size=40, overlap=10):
    chunks = []
    i = 0
    while i < len(text):
        c = text[i:i+size]
        if c: chunks.append(c)
        if i+size >= len(text): break
        i += size - overlap
    return chunks

docs = "退款政策7天内可退需提供订单号。保修期1年含免费维修。配送时间3到5个工作日。客服电话4001234。"
chunks = chunk(docs, size=24, overlap=6)
print("分块:", chunks)

# 2. TF-IDF 检索
def build_index(chunks):
    df = defaultdict(int)
    tf = []
    for c in chunks:
        words = list(c)
        cnt = Counter(words)
        tf.append(cnt)
        for w in cnt: df[w] += 1
    N = len(chunks)
    idf = {w: math.log(N/(1+d)) for w,d in df.items()}
    return tf, idf

def retrieve(query, chunks, tf, idf, top_k=2):
    qw = Counter(query)
    scores = []
    for i, cnt in enumerate(tf):
        s = sum(qw[w]*cnt.get(w,0)*idf.get(w,0) for w in qw)
        scores.append((s, i))
    scores.sort(reverse=True)
    return [chunks[i] for s,i in scores[:top_k]]

tf, idf = build_index(chunks)

# 3. RAG 生成闭环
def rag_answer(query):
    refs = retrieve(query, chunks, tf, idf, top_k=2)
    context = "\n".join(refs)
    prompt = f"根据以下资料回答问题，若资料不足请说明：\n资料：{context}\n问题：{query}"
    # mock 生成
    ans = f"根据资料回答：{refs[0][:20]}..."
    return ans, refs

q = "保修期多久？"
ans, refs = rag_answer(q)
print(f"\n问题: {q}\n答案: {ans}\n引用: {refs}")
```
检索注入的外部文档存在间接 Prompt Injection 风险，需隔离检索内容并校验答案来源。
RAG 把外部文档放进模型上下文，文档中可藏 Prompt Injection（间接注入）——
这是 W5 安全周重点。工程上要把检索内容与系统指令隔离，并在输出处校验答案是否真的来自检索内容。

## 进阶挑战

1. 把 TF-IDF 换成真实 Embedding（sentence-transformers），对比检索质量
2. 接入真实 LLM 生成，观察 RAG 如何降低幻觉
3. 统计不同 chunk_size/overlap 对检索召回率的影响

---

## 明日预告

**Day 7：分块策略与向量数据库构建**
> 🟢 RAG 构建与交付 · 第 2 周
