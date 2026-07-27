# 我的FDE学习计划

> 面向 AI FDE (Forward Deployed Engineer) 方向的 28 天安全实战课程。
> 每天 = 理论 + 可复现安全 Demo + 保姆教程 + 安全分析 + 进阶挑战。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Days](https://img.shields.io/badge/Days-28-success)
![Focus](https://img.shields.io/badge/Focus-AI%20Security-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 什么是 FDE？

FDE (Forward Deployed Engineer) 是当下 AI 行业最热门的工程岗位之一。
它要求既懂模型原理、又懂工程部署、还要有安全意识——把 AI 能力安全地落到生产环境。
本课程从安全视角切入，通过 28 天高强度实战，帮你建立 AI 安全工程的完整知识体系。

## 课程特色

- **28 天 4 周**：从 LLM 原理到 Agent 安全，循序渐进
- **安全驱动**：每个 Demo 都是一个真实安全场景的复现
- **保姆教程**：每篇教程含完整代码、复现步骤、预期输出，可直接跑通
- **面试导向**：每周末设有面试题清单与项目展示话术
- **开源友好**：所有代码 MIT 协议，欢迎 Star / Fork / PR

## 适合人群

- 计算机/安全/AI 方向的在校生，想拿 AI 安全方向 Offer
- 有 Python 基础，想转向 AI 安全 / FDE 岗位的工程师
- 对 LLM 安全、Prompt Injection、RAG 安全感兴趣的学习者

## 前置要求

- Python 3.8+，能独立 `pip install` 和运行脚本
- 了解基本 ML 概念（向量、矩阵、softmax）
- 一台能联网的 macOS / Linux / WSL 环境

## 课程路线图

### 第 1 周：LLM 核心原理与安全基础
_从 Transformer 到推理服务，理解 LLM 底层原理并搭建第一个安全推理 API_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 1](tutorials/Day-01.md) | Transformer 与注意力机制 | Attention 权重可视化：定位 prompt injection 的高权重 token | 基础 |
| [Day 2](tutorials/Day-02.md) | Tokenization 与词嵌入 | Token 边界注入实验：用分词差异绕过安全过滤 | 基础 |
| [Day 3](tutorials/Day-03.md) | GPT 系列演进与对齐安全 | Base vs Instruct 模型安全行为对比实验 | 基础 |
| [Day 4](tutorials/Day-04.md) | 推理优化与 KV Cache 安全 | KV Cache 投毒实验：模拟缓存污染攻击 | 进阶 |
| [Day 5](tutorials/Day-05.md) | 幻觉检测与安全风险 | 幻觉检测器：基于自一致性检测幻觉 | 基础 |
| [Day 6](tutorials/Day-06.md) | 开源模型生态与安全评估 | 模型安全评分系统：多维度评估开源模型安全性 | 进阶 |
| [Day 7](tutorials/Day-07.md) | 第一周实战：安全 LLM 推理服务 | 安全 LLM 推理服务：从零搭建带防护的 API | 项目 |

### 第 2 周：Prompt Injection 攻防实战
_从经典 Prompt Injection 到 Jailbreak 检测，系统掌握 LLM 输入侧攻防_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 8](tutorials/Day-08.md) | Prompt Injection 攻防入门 | Prompt Injection 攻击库：从经典到现代 | 进阶 |
| [Day 9](tutorials/Day-09.md) | Jailbreak 与越狱技术 | 越狱技术复现与防御分析 | 进阶 |
| [Day 10](tutorials/Day-10.md) | API 安全实战 | API 安全攻防：从 Key 泄露到 SSRF | 进阶 |
| [Day 11](tutorials/Day-11.md) | Function Calling 与工具劫持 | Function Calling 工具劫持实验 | 进阶 |
| [Day 12](tutorials/Day-12.md) | 流式输出与信息泄露 | 流式输出信息泄露实验 | 进阶 |
| [Day 13](tutorials/Day-13.md) | 防御工程：输入过滤、输出检查与 Guardrails | 多层防御工程：从规则到语义的完整防护链 | 进阶 |
| [Day 14](tutorials/Day-14.md) | 第二周实战：安全 API 网关 | 安全 API 网关：生产级 LLM 服务防护 | 项目 |

### 第 3 周：RAG 安全全链路
_从文档投毒到三层防御 RAG，打通检索增强生成全链路安全_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 15](tutorials/Day-15.md) | RAG 基础与间接注入 | 间接注入实验：通过 RAG 文档触发指令覆盖 | 进阶 |
| [Day 16](tutorials/Day-16.md) | 文档分块与分块边界注入 | 分块边界注入实验：利用分块策略绕过安全检查 | 进阶 |
| [Day 17](tutorials/Day-17.md) | Embedding 安全与投毒检测 | Embedding 投毒实验：操纵检索结果 | 进阶 |
| [Day 18](tutorials/Day-18.md) | 向量数据库安全与投毒攻击 | 向量数据库投毒攻击：从注入到持久化 | 进阶 |
| [Day 19](tutorials/Day-19.md) | 安全 RAG Pipeline：三层防御架构 | 安全 RAG Pipeline：三层防御架构实现 | 进阶 |
| [Day 20](tutorials/Day-20.md) | RAG 红队测试与自动化扫描 | RAG 红队测试：自动化安全扫描 | 进阶 |
| [Day 21](tutorials/Day-21.md) | 第三周实战：企业级安全 RAG | 企业级安全 RAG：完整项目 | 项目 |

### 第 4 周：Agent 安全与部署运维
_从 Agent 注入到生产部署审计，覆盖 MCP、多智能体与运维安全_

| Day | 主题 | Demo | 难度 |
|-----|------|------|------|
| [Day 22](tutorials/Day-22.md) | ReAct Agent 原理与注入攻击 | ReAct Agent 注入攻击复现 | 进阶 |
| [Day 23](tutorials/Day-23.md) | MCP 协议安全与工具投毒 | MCP 工具投毒实验：操纵工具描述劫持 LLM | 进阶 |
| [Day 24](tutorials/Day-24.md) | 多 Agent 横向移动与记忆投毒 | 多 Agent 横向移动：记忆投毒与链式攻击 | 进阶 |
| [Day 25](tutorials/Day-25.md) | vLLM 服务安全与模型部署加固 | vLLM 安全部署实验：从默认配置到安全加固 | 进阶 |
| [Day 26](tutorials/Day-26.md) | 容器化 LLM 服务安全 | 容器化 LLM 安全：从 Dockerfile 到 K8s 加固 | 进阶 |
| [Day 27](tutorials/Day-27.md) | 红队实战：Garak 与 PyRIT 自动化测试 | 红队实战：用 Garak + PyRIT 做 LLM 安全评估 | 进阶 |
| [Day 28](tutorials/Day-28.md) | FDE 面试准备与最终复习 | FDE 面试准备：知识图谱与模拟面试 | 复习 |

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/Siebelyk/fde-daily-plan.git
cd fde-daily-plan

# 查看任意一天的教程
cat tutorials/Day-01.md

# 重新生成所有文件（修改课程后）
python3 build_curriculum.py
```

## 在线运行 Notebook

每个 Demo 都有对应的 Jupyter Notebook，支持一键在 Google Colab 中运行：

- 零环境配置：打开 Colab 链接即可运行，无需本地安装任何依赖
- 逐 cell 执行：每个步骤可以单独运行，看到中间输出
- 可视化友好：matplotlib 图表直接在 notebook 中展示

| Day | Notebook | Day | Notebook |
|-----|----------|-----|----------|
| [Day 1](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-01.ipynb) | [Day 15](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-15.ipynb) |
| [Day 2](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-02.ipynb) | [Day 16](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-16.ipynb) |
| [Day 3](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-03.ipynb) | [Day 17](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-17.ipynb) |
| [Day 4](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-04.ipynb) | [Day 18](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-18.ipynb) |
| [Day 5](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-05.ipynb) | [Day 19](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-19.ipynb) |
| [Day 6](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-06.ipynb) | [Day 20](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-20.ipynb) |
| [Day 7](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-07.ipynb) | [Day 21](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-21.ipynb) |
| [Day 8](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-08.ipynb) | [Day 22](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-22.ipynb) |
| [Day 9](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-09.ipynb) | [Day 23](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-23.ipynb) |
| [Day 10](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-10.ipynb) | [Day 24](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-24.ipynb) |
| [Day 11](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-11.ipynb) | [Day 25](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-25.ipynb) |
| [Day 12](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-12.ipynb) | [Day 26](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-26.ipynb) |
| [Day 13](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-13.ipynb) | [Day 27](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-27.ipynb) |
| [Day 14](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-14.ipynb) | [Day 28](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-28.ipynb) |

## 核心项目展示

课程中你会完成以下可写进简历的项目：

| 项目 | 对应 Day | 核心能力 |
|------|----------|----------|
| 安全 LLM 推理服务 | Day 7 | 输入过滤 + 输出检查 + 速率限制 + 审计 |
| 安全 API 网关 | Day 14 | JWT + APIKey 双认证 + 规则引擎 + 审计链路 |
| 企业级安全 RAG | Day 21 | 文档安全扫描 + 三层防御 + 用户隔离 |
| 生产部署安全审计 | Day 28 | 配置审计 + 容器安全 + 综合评估 |

## 可选：每日自动推送

如果你希望每天自动收到学习计划推送（macOS 通知 + 企业微信），可以配置定时任务：

```bash
# 1. 复制配置模板并填入你的企业微信 webhook
cp config.example.json config.json

# 2. 设置 crontab 每天 08:30 推送
crontab -e  # 添加：30 8 * * * cd /path/to/fde-daily-plan && python3 daily-plan.py
```

> 此功能为可选的个人学习辅助，课程核心内容不依赖推送配置。

## 学习进度打卡

复制下面的清单到你的笔记里，每完成一天打个勾：

```markdown
- [ ] Day 01  Transformer 与注意力机制
- [ ] Day 02  Tokenization 与词嵌入
- [ ] Day 03  GPT 系列演进与对齐安全
- [ ] Day 04  推理优化与 KV Cache 安全
- [ ] Day 05  幻觉检测与安全风险
- [ ] Day 06  开源模型生态与安全评估
- [ ] Day 07  第一周实战：安全 LLM 推理服务
- [ ] Day 08  Prompt Injection 攻防入门
- [ ] Day 09  Jailbreak 与越狱技术
- [ ] Day 10  API 安全实战
- [ ] Day 11  Function Calling 与工具劫持
- [ ] Day 12  流式输出与信息泄露
- [ ] Day 13  防御工程：输入过滤、输出检查与 Guardrails
- [ ] Day 14  第二周实战：安全 API 网关
- [ ] Day 15  RAG 基础与间接注入
- [ ] Day 16  文档分块与分块边界注入
- [ ] Day 17  Embedding 安全与投毒检测
- [ ] Day 18  向量数据库安全与投毒攻击
- [ ] Day 19  安全 RAG Pipeline：三层防御架构
- [ ] Day 20  RAG 红队测试与自动化扫描
- [ ] Day 21  第三周实战：企业级安全 RAG
- [ ] Day 22  ReAct Agent 原理与注入攻击
- [ ] Day 23  MCP 协议安全与工具投毒
- [ ] Day 24  多 Agent 横向移动与记忆投毒
- [ ] Day 25  vLLM 服务安全与模型部署加固
- [ ] Day 26  容器化 LLM 服务安全
- [ ] Day 27  红队实战：Garak 与 PyRIT 自动化测试
- [ ] Day 28  FDE 面试准备与最终复习
```

## 贡献

欢迎提交 Issue 和 PR：修正错误、补充资料、新增 Demo。

## License

MIT License — 自由使用，注明出处即可。
