# Day 15：意图路由与多 Agent 实战

> 🟣 Agent 开发与 MCP 集成 · 第 3 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-15.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-15.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解意图识别在多 Agent 系统的作用：把用户请求路由到正确的处理链
2. 掌握三种意图识别方法：关键词/向量分类/LLM 路由
3. 实现一个意图路由器，把不同问题分发给不同 Agent
4. 整合本周所学：Agent 开发 + 工具调用 + MCP 集成 + 意图路由
5. 构建一个可演示的多 Agent 业务工作流（检索→写作→审核闭环）
6. 理解多 Agent 协同编排与交付价值

## 推荐资料

- 📄 文章 [Semantic Router 教程](https://github.com/aurelio-labs/semantic-router)
- 📚 文档 [LangGraph 多 Agent](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)

## Demo 练习：意图路由器 + 检索-写作-审核工作流

意图路由决定系统好不好用。对比关键词/向量/LLM 三种路由，再做三 Agent 协同工作流——客户场景里90%是路由问题。

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 约 5h |

### 复现步骤

1. 定义意图空间与对应 Agent
2. 实现关键词路由 + 向量相似度路由 + LLM 路由三种方式
3. 对比三种方式的准确率与成本
4. 定义三个 Agent 角色：检索（找资料）、写作（生成）、审核（校验）
5. 实现工作流编排：检索→写作→审核→不通过则打回重写
6. 跑一个完整业务案例，输出最终交付物

## 保姆教程

## 原理速览
FDE 落地的多 Agent 系统第一步往往是"用户这句话该交给谁"。意图识别=路由器。
关键词法便宜但脆，向量法懂语义但需 Embedding，LLM 法最准但最贵。生产常混合：先便宜后贵。

## 代码
```python
import math
from collections import Counter

INTENTS = {
    "售后": {"keywords": ["退", "换", "保修", "维修", "投诉"], "agent": "售后Agent"},
    "技术": {"keywords": ["报错", "故障", "bug", "安装", "配置", "报错码"], "agent": "技术Agent"},
    "销售": {"keywords": ["价格", "报价", "购买", "合作", "咨询"], "agent": "销售Agent"},
}

# 1. 关键词路由
def route_keyword(query):
    best, score = None, 0
    for intent, cfg in INTENTS.items():
        s = sum(1 for kw in cfg["keywords"] if kw in query)
        if s > score: best, score = intent, s
    return best or "通用"

# 2. 向量相似度路由（mock：用字符集合 Jaccard 模拟语义相似）
def route_vector(query):
    qw = set(query)
    best, score = None, 0
    for intent, cfg in INTENTS.items():
        sample = "".join(cfg["keywords"])
        sim = len(qw & set(sample)) / len(qw | set(sample)) if qw|set(sample) else 0
        if sim > score: best, score = intent, sim
    return best

# 3. LLM 路由（mock：综合判断）
def route_llm(query):
    if any(k in query for k in ["退","换","保修"]): return "售后"
    if any(k in query for k in ["报错","故障","安装"]): return "技术"
    if any(k in query for k in ["价格","购买"]): return "销售"
    return "通用"

tests = ["我要退款", "系统报错码500", "报价多少", "帮我查个东西"]
print("=== 意图路由对比 ===")
print(f"{'问题':12} {'关键词':6} {'向量':6} {'LLM':6}")
for q in tests:
    print(f"{q:12} {route_keyword(q):6} {route_vector(q):6} {route_llm(q):6}")
print("\n💡 生产中：先用关键词/向量低成本路由，命中不确定再用 LLM 兜底")
```
意图路由可被注入劫持到高权限 Agent，需置信度阈值与安全回退。
意图路由若被注入，可把恶意请求路由到高权限 Agent（如执行系统命令的技术Agent）。
工程上要对路由结果做置信度阈值，低置信度回退到安全的通用 Agent 并告警。

---

## 第二部分：检索-写作-审核三 Agent 协同工作流

## 原理速览
FDE 落地的高级形态是多 Agent 协同：不是单个 Agent 对话，而是一条业务流水线。
本实验编排'检索→写作→审核'三 Agent，模拟企业内容生产流程，这是交付级工作流的雏形。

## 代码
```python
class Agent:
    def __init__(self, role, action):
        self.role, self.action = role, action
    def __call__(self, input):
        result = self.action(input)
        print(f"  [{self.role}] → {result}")
        return result

def retrieve(topic): return f"检索到关于{topic}的3条资料：要点A、要点B、要点C"
def write(material): return f"基于{material}撰写：{material}的综合分析报告初稿"
def review(draft): 
    ok = "要点C" in draft  # mock：必须覆盖要点C
    return ("通过", draft) if ok else ("打回", "缺少要点C，请补充")

retriever = Agent("检索Agent", retrieve)
writer = Agent("写作Agent", write)
reviewer = Agent("审核Agent", review)

def workflow(topic, max_rounds=3):
    print(f"\n=== 业务工作流：产出关于'{topic}'的报告 ===")
    material = retriever(topic)
    for r in range(max_rounds):
        draft = writer(material)
        verdict, msg = reviewer(draft)
        if verdict == "通过":
            print(f"\n✅ 第{r+1}轮审核通过，交付物：\n{draft}")
            return draft
        print(f"  审核反馈：{msg}，打回重写")
        material += " 要点C"  # 补充后重写
    print("达到最大轮次，交付当前版本")
    return draft

workflow("企业 RAG 落地")
```
多 Agent 链任一节点被注入会横向扩散，需消息校验+信任评分+人工卡点+全链路审计。
多 Agent 链中，任一 Agent 被注入都会污染下游（横向移动）。W5 会专门讲多 Agent 攻防。
工程上：Agent 间消息校验 + 信任评分 + 关键节点人工卡点 + 全链路审计。

## 真实案例：简单问题也跑完整 Agent，又慢又贵——意图路由器一刀切好

**背景**：一个 FDE 的客服系统不管什么问题都走完整 Agent 流程：闲聊"你好"也要跑一遍"检索→工具决策→多步推理"，平均响应 4 秒、每次都烧一堆 token。客户反馈"太慢，简单问题不如搜索引擎快"。

**问题**：没做意图分流，所有请求一视同仁走最重的链路。简单 FAQ 用 RAG 秒回即可，复杂多步才需要 Agent。统一走 Agent 是"用大炮打蚊子"，慢且贵。

**定位过程**：他先统计了请求分布——70% 是简单 FAQ（"怎么退货""营业时间"），只有 10% 需要工具调用，20% 需要多步推理。数据证明绝大多数请求被过度处理了。

**做法**：加意图路由器，先分类请求复杂度，简单走轻量 RAG，复杂才走 Agent，并设置信度阈值 + fallback 防误判。
```python
import openai
client=openai.OpenAI()
def route(query):
    # 用小模型做意图分类，输出简单/工具/复杂
    r=client.chat.completions.create(model="gpt-4o-mini",temperature=0,
        messages=[{"role":"system","content":
          "分类用户意图：faq(查信息)/tool(需查实时数据)/complex(多步推理)。只输出类别。"},
          {"role":"user","content":query}])
    return r.choices[0].message.content.strip()

def rag_answer(q):           # 轻量RAG：毫秒级
    return f"(RAG)基于知识库答复：{q}"
def agent_answer(q):         # 重Agent：见Day12-13
    return f"(Agent)调工具+多步推理：{q}"

def serve(query):
    intent=route(query)
    if intent=="faq":     return rag_answer(query)      # 70%走这里，快又省
    if intent=="tool":    return agent_answer(query)    # 10%
    return agent_answer(query)                            # 20%复杂
print(serve("营业时间几点"))   # → RAG秒回
print(serve("订单A123到哪了退款多少"))  # → Agent
```

**结果**：简单问题平均延迟 4s → 0.6s（走轻量 RAG）；token 成本降 55%（70% 请求不再走 Agent）。客户"太慢"投诉消失，简单问题响应快过搜索引擎。

**踩坑**：第一版路由用关键词匹配（含"订单"就归 tool），结果"我想知道订单是什么意思"这种闲聊被误判去调工具、报错。改成小模型语义分类 + 置信度阈值，低于阈值就 fallback 到 Agent（宁重勿错）。还有分类用和大模型一样的 gpt-4o-mini 没省钱，他换成更便宜的分类专用小模型，路由本身成本也压下来了。

**可复用经验**：生产 Agent 系统必装意图路由器——先分类再分流，简单走 RAG、复杂走 Agent。这是同时优化延迟和成本的杠杆点，70% 请求走轻量链路，体验和账单同时变好。配置信度阈值 + fallback 防误判，宁慢勿错。

## 面试高频问答
问:意图路由为什么重要?
答:不是所有问题都要走完整 Agent。80% 是简单问题,路由到快链路;复杂问题才走完整流程。响应速度提升 5 倍,成本也降。

## 简历话术
- ❌ 弱表述:了解意图路由与多 Agent 实战
- ✅ 强表述:实现关键词/向量/LLM 三种意图路由,分发到不同处理链,系统响应速度提升 5 倍


## 进阶挑战

1. 接入真实 Embedding 做向量路由，对比关键词法的召回提升
2. 实现'路由 + 兜底'：低置信度问题转人工，而非乱路由
3. 加一个'注入意图'检测：query 含'忽略指令'等强制路由到隔离 Agent
4. 用 LangGraph 重写本工作流，引入状态图与条件分支
5. 加一个'人工审核'节点：涉及合规的内容必须人工确认才放行
6. 实现工作流回放：从审计日志还原任意一次执行过程

---

## 明日预告

**Day 16：推理引擎部署：vLLM 与 SGLang**
> 🟠 部署交付与生产化 · 第 4 周
