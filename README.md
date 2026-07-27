# FDE 每日学习计划

面向 AI FDE (Forward Deployed Engineer) 方向的 8 周 56 天学习计划，每天自动推送学习目标、推荐资料和 Demo 练习到 macOS 通知 + 企业微信。

## 课程概览

| 周次 | 主题 | 核心内容 | 安全 Demo |
|------|------|----------|-----------|
| 1 | LLM 基础 | Transformer、Tokenization、GPT 演进、开源模型 | Attention 权重注入分析、Token 边界绕过、Pickle 攻击 |
| 2 | Prompt Engineering | 提示工程、API 实战、Function Calling、Ollama | 5 种注入手法、CoT 越狱、API Key 泄露、工具劫持 |
| 3 | RAG 安全 | 间接注入、分块边界注入、Embedding 检测、向量投毒 | 间接注入实验、向量投毒检测、安全 RAG Pipeline |
| 4 | 高级 RAG 安全 | 混合检索攻击、Reranker 操纵、HyDE 攻击、路由劫持 | 混合检索投毒、安全重排序、企业级安全 RAG |
| 5 | Agent 安全 | ReAct 注入、工具注入、记忆投毒、MCP 投毒、沙箱 | Agent 注入实验、MCP 工具投毒、Agent 沙箱 |
| 6 | 多 Agent 安全 | 横向移动、LangGraph 攻击、HITL 绕过、取证 | 多 Agent 横向移动、HITL 绕过、行为取证 |
| 7 | 部署运维安全 | vLLM 加固、缓存投毒、遥测泄露、Docker 安全 | vLLM 安全加固、缓存投毒、Docker 加固 |
| 8 | 综合安全实战 | Prompt Injection 防御、OWASP Top 10、越狱测试 | Guardrails 实现、Garak/PyRIT 红队、面试准备 |

## 每日 Demo 格式

每天的计划包含三个部分：

1. **学习目标 + 推荐资料** — 明确今日重点和阅读材料
2. **Demo 练习** — 全部与安全挂钩的实战 demo
3. **复现步骤 + 保姆教程** — 可直接复制运行的完整代码和逐步说明

每个 demo 的 `tutorial` 字段包含完整代码、环境准备和安全分析，从零开始即可复现，无需额外翻文档。

## 快速开始

```bash
# 1. 安装定时任务（每天自动弹通知）
bash install.sh

# 2. 手动测试一次（看看今日计划长什么样）
python3 daily-plan.py

# 3. 手动测试并自动打开生成的文件
python3 daily-plan.py --open
```

## 配置

编辑 `config.json`：

```json
{
  "start_date": "2026-07-27",     // 开始日期，Day 1
  "push_time": "08:30",           // 每天推送时间
  "total_days": 56,               // 课程总天数
  "wechat_webhook": "https://..."  // 企业微信机器人 webhook，留空则只弹 macOS 通知
}
```

修改 `push_time` 后重新运行 `bash install.sh` 即可更新定时任务。去掉 `wechat_webhook` 的值可关闭企业微信推送。

## 文件结构

```
TO FDE/
├── curriculum.json     # 56 天课程数据
├── daily-plan.py       # 每日计划生成脚本（macOS 通知 + 企业微信推送）
├── config.json         # 开始日期与推送时间
├── install.sh          # 定时任务安装脚本
├── README.md           # 本文件
├── logs/               # 定时任务运行日志
└── 今日计划/            # 每日生成的计划文件
    └── Day-01-2026-07-27.md
```

## 常用命令

```bash
# 查看定时任务状态
launchctl list | grep fde

# 立即手动触发
python3 daily-plan.py --open

# 卸载定时任务
launchctl unload ~/Library/LaunchAgents/com.fde.daily-plan.plist

# 重新安装（改了时间或路径后）
bash install.sh
```

## 说明

- 定时任务通过 macOS launchd 运行，电脑开机即生效，不需要终端开着
- 每天到点会弹一个 macOS 通知 + Glass 提示音，计划文件自动生成在 `今日计划/` 目录
- 如果那天没开机，launchd 会在下次开机时补跑一次
- 所有 56 天的 Demo 练习都与安全挂钩，含完整复现步骤和保姆教程
- 课程基于你的安全背景（渗透测试 + CTF）设计，安全是贯穿 8 周的主线，不只是第 8 周
- 第 8 周完成 5 个可展示项目 + 知识图谱 + FDE 面试准备
