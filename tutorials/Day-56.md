# Day 56: FDE 面试准备与最终复习

> 综合安全实战 | 第 8 周

## Demo: 面试准备：FDE + AI 安全知识图谱与模拟面试

整理 8 周学习成果，制作知识图谱，准备 FDE 面试常见问题，完成模拟面试

- 难度：复习
- 预计时间：3.5h

## 复现步骤

- 1. 制作 8 周知识图谱
- 2. 整理 5 个安全项目
- 3. 准备 20 个高频面试题
- 4. 模拟面试练习
- 5. 制作个人技术简历亮点

## 保姆教程

## 8 周知识图谱

\`\`\`
Week 1-2: LLM 基础 + Prompt Engineering
  ├── Transformer/Attention 安全
  ├── Tokenization 注入
  ├── Prompt Injection (5种)
  ├── CoT 越狱
  ├── API 安全
  ├── Function Calling 劫持
  └── 三层防御客服

Week 3-4: RAG 安全
  ├── 间接注入
  ├── 分块边界注入
  ├── Embedding 注入检测
  ├── 向量投毒
  ├── 安全 RAG Pipeline
  ├── 混合检索攻击
  ├── Reranker 操纵
  ├── HyDE 攻击
  ├── 路由劫持
  └── 企业级安全 RAG

Week 5-6: Agent 安全
  ├── ReAct Agent 注入
  ├── 工具注入
  ├── 记忆投毒
  ├── Plan-and-Execute 劫持
  ├── MCP 工具投毒
  ├── Agent 沙箱
  ├── 多 Agent 横向移动
  ├── LangGraph 工作流攻击
  ├── HITL 绕过
  ├── Agent 取证
  ├── 失败模式降级
  └── Agent 安全架构

Week 7-8: 部署 + 综合
  ├── vLLM 安全部署
  ├── 缓存投毒
  ├── 遥测泄露
  ├── LLM-as-Judge 操纵
  ├── A/B 测试安全
  ├── Docker 加固
  ├── Prompt Injection 防御
  ├── OWASP LLM Top 10
  ├── 越狱测试
  ├── 模型窃取防护
  ├── Guardrails 中间件
  └── Garak/PyRIT 红队
\`\`\`

## 5 个安全项目整理

\`\`\`python
projects = [
    {
        "name": "安全加固版智能客服",
        "week": "W2",
        "skills": ["Prompt Injection 防御", "三层安全架构", "API 安全"],
        "github": "建议上传到GitHub",
        "interview_talk": "构建了含输入检测+工具分级+输出过滤的三层防御客服系统"
    },
    {
        "name": "安全 RAG 知识库",
        "week": "W3-4",
        "skills": ["间接注入防御", "向量投毒检测", "Embedding 异常检测", "企业级Web"],
        "github": "建议上传到GitHub",
        "interview_talk": "实现了含文档扫描+向量检测+三层防御+红队测试的安全RAG系统"
    },
    {
        "name": "安全 Agent 框架",
        "week": "W5",
        "skills": ["Agent 注入防御", "工具权限分级", "记忆安全", "沙箱隔离"],
        "github": "建议上传到GitHub",
        "interview_talk": "设计了含输入检测+工具分级+记忆过滤+沙箱+审计的安全Agent框架"
    },
    {
        "name": "安全 Multi-Agent 系统",
        "week": "W6",
        "skills": ["多Agent安全", "消息隔离", "HITL", "行为取证"],
        "github": "建议上传到GitHub",
        "interview_talk": "构建了含Agent隔离+消息过滤+审计追踪的安全多Agent协作系统"
    },
    {
        "name": "安全 LLM 部署方案",
        "week": "W7",
        "skills": ["vLLM加固", "Docker安全", "监控告警", "DevSecOps"],
        "github": "建议上传到GitHub",
        "interview_talk": "实现了含容器加固+反代认证+监控告警+日志审计的LLM安全部署"
    }
]

for p in projects:
    print(f"- {p['name']} (W{p['week']}): {p['interview_talk']}")
\`\`\`

## 20 个高频面试题

\`\`\`python
interview_questions = [
    # 基础
    "1. 什么是 Prompt Injection？如何防御？",
    "2. 直接注入和间接注入有什么区别？",
    "3. 解释 RAG 系统的安全风险",
    "4. 什么是向量投毒？如何检测？",
    # Agent
    "5. Agent 的安全风险有哪些？",
    "6. 如何设计安全的工具调用权限？",
    "7. 什么是 Agent 记忆投毒？",
    "8. 多 Agent 系统如何防止横向移动？",
    # 防御
    "9. 解释三层防御架构",
    "10. 什么是 Guardrails？如何实现？",
    "11. HITL 机制如何防止被绕过？",
    "12. 如何设计 Agent 沙箱？",
    # 部署
    "13. vLLM 服务有哪些安全风险？",
    "14. 如何安全部署 Docker 化 LLM 服务？",
    "15. 什么是缓存投毒？如何防御？",
    # 标准
    "16. OWASP LLM Top 10 你了解几个？",
    "17. 如何用 Garak 做 LLM 漏洞扫描？",
    "18. 什么是模型窃取攻击？如何防护？",
    # 综合
    "19. 你做过哪些 AI 安全项目？",
    "20. 作为 FDE，你如何在客户现场保障 AI 系统安全？",
]

for q in interview_questions:
    print(f"  {q}")
\`\`\`

## 简历亮点提取

\`\`\`markdown
## AI 安全与 FDE 能力

### 核心技能
- LLM 安全：Prompt Injection 防御、RAG 安全、Agent 安全
- 安全工具链：Garak、PyRIT、OWASP LLM Top 10
- 部署安全：Docker 加固、vLLM 部署、DevSecOps

### 项目经验
1. 安全 RAG 知识库系统（三层防御 + 红队测试）
2. 安全 Agent 框架（工具分级 + 沙箱 + 审计）
3. 安全 Multi-Agent 系统（消息隔离 + HITL + 取证）
4. 安全 LLM 部署方案（容器加固 + 监控告警）
5. 智能安全客服（注入检测 + 三层防御）

### 安全能力
- 独立完成 LLM 应用的安全评估与加固
- 熟悉 OWASP LLM Top 10 并能落地实施
- 具备 AI 红队测试经验（Garak + PyRIT）
\`\`\`

## 安全分析
8周从 LLM 基础到 AI 安全实战，5 个可展示项目 + 知识图谱 + 面试准备 = 完整的 FDE 安全求职准备
