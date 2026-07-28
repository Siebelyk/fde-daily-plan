# Day 6：RAG 基础与架构

> 🟢 RAG 构建与交付 · 第 2 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-06.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-06.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 RAG 为什么是大模型落地的首选:解决幻觉+知识更新+私有数据三大痛点
2. 30 行代码跑通 RAG 全闭环:文档→分块→向量→检索→生成,亲眼看效果
3. 对比 RAG vs 微调:什么场景该用 RAG,什么场景该微调(JD 高频面试题)
4. 理解 RAG 的核心组件,为本周深入分块/向量/重排打基础

## 推荐资料

- 📝 论文 [RAG 原始论文 (Lewis et al.)](https://arxiv.org/abs/2005.11401)
- 📄 文章 [Pinecone - RAG 从零讲清](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- 📚 文档 [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)

## Demo 练习：最简 RAG：从零跑通检索增强生成闭环

RAG 是 6/6 岗位必考题。30 行代码从零跑通检索增强生成闭环,亲眼看模型用外部知识回答——这是 FDE 的核心交付能力,面试第一个就会问。

| 难度 | 预计时间 |
|------|----------|
| 入门 | 2h |

### 复现步骤

1. 准备一份本地知识文档(纯文本即可)
2. 实现 TF-IDF 检索(不依赖外部 API,零成本跑通)
3. 把检索到的片段拼进 prompt,让模型基于检索内容回答
4. 对比开/关 RAG 的回答差异,直观理解 RAG 价值

## 保姆教程

## 原理速览
大模型有三个天生缺陷,RAG 专门解决它们:
1. **幻觉**:模型会编造看似合理但错误的内容 → RAG 让它基于真实文档回答
2. **知识截止**:模型不知道训练后发生的事 → RAG 接入实时文档
3. **不懂你的私有数据**:模型没见过你的内部资料 → RAG 喂你的数据给它

**RAG = 检索(Retrieval) + 增强(Augmented) + 生成(Generation)**
流程:用户提问 → 从知识库检索相关片段 → 把片段塞进 prompt → 模型基于片段回答。

### RAG vs 微调(JD 面试高频题)
| 维度 | RAG | 微调 |
|---|---|---|
| 适合 | 知识常变、要可溯源 | 风格/格式固定、知识稳定 |
| 成本 | 低(改文档即可) | 高(需标注数据+训练) |
| 更新 | 改文档即时生效 | 重新训练 |
| 幻觉 | 低(基于真实文档) | 仍可能幻觉 |
| 灵活性 | 多知识库切换方便 | 换知识要重训 |

**面试标准答**:"知识更新快/要可溯源/多场景切换用 RAG;风格统一/知识稳定/低延迟用微调;两者也可结合。"

## 代码:30 行跑通 RAG 全闭环(零外部 API 依赖)
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 1. 知识库(你的私有文档)
docs = [
    "公司报销流程:填写报销单,附发票,提交部门主管审批,超过5000元需VP审批。",
    "请假制度:年假需提前3天申请,病假需附医院证明,连续超3天需HR备案。",
    "差旅标准:经济舱机票需提前7天预订,酒店标准一线城市500元/晚以下。",
    "采购流程:填写采购申请,3万以下部门审批,3万以上需采购部和财务联签。",
    "入职办理:入职当天到HR领取工牌,开通邮箱,导师1周内制定培养计划。"
]
# 2. 向量化(TF-IDF,实际用 Embedding)
vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(docs)

# 3. 检索
def retrieve(query, top_k=2):
    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, doc_vectors)[0]
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return [docs[i] for i in top_idx if scores[i] > 0]

# 4. 生成(拼进 prompt;无 API 时直接展示检索结果)
def rag_answer(query):
    context = "\n".join(retrieve(query))
    # 实际:prompt = f"基于以下资料回答:\n{context}\n问题:{query}"
    # 这里展示 RAG 核心机制
    return f"[检索到相关文档]\n{context}\n\n→ 模型会基于以上内容回答:{query}"

# 测试
for q in ["怎么报销", "请假要什么证明", "出差住酒店标准"]:
    print(f"\n问: {q}")
    print(rag_answer(q))

print("\n✅ RAG 闭环跑通! 关掉检索=模型瞎编,开着检索=基于真实文档答")
```

## 真实案例
某 FDE 给律所做合同助手。律师问"租赁合同最长能签几年",模型不知道(训练数据无该律所内部规范),加 RAG 接入律所知识库后,准确回答"根据我们所规定最长 20 年并附条款依据"。律师最买账的是**答案带出处**,能直接引用。**RAG 的可溯源是它替代直接问模型的关键优势**。

RAG 会把检索内容当事实,知识库投毒会导致基于虚假内容回答,生产环境必须做文档来源审核+内容过滤+权限隔离防止泄露。
RAG 检索的内容会被模型当作事实,如果知识库被投毒(植入虚假文档),模型会基于虚假内容回答。生产环境必须做文档来源审核+内容过滤。检索结果可能泄露其他用户隐私信息,需做权限隔离。


## 进阶挑战

1. 把 TF-IDF 换成 OpenAI Embedding + cosine 相似度,对比检索效果
2. 加 5 篇文档,测试检索能否找到正确的那篇
3. 思考:什么问题 RAG 反而不如直接问模型?(知识模糊/需推理的问题)

---

## 明日预告

**Day 7：分块策略与向量数据库构建**
> 🟢 RAG 构建与交付 · 第 2 周
