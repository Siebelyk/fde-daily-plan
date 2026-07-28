# FDE 岗位要求 vs 课程覆盖 — Gap 分析

> 基于 Boss 直聘 6 个不同 FDE 岗位 JD（7 张截图，其中 2 张为同一腾讯岗位重复）
> 生成时间：2026-07-28

---

## 一、岗位汇总（OCR 提取）

| # | 公司/产品 | 经验 | 核心技术栈 | 特殊要求 |
|---|----------|------|-----------|---------|
| 1-2 | 腾讯 WorkBuddy/CodeBuddy | 3年+ | Python/TS/Java≥2门, RAG, MCP, Agent, 上下文工程 | 云原生(Docker/K8s/CI-CD), 腾讯云认证, 出差驻场 |
| 3 | 飞书(Lark) AI | 应届~3年 | Python/SQL, 飞书产品(多维表格/aily/妙搭) | SaaS实施/客户成功, 配置调试, 消耗指标 |
| 4 | (未标注) 行业头部 | - | Agent架构, workflow, 意图识别, RAG | 私有化部署+Linux+容器, 政企/金融/能源/制造 |
| 5 | (未标注) 重点客户 | 2年+ | RAG, Agent编排, Python/Java, vLLM/SGLang | LangChain/LlamaIndex, 语料处理(EasyDataset/Data-Juicer), Post-Training(CPT/SFT/RL) |
| 6 | (未标注) | 3年+/1年AI | TS+React/Vue3全栈, RAG(向量库Pinecone/FAISS), Agent框架, Docker | SSE/WebSocket流式, 智谱GLM, 私有化部署 |
| 7 | (未标注) FDE工程师 | 1-3年 | Python, LangChain/Agent SDK, vibe coding | 211/985, 快速原型验证, Agent/工作流开发 |

---

## 二、JD 高频要求频次统计（6 个岗位）

| 要求项 | 出现次数 | 你课程是否覆盖 |
|--------|---------|--------------|
| **Python 编程** | 6/6 | ⚠️ 假设已会，无专门模块 |
| **RAG 全链路** | 6/6 | ✅ W3 有（但偏攻防，非交付构建） |
| **Agent / 多Agent / Workflow** | 6/6 | ⚠️ W4 有（但偏注入攻击，非开发交付） |
| **MCP** | 4/6 | ⚠️ Day23 有（但偏投毒攻击，非系统集成） |
| **Context/Prompt Engineering** | 5/6 | ❌ 无专门模块 |
| **LangChain/LlamaIndex 框架** | 4/6 | ❌ 仅作为"挑战"提及，无系统训练 |
| **客户沟通/需求拆解/驻场** | 6/6 | ❌ 仅 Day28 面试准备 |
| **Docker/K8s/容器化** | 4/6 | ✅ Day26 有（偏安全加固） |
| **私有化部署/Linux** | 3/6 | ⚠️ Day25 有（偏安全加固） |
| **vLLM/SGLang 推理引擎** | 2/6 | ⚠️ Day25 有 vLLM（偏加固），无 SGLang |
| **SSE/WebSocket 流式** | 2/6 | ⚠️ Day12 有（偏信息泄露） |
| **意图识别/Workflow编排** | 2/6 | ❌ 无 |
| **Post-Training 微调(CPT/SFT/RL)** | 1/6 | ❌ 无（仅 Day3 提 RLHF 概念） |
| **语料处理(EasyDataset/Data-Juicer)** | 1/6 | ❌ 无 |
| **前端全栈(TS/React/Vue3)** | 1/6 | ❌ 无 |
| **vibe coding/快速原型** | 1/6 | ❌ 无 |
| **AI 安全/攻防** | **0/6** | ✅✅ 课程 90% 都是（**但 JD 几乎不要求**） |

---

## 三、核心结论

### ⚠️ 最大问题：课程定位与岗位需求错配

你自己在上一条会话里说过 **"主要是 FDE，安全是附带的"**——但现在的 28 天课程正好相反：

- **课程 ≈ 90% AI 安全攻防 + 10% FDE 交付工程**
- **JD ≈ 60% 大模型应用开发交付 + 25% 客户落地沟通 + 15% 安全意识**

FDE = Forward Deployed Engineer，核心是**把 AI 能力落地交付到客户现场**。
JD 要的是能**构建 RAG / 开发 Agent / 用 MCP 打通系统 / 做工程化部署**的人，
安全是加分项，不是主线——**6 个岗位没有一个把"安全"列为必备要求**。

### ✅ 课程优势（保留）
- AI 安全纵深：Prompt Injection / Jailbreak / RAG 投毒 / Agent 注入 / MCP 投毒 / 红队
- 这是稀缺差异化能力，面试能加分，**但不应占 90% 篇幅**

### ❌ 关键缺口（按优先级）

| 优先级 | 缺口 | 影响 | 建议 |
|--------|------|------|------|
| **P0** | **Context/Prompt Engineering** | 5/6 岗位要求，课程无专门模块 | 新增 2-3 天：Prompt 模板库、上下文窗口管理、Few-shot/CoT、System Prompt 设计 |
| **P0** | **LangChain/LlamaIndex Agent 开发** | 4/6 要求，课程只当"挑战"提 | 新增 3-4 天：用 LangChain 构建 Agent、Tool Calling、Workflow 编排、LlamaIndex RAG |
| **P0** | **RAG 作为"构建能力"而非"攻击靶场"** | 6/6 要求 | 调整 W3：先教构建（向量库/检索/重排/引用），再教安全。现在只有攻击视角 |
| **P1** | **MCP 系统集成**（非投毒） | 4/6 要求 | Day23 补充：用 MCP 打通 CRM/ERP/OA 的集成实践，而不只是投毒实验 |
| **P1** | **Agent Workflow 编排 / 意图识别** | 2/6 要求 | 新增：多 Agent 协同、任务拆解、意图路由 |
| **P1** | **部署为"交付"而非"加固"** | 4/6 要求 | Day25-26 补充：不只是安全加固，而是从零部署一套可交付的 LLM 服务 |
| **P2** | **Post-Training 微调** | 1/6 要求 | 可选：CPT/SFT/LoRA 实践 |
| **P2** | **语料处理 / 数据工程** | 1/6 要求 | 可选：EasyDataset/Data-Juicer |
| **P2** | **前端全栈** | 1/6 要求 | 视目标岗位决定是否补 |

---

## 四、建议的课程重构方向

**方案 A（推荐）：扩到 6 周，前后补 FDE 核心**
- 第 0 周（新增）：FDE 工程基础 — Python 工程化、Prompt/Context Engineering、LangChain/LlamaIndex 入门
- 第 1-4 周（保留）：现有 28 天 AI 安全（作为差异化能力）
- 第 5 周（新增）：FDE 交付实战 — RAG 构建、Agent 开发交付、MCP 集成、端到端部署、客户场景模拟

**方案 B：重排现有 4 周，把安全压缩到 2 周**
- W1：LLM 基础 + Prompt/Context Engineering + LangChain
- W2：RAG 构建 + Agent 开发 + MCP 集成（交付视角）
- W3：AI 安全攻防（压缩精华版）
- W4：部署交付 + 红队 + 面试

---

## 五、面试可立刻改进的点

1. **准备 2-3 个"交付型"项目**：一个 RAG 知识库（带引用+重排）、一个 Agent 工作流（多工具协同）、一个 MCP 集成 demo。JD 反复要求"有落地案例/可演示项目"。
2. **简历突出"构建"而非"攻击"**：现有 demo 都是攻击/防御视角，面试官想看的是"你能帮客户搭出来"。
3. **补 LangChain 实战**：这是出现频次第二高的框架要求，课程里几乎是空白。
