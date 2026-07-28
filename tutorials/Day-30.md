# Day 30：面试冲刺：知识图谱与模拟面试

> 🟡 客户落地实战与面试 · 第 6 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-30.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-30.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 梳理 42 天知识体系，构建 FDE 交付能力知识图谱
2. 整理 FDE 岗位面试高频考点与项目展示话术
3. 完成模拟面试与交付能力自评

## 推荐资料

- 🎓 课程 [DeepLearning.AI 短课程](https://www.deeplearning.ai/short-courses/)
- 📚 文档 [LangChain 面试题集](https://python.langchain.com/docs/concepts/)

## Demo 练习：FDE 知识图谱 + 模拟面试演练

面试冲刺：生成知识图谱+模拟面试。把 30 天学的串成可讲的项目链——这才是能拿 offer 的临门一脚。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 2.5h |

### 复现步骤

1. 构建 AI 安全知识图谱（4 大领域 x 28 天）
2. 整理 FDE 面试高频问题清单
3. 准备项目展示话术（3 个项目）
4. 完成模拟面试问答

## 保姆教程

## 知识图谱

### Week 1: LLM 核心原理与安全基础
- Day 1: Transformer & Attention → Q/K/V 计算, attention 权重, injection 热点
- Day 2: Tokenization → BPE 分词, token 边界注入, 绕过关键词过滤
- Day 3: GPT 演进 → Base vs Instruct, RLHF, 越狱与对齐
- Day 4: KV Cache → 缓存投毒, 前缀复用风险
- Day 5: 幻觉检测 → 自一致性, 幻觉对安全的影响
- Day 6: 安全评估 → 多维度评分, toxicity/bias/jailbreak
- Day 7: 实战项目 → 安全 LLM 推理服务（4层防御）

### Week 2: Prompt Injection 攻防实战
- Day 8: Injection 入门 → 6种攻击模式, 检测器
- Day 9: 越狱技术 → DAN, CoT, 多轮诱导, 检测
- Day 10: API 安全 → Key 管理, SSRF, 速率限制, 签名
- Day 11: Function Calling → 工具劫持, 参数注入, 返回值污染
- Day 12: 流式输出 → SSE 安全, buffer-and-check
- Day 13: Guardrails → 纵深防御, 多层 pipeline
- Day 14: 实战项目 → 安全 API 网关

### Week 3: RAG 安全全链路
- Day 15: 间接注入 → RAG 文档投毒
- Day 16: 分块注入 → 边界注入, 跨块攻击
- Day 17: Embedding 投毒 → 向量操纵, 检索劫持
- Day 18: 向量 DB → 持久化投毒, 来源认证
- Day 19: 三层防御 → 输入-检索-输出全链路
- Day 20: 红队测试 → 自动化扫描, 5类攻击
- Day 21: 实战项目 → 企业级安全 RAG

### Week 4: Agent 安全与部署运维
- Day 22: ReAct Agent → observation 注入, goal 劫持
- Day 23: MCP 安全 → 工具描述投毒, 返回值污染
- Day 24: 多 Agent → 记忆投毒, 横向移动
- Day 25: vLLM → 部署加固, 认证限流
- Day 26: 容器化 → Docker/K8s 安全, 最小权限
- Day 27: 红队实战 → Garak, PyRIT, 自动化评估
- Day 28: 面试准备 → 知识图谱, 模拟面试

## FDE 面试高频问题

### 技术问题
```python
INTERVIEW_QA = {
    "LLM 基础": [
        "解释 Self-Attention 的计算过程",
        "BPE 分词如何被利用做 token 边界注入？",
        "RLHF 如何影响模型安全？有什么局限性？",
        "KV Cache 投毒的原理和防御方案？",
        "如何检测和缓解 LLM 幻觉？",
    ],
    "Prompt Injection": [
        "Direct vs Indirect Injection 的区别？",
        "举例 3 种 jailbreak 技术并解释原理",
        "如何设计纵深防御来对抗 prompt injection？",
        "流式输出的安全挑战和解决方案？",
        "Function Calling 有哪些攻击面？",
    ],
    "RAG 安全": [
        "RAG 系统面临的主要安全威胁？",
        "如何防御间接注入攻击？",
        "向量数据库投毒如何检测和防御？",
        "描述安全 RAG 的三层防御架构",
        "如何对 RAG 系统做红队测试？",
    ],
    "Agent 安全": [
        "ReAct Agent 的攻击面有哪些？",
        "MCP 协议的安全风险？",
        "多 Agent 系统中如何防止横向移动？",
        "Agent 记忆投毒的原理和防御？",
        "如何设计 Agent 执行沙箱？",
    ],
    "部署运维": [
        "vLLM 的安全加固清单？",
        "LLM 容器化的安全最佳实践？",
        "如何监控 LLM 服务的安全状态？",
        "如何设计 LLM 服务的审计日志？",
        "Garak 和 PyRIT 的区别和适用场景？",
    ],
}

# 打印问题清单供复习
for topic, questions in INTERVIEW_QA.items():
    print(f"
### {topic}")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
```

### 项目展示话术
```python
PROJECTS = [
    {
        "name": "安全 LLM 推理服务 (Day 7)",
        "summary": "用 FastAPI + OpenAI 搭建带输入过滤、输出检查、速率限制、审计日志的 LLM 服务",
        "highlights": ["4层防御架构", "正则+语义双检测", "可配置规则引擎"],
        "interview_talking": "我在项目中实现了纵深防御策略，包含输入端的正则和编码检测、"
                            "输出端的敏感信息过滤，以及速率限制和完整审计日志。"
                            "这让我理解了生产级 LLM 服务的安全基线。",
    },
    {
        "name": "安全 API 网关 (Day 14)",
        "summary": "整合认证、多层过滤、限流、审计的生产级 LLM API 网关",
        "highlights": ["JWT+APIKey 双认证", "可配置规则引擎", "完整审计链路"],
        "interview_talking": "这个项目整合了第二周所有安全组件。我设计了 JWT 和 API Key 双模式认证，"
                            "可配置的规则引擎让安全策略可以热加载，审计日志支持事后追溯。",
    },
    {
        "name": "企业级安全 RAG (Day 21)",
        "summary": "包含文档安全扫描、三层防御 RAG、用户隔离、审计的完整应用",
        "highlights": ["三层防御", "用户隔离", "文档安全扫描"],
        "interview_talking": "这是最复杂的项目。我实现了文档上传安全扫描、三层防御的 RAG pipeline"
                            "（输入-检索-输出），以及多用户的数据隔离。这让我理解了企业级 AI 应用"
                            "的安全架构设计。",
    },
]

print("
=== 项目展示准备 ===")
for p in PROJECTS:
    print(f"
{p['name']}")
    print(f"  概述: {p['summary']}")
    print(f"  亮点: {', '.join(p['highlights'])}")
    print(f"  面试话术: {p['interview_talking']}")
```

## 安全分析


## 真实案例：面试被问"你 Agent 怎么做的"答得零散——知识图谱 + 模拟面试救回

**背景**：一个候选人面试 FDE，被问"你做的 Agent 怎么决策、怎么防循环、怎么处理工具失败"，他东一句西一句答得零散，面试官评价"知识点都有，但没体系，不像做过的"。挂了。

**问题**：知识是散的，没有串成体系。FDE 面试考的是"你能否系统讲清一个项目的技术决策链路"，零散回答显得"没做过、只是背的"。

**定位过程**：他复盘发现不是缺知识，是缺"结构化表达"。于是先画 FDE 知识图谱把散点连成线，再用模拟面试反复练"用结构讲项目"。

**做法**：用知识图谱把 30 天学的内容串成"项目→技术决策→坑"的链路，再用模拟面试问答练表达。
```python
# FDE知识图谱：把能力点串成可讲的项目链路
GRAPH = {
 "RAG项目": ["分块策略(Day7)","混合检索重排(Day8)","评测验收(Day9)","可溯源隔离(Day10)"],
 "Agent项目": ["ReAct循环(Day11)","Tool Calling校验(Day12)","多Agent制衡(Day13)","MCP集成(Day14)","意图路由(Day15)"],
 "部署项目": ["vLLM并发(Day16)","流式SSE(Day17)","Docker交付(Day18)","K8s自愈(Day19)","缓存降本(Day20)"],
 "安全项目": ["注入防御(Day22)","投毒防御(Day23)","红队(Day24)","纵深网关(Day25)"],
 "落地项目": ["价值翻译(Day26)","SPIN挖需求(Day27)","企微飞书集成(Day28)","LoRA微调(Day29)"],
}
# 每个项目配"技术决策链"模板：为什么这么做->关键坑->量化结果
STORY = {
 "Agent项目": {
   "为什么用ReAct": "要可解释的决策链路，面试能讲清每步",
   "关键坑": "不限max_steps会死循环烧token；工具参数不校验会被注入",
   "量化结果": "客服解决率30%->65%，简单请求路由后延迟4s->0.6s",
 },
}
# 模拟面试：随机抽项目+问题，强制用"背景-决策-坑-结果"结构答
import random
proj = random.choice(list(STORY))
print(f"模拟面试：详细讲讲你的{proj}")
# 答题框架：背景一句话 -> 关键技术决策(为什么) -> 踩过的坑 -> 量化结果
```

**结果**：他用知识图谱把 30 天内容串成 5 个可讲项目，每个按"背景-决策-坑-结果"练熟。二面再被问"你 Agent 怎么做的"，他直接用结构讲完决策链路和坑，面试官说"这个讲得有体系，是真做过的"。拿到 offer。

**踩坑**：第一版他背了一堆八股答案，被追问"为什么这么选"就接不上——八股没有"为什么"。改成每项都准备"技术决策理由+踩坑+数据"后，追问也能答。还有模拟面试他一个人对镜练没压力，后来用 AI 当面试官随机追问，逼自己临场组织结构，效果好得多。

**可复用经验**：面试前别只背八股，先用知识图谱把项目串成"背景-技术决策(为什么)-坑-量化结果"的链路结构，再用模拟面试练临场表达。**有体系地讲一个项目，胜过零散背十个知识点**——这是 FDE 面试从"显得背过"到"显得做过"的关键一跃，也是 30 天学习的收尾整合。
面试核心：能说清'需求→方案→构建→部署→安全→效果'完整链路，项目展示突出交付能力与安全意识。

## 进阶挑战

1. 录制 3 个项目的 demo 视频
2. 准备一份 1-page 的安全架构图
3. 找同学做模拟面试并录音回听

---

> 🎉 恭喜完成全部 42 天 FDE 交付课程！接下来整理项目集、准备面试话术。
