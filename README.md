# 我的FDE学习计划

> 面向 AI FDE (Forward Deployed Engineer) 方向的 **42 天交付主线**实战课程。
> FDE 交付为主线（5 周）+ AI 安全为差异化能力（1 周）。
> 每天 = 理论 + 可复现交付 Demo + 保姆教程 + 安全意识 + 进阶挑战。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Days](https://img.shields.io/badge/Days-42-success)
![Focus](https://img.shields.io/badge/Focus-FDE%20Delivery-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 什么是 FDE？

FDE (Forward Deployed Engineer) 是 AI 行业最热门的工程岗位之一：
**把 AI 能力落地交付到客户现场**——既懂模型应用、又懂工程部署、还能对接客户业务。
本课程以 FDE 交付为主线，通过 42 天高强度实战，建立从构建到部署到客户落地的完整能力体系。

## 课程特色

- **交付主线**：5 周 FDE 交付工程（RAG 构建/Agent 开发/部署/客户落地），1 周 AI 安全差异化
- **JD 对标**：基于 6 个真实 FDE 岗位 JD 设计，覆盖 RAG/Agent/MCP/LangChain/部署/沟通高频要求
- **可演示**：每天 Demo 都是可复现、可演示给客户的交付物，而非纯理论
- **安全意识**：交付全程嵌入安全检查点，第 5 周系统攻防

## 课程路线图


### 第 1 周：🔵 FDE 工程基础与 LLM 原理
_从 FDE 岗位认知到 LLM 原理，掌握 API/Prompt/Context 工程，构建第一个可演示应用_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 1](tutorials/Day-01.md) | FDE 岗位认知与开发环境搭建 | FDE 能力雷达图 + 环境自检脚本 | 入门 |
| [Day 2](tutorials/Day-02.md) | 理解 LLM：Attention 与 Token 计费 | Attention 可视化 + Token 成本分析 | 入门 |
| [Day 3](tutorials/Day-03.md) | API 调用与 Prompt 工程 | 多厂商 API 封装 + Prompt 模板库 | 入门 |
| [Day 4](tutorials/Day-04.md) | Context Engineering：上下文管理 | 上下文预算管理器 + 多轮记忆策略 | 基础 |
| [Day 5](tutorials/Day-05.md) | 第一周实战：搭一个能演示的 LLM 助手 | Gradio 多轮对话助手（可写简历的项目） | 基础 |

### 第 2 周：🟢 RAG 构建与交付
_从分块到向量库到重排评测，构建可交付级 RAG 知识库（含安全检查点）_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 6](tutorials/Day-06.md) | RAG 入门：30 行跑通检索增强 | 最简 RAG 闭环 + RAG vs 微调决策 | 入门 |
| [Day 7](tutorials/Day-07.md) | 分块策略与向量库构建 | 分块策略对比 + Embedding 向量库 | 基础 |
| [Day 8](tutorials/Day-08.md) | 混合检索 + 重排 + 引用回溯 | BM25+向量混合检索 + Cross-Encoder 重排 | 进阶 |
| [Day 9](tutorials/Day-09.md) | RAG 评测与安全检查 | RAG 评测 Pipeline + 间接注入防御 | 进阶 |
| [Day 10](tutorials/Day-10.md) | 第二周实战：交付级 RAG 知识库 | 企业级 RAG 知识库（可演示产品） | 项目 |

### 第 3 周：🟣 Agent 开发与 MCP 集成
_从 ReAct Agent 到 LangChain 到 MCP，开发并编排多 Agent 业务工作流_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 11](tutorials/Day-11.md) | Agent 入门：ReAct 范式 | ReAct Agent 构建 + 攻击面认知 | 基础 |
| [Day 12](tutorials/Day-12.md) | LangChain 与 Function Calling | Tool Calling Agent + 安全工具开发 | 基础 |
| [Day 13](tutorials/Day-13.md) | 多 Agent 协同与 Workflow 编排 | LangGraph 多 Agent 业务工作流 | 进阶 |
| [Day 14](tutorials/Day-14.md) | MCP 协议与系统集成 | MCP 打通 CRM/ERP/OA 集成 | 进阶 |
| [Day 15](tutorials/Day-15.md) | 意图路由与多 Agent 实战 | 意图路由器 + 检索-写作-审核工作流 | 进阶 |

### 第 4 周：🟠 部署交付与生产化
_从 vLLM 部署到 K8s 到监控优化，交付生产级 LLM 服务_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 16](tutorials/Day-16.md) | 推理引擎部署：vLLM 与 SGLang | vLLM 服务搭建 + SGLang 对比 | 进阶 |
| [Day 17](tutorials/Day-17.md) | 流式输出：SSE 实时返回 | SSE 流式接口实现 | 基础 |
| [Day 18](tutorials/Day-18.md) | Docker 容器化交付 | Dockerfile 打包 + 镜像分发 | 基础 |
| [Day 19](tutorials/Day-19.md) | K8s 部署与 LLM 服务监控 | K8s 部署 YAML + Prometheus 监控 | 进阶 |
| [Day 20](tutorials/Day-20.md) | 性能与成本优化 | 语义缓存 + 模型路由 + 成本报告 | 进阶 |
| [Day 21](tutorials/Day-21.md) | 第四周实战：生产级 LLM 服务 | FastAPI+流式+缓存+监控 骨架 | 项目 |

### 第 5 周：🔴 AI 安全攻防（差异化能力）
_Prompt Injection/RAG投毒/Agent注入/红队，构建安全 LLM 网关（差异化能力）_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 22](tutorials/Day-22.md) | Prompt Injection 与 API 安全 | Injection 攻击库 + API 安全加固 | 进阶 |
| [Day 23](tutorials/Day-23.md) | RAG 安全：投毒与防御 | 文档投毒复现 + 检索链路防御 | 进阶 |
| [Day 24](tutorials/Day-24.md) | Agent 注入与红队实战 | Agent 注入靶场 + Garak/PyRIT 红队 | 进阶 |
| [Day 25](tutorials/Day-25.md) | 多层防御与安全网关 | 输入过滤 + 输出审查 + 护栏网关 | 项目 |

### 第 6 周：🟡 客户落地实战与面试
_从交付方法论到行业方案到客户沟通，完成面试冲刺_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 26](tutorials/Day-26.md) | FDE 交付流程与行业方案 | 交付清单 + 政企/金融/制造方案模板 | 基础 |
| [Day 27](tutorials/Day-27.md) | 客户沟通与方案设计 | SPIN 需求挖掘 + 价值翻译 + 异议处理 | 基础 |
| [Day 28](tutorials/Day-28.md) | 企微/飞书生态集成 | 企微机器人推送 + 飞书多维表格写入 | 基础 |
| [Day 29](tutorials/Day-29.md) | 模型微调：SFT 与 LoRA | LLaMA-Factory SFT + 语料处理 | 进阶 |
| [Day 30](tutorials/Day-30.md) | 面试冲刺：知识图谱与模拟面试 | FDE 知识图谱 + 模拟面试演练 | 基础 |

## 快速开始

```bash
git clone https://github.com/Siebelyk/fde-daily-plan.git
cd fde-daily-plan
cat tutorials/Day-01.md   # 查看任意一天教程
```

## 每日推送

配置 `config.json` 后运行 `install.sh` 安装定时任务，每天自动推送学习计划到企业微信。
