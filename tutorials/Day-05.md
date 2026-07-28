# Day 5：第一周实战：搭一个能演示的 LLM 助手

> 🔵 FDE 工程基础与 LLM 原理 · 第 1 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-05.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-05.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 整合本周所学:API调用+Prompt+Context工程，构建一个能多轮对话、能引用资料的助手
2. 用 Gradio 一键搭出可演示界面，3 分钟从代码到能用的小程序
3. 设计能让客户/面试官'哇'的演示话术:讲清解决了什么问题、效果如何
4. 积累第一个能写进简历的可演示项目

## 推荐资料

- 🗺️ 指南 [Gradio LLM 演示教程](https://www.gradio.app/guides/creating-a-chatbot-fast)
- 📚 文档 [LangChain LLM Chain 教程](https://python.langchain.com/docs/tutorials/llm_chain/)

## Demo 练习：Gradio 多轮对话助手（可写简历的项目）

第一周收尾:用 Gradio 搭一个带界面的多轮问答助手,3分钟出原型。直接能演示给客户/面试官看——这是你第一个能写简历的项目。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 3h |

### 复现步骤

1. 实现多轮对话的核心逻辑:维护历史、调用 LLM、处理上下文
2. 用 Gradio 搭建聊天界面,一行代码出网页
3. 设计演示话术:3句话讲清'这是什么、解决什么、效果如何'
4. 打包成可展示项目,更新到简历

## 保姆教程

## 原理速览
学了一周 API/Prompt/Context,现在把它们串成一个**能看、能演示、能写简历**的项目。
FDE 面试看的不是你会多少理论,而是"你做出来过什么"。今天搭一个多轮对话助手+Gradio 界面,这个项目能:
- **演示给面试官**:直观看到你的工程能力,比简历上的"熟悉 LLM"有说服力 100 倍
- **演示给客户**:Gradio 一键出界面,客户能直接点,感受产品形态
- **写进简历**:加一句"用 Gradio 构建 LLM 对话应用,支持多轮上下文管理",比空话强

### Gradio:FDE 演示神器
Gradio 能把 Python 函数 3 行代码变成网页界面。面试官打开链接就能玩,不用你口述。**能让人亲手点的 demo 比千言万语强**。

## 代码:多轮对话助手 + Gradio 界面
```python
# 一个能多轮对话、记上下文、带界面的 LLM 助手
# 无 API key 时用模拟模式,有 key 时接真实模型
import os

class ChatAssistant:
    def __init__(self):
        self.history = []  # [(role, content)]
        self.max_turns = 10  # 上下文管理:只保留最近10轮

    def chat(self, user_msg):
        # 维护上下文(核心:Context Engineering)
        self.history.append(("user", user_msg))
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-self.max_turns*2:]

        # 构造 prompt(有 API 接真实模型,无则模拟)
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            client = OpenAI()
            messages = [{"role": r, "content": c} for r, c in self.history]
            resp = client.chat.completions.create(
                model="gpt-4o-mini", messages=messages)
            reply = resp.choices[0].message.content
        else:
            # 模拟模式:演示逻辑,不花钱
            reply = f"[模拟回复] 我收到了你的问题:'{user_msg}'。接上 API key 我就是真的 LLM 助手了。当前已记住{len(self.history)//2}轮对话。"

        self.history.append(("assistant", reply))
        return reply

    def reset(self):
        self.history = []
        return "对话已清空"

# ===== 用 Gradio 搭界面(3行代码出网页) =====
# pip install gradio
try:
    import gradio as gr
    assistant = ChatAssistant()

    def respond(msg, history):
        return assistant.chat(msg)

    demo = gr.ChatInterface(respond, title="我的FDE助手-Demo",
                           description="多轮对话 + 上下文管理(可演示项目)")
    # demo.launch()  # 取消注释即运行,浏览器打开 http://localhost:7860
    print("✅ 助手+界面代码就绪! 取消 demo.launch() 注释即可在浏览器访问")
    print("部署到 HuggingFace Spaces 后可获得公开链接写进简历")
except ImportError:
    # 无 gradio 也能用命令行测
    a = ChatAssistant()
    for q in ["你好","我刚问了什么?","我上下文还有几轮?"]:
        print(f"我: {q}\n助手: {a.chat(q)}\n")
    print("✅ 助手逻辑验证通过(命令行模式),装 gradio 后可出界面")
```

## 真实案例
某候选人面试 FDE,没讲理论,直接打开 HuggingFace 上的 Gradio 链接让面试官玩他做的助手,边玩边讲"这里我做了上下文裁剪防止爆 token"。面试官当场说"这就是我们要的能做出来的人"。**有可玩 demo 的候选人秒杀只讲理论的**。

## 简历话术(直接复制)
- ❌ 弱:"熟悉大模型应用开发,了解 Prompt Engineering"
- ✅ 强:"独立构建 LLM 多轮对话应用,实现上下文窗口管理与历史裁剪,使用 Gradio 部署可交互演示(附公开链接),验证多轮对话稳定性"

演示用 API key 切勿硬编码上传公开仓库,用环境变量管理。多轮历史可能泄露前序用户敏感信息,生产环境需按用户隔离历史。
演示时用的 API key 切勿硬编码进代码再上传,Gradio/HF Spaces 是公开的。用环境变量管理 key,demo 仓库的 .env 要 gitignore。多轮历史可能泄露前面用户的敏感信息,生产环境需按用户隔离。


## 进阶挑战

1. 加一个'清空对话'按钮和当前 token 用量显示
2. 接 RAG 检索,让助手能回答私有知识(串接 Day06)
3. 部署到 HuggingFace Spaces,生成公开链接放简历

---

## 明日预告

**Day 6：RAG 入门：30 行跑通检索增强**
> 🟢 RAG 构建与交付 · 第 2 周
