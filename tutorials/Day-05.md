# Day 5：第一周实战：构建第一个可演示的 LLM 应用

> 🔵 FDE 工程基础与 LLM 原理 · 第 1 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-05.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-05.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 整合本周所学：API 封装 + Prompt 模板 + 上下文管理，端到端构建应用
2. 实现一个命令行多轮问答助手，可演示给客户看
3. 理解'可演示原型'对 FDE 的价值：用真实数据而非 PPT 验证方案

## 推荐资料

- 🗺️ 指南 [Gradio LLM 演示教程](https://www.gradio.app/guides/creating-a-chatbot-fast)
- 📚 文档 [LangChain LLM Chain 教程](https://python.langchain.com/docs/tutorials/llm_chain/)

## Demo 练习：端到端多轮问答助手（可演示原型）

第一周收尾：搭一个能多轮对话、能引用资料的助手原型。Gradio 一键出界面，直接能演示给客户/面试官看。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 3h |

### 复现步骤

1. 复用 Day4 的 LLMClient + Day5 的 PromptTemplate + Day6 的 ContextManager
2. 实现多轮交互循环，支持 /reset /cost /save 等命令
3. 打包成可运行入口，准备一份 demo 脚本话术

## 保姆教程

## 原理速览
FDE 的第一周目标：能拿出一个"可演示原型"。不是 PPT，是能跑、能看到真实输入输出的小工具。
本实验把前三天的组件拼成一个命令行 AI 助手，这就是你交付能力的最小闭环。

## 代码
```python
import sys

def count_tokens(t): return int(len(t)*1.5) if any(ord(c)>127 for c in t) else len(t)//4

class LLMClient:
    def __init__(self): self.cost=0.0; self.calls=0
    def chat(self, prompt):
        self.calls+=1; self.cost+=0.01
        return f"[mock] 已理解你的问题并给出专业解答"

class PromptTemplate:
    def __init__(self, t): self.t=t
    def render(self, **k): return self.t.format(**k)

class Assistant:
    """第一周实战：可演示的 AI 助手"""
    def __init__(self, name="企业助手"):
        self.name=name
        self.llm=LLMClient()
        self.ctx_mgr=ContextManager()
        self.sys=f"你是{name}，专业、简洁地回答问题。"
    def ask(self, q):
        prompt=self.sys+"\n\n历史: "+";".join(self.history[-3:])+"\n问: "+q
        ans=self.llm.chat(prompt)
        self.history.append(f"{q[:20]}→{ans[:20]}")
        return ans
    def reset(self): self.history=[]; return "已重置对话"

class ContextManager:
    def __init__(self): self.history=[]
    def add(self,q,a): self.history.append((q,a))

# 演示脚本
ast = Assistant("FDE 企业知识助手")
ast.ctx_mgr = ContextManager()
ast.history = []
print(f"=== {ast.name} 已就绪 ===")
demo_q = ["什么是 FDE？", "帮我推荐一个适合中小企业的 RAG 方案", "/cost", "/reset"]
for q in demo_q:
    if q.startswith("/cost"):
        print(f"  💰 累计调用 {ast.llm.calls} 次, 成本 ${ast.llm.cost:.2f}")
    elif q.startswith("/reset"):
        print("  🔄", ast.reset())
    else:
        ans = ast.ask(q)
        print(f"  👤 {q}\n  🤖 {ans}")
print("\n✅ 这是一个最小可演示原型，FDE 进客户现场就拿这种东西验证方案")
```
演示原型连接真实 API 时，避免终端回显泄露 Key；准备脱敏 demo 数据集防止客户数据外泄。
演示原型若连真实 API，注意别在客户面前泄露 API key（终端回显命令历史）。
建议演示用环境变量注入 key，并准备一份脱敏的 demo 数据集。

## 进阶挑战

1. 接入真实智谱 GLM API，把 mock 换成真实回答，跑通端到端
2. 用 FastAPI 给助手加一个 HTTP 接口，变成可被调用的服务
3. 录一段 3 分钟演示视频，练习用业务语言（非技术术语）讲解价值

---

## 明日预告

**Day 6：RAG 基础与架构**
> 🟢 RAG 构建与交付 · 第 2 周
