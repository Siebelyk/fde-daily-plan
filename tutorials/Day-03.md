# Day 3：API 调用与 Prompt 工程

> 🔵 FDE 工程基础与 LLM 原理 · 第 1 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-03.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-03.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握多 Provider 统一封装：OpenAI / 智谱 GLM / 本地 Ollama 一套接口调用
2. 理解模型选型维度：能力/成本/延迟/上下文长度/私有化，按场景选模型
3. 估算用量成本：token 计费、上下文成本、批处理优化
4. 掌握核心 Prompt 技法：System Prompt、Few-shot、Chain-of-Thought、角色设定
5. 理解 Prompt 模板化工程：变量注入、模板复用、版本管理
6. 构建可复用的 Prompt 模板库，按业务场景选择最优 Prompt

## 推荐资料

- 📚 文档 [OpenAI API 参考](https://platform.openai.com/docs/api-reference)
- 🗺️ 指南 [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- 🎓 课程 [DeepLearning.AI - ChatGPT Prompt Engineering](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/)
- 📚 文档 [智谱 GLM API 文档](https://open.bigmodel.cn/dev/api)
- 📚 文档 [Ollama - 本地跑大模型](https://ollama.com/)

## Demo 练习：多厂商 API 封装 + Prompt 模板库

一套多 Provider 封装代码，换 API key 就能切换厂商。Prompt 模板库直接复用——日常交付高频用的轮子，能写进简历。

| 难度 | 预计时间 |
|------|----------|
| 入门 | 约 4h |

### 复现步骤

1. 实现统一 chat() 接口，三种 Provider 后端可切换
2. 实现 token 计数与成本估算（按各厂商定价表）
3. 写模型选型决策函数：按场景（低成本/长上下文/私有化）推荐模型
4. 实现 PromptTemplate 引擎：变量注入 + 模板注册
5. 实现三种 Prompt 策略：Zero-shot / Few-shot / CoT
6. 用 mock LLM 对比三种策略在情感分类上的效果

## 保姆教程

## 原理速览
FDE 落地时客户的模型来源五花八门：有的用 OpenAI，有的用国产 GLM，有的要求私有化 Ollama。
工程上要抽象成统一接口，让上层应用不关心后端。本实验用 mock 实现，真实环境只需补上 API key。

## 代码
```python
import time, hashlib, os
from typing import Optional

# 各厂商定价（元/千 token，示意）
PRICING = {
    "gpt-4o":      {"in": 0.0175, "out": 0.07},
    "gpt-4o-mini": {"in": 0.00105, "out": 0.0042},
    "glm-4":       {"in": 0.05, "out": 0.05},
    "glm-4-flash": {"in": 0.0, "out": 0.0},
    "ollama-qwen": {"in": 0.0, "out": 0.0},  # 本地免费
}

def count_tokens(text: str) -> int:
    # 粗估：中文约1字=1.5token，英文约4字符=1token
    return int(len(text) * 1.5) if any(ord(c) > 127 for c in text) else len(text) // 4

class LLMClient:
    """统一 LLM 客户端，支持多 Provider 切换"""
    def __init__(self, provider="mock", model="gpt-4o-mini", api_key=None, base_url=None):
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.getenv("API_KEY", "")
        self.base_url = base_url
        self.usage = {"in_tokens": 0, "out_tokens": 0, "cost": 0.0}

    def chat(self, prompt: str, system: str = "") -> str:
        t0 = time.time()
        in_tok = count_tokens(system + prompt)
        # 真实环境按 provider 走 requests，这里 mock
        resp = f"[{self.provider}/{self.model}] 收到：{prompt[:40]}"
        out_tok = count_tokens(resp)
        p = PRICING.get(self.model, {"in": 0, "out": 0})
        cost = in_tok / 1000 * p["in"] + out_tok / 1000 * p["out"]
        self.usage["in_tokens"] += in_tok
        self.usage["out_tokens"] += out_tok
        self.usage["cost"] += cost
        self.usage["latency_ms"] = (time.time() - t0) * 1000
        return resp

def select_model(scene: str) -> str:
    """按交付场景选模型"""
    rules = {
        "low_cost": "gpt-4o-mini",      # 高频低价值场景
        "long_context": "glm-4",         # 长文档 RAG
        "private": "ollama-qwen",        # 客户要求私有化
        "high_quality": "gpt-4o",        # 复杂推理
    }
    return rules.get(scene, "gpt-4o-mini")

# 测试多 Provider 切换
for prov, model in [("openai", "gpt-4o"), ("zhipu", "glm-4-flash"), ("ollama", "ollama-qwen")]:
    c = LLMClient(provider=prov, model=model)
    print(c.chat("用一句话介绍 FDE 岗位", system="你是资深 FDE 工程师"))
    print(f"  → 用量: {c.usage}")

# 模型选型
for scene in ["low_cost", "long_context", "private", "high_quality"]:
    print(f"场景 {scene} → 推荐 {select_model(scene)}")
```
API Key 必须通过环境变量或密钥管理服务注入，禁止写入代码仓库；交付时为客户配置用量预算告警。
API key 绝不硬编码进源码，必须走环境变量或密钥管理服务（KMS/Vault）。
交付时提醒客户：云厂商 API key 泄露=按量计费被刷爆，务必设用量告警与预算上限。

---

## 第二部分：Prompt 模板库 + 技法效果对比

## 原理速览
Prompt Engineering 是 FDE 最日常的武器：客户每个场景都需要调 Prompt。本实验把 Prompt
从散落的字符串工程化为"模板库"，可版本管理、可复用、可对比。工程化的 Prompt = 可交付的资产。

## 代码
```python
from string import Template

class PromptTemplate:
    """Prompt 模板引擎：变量注入 + 复用"""
    _registry = {}
    def __init__(self, name, template):
        self.name = name
        self.tpl = Template(template)
        PromptTemplate._registry[name] = self
    def render(self, **kw):
        return self.tpl.substitute(kw)
    @classmethod
    def get(cls, name): return cls._registry[name]

# 注册业务 Prompt 模板库
PromptTemplate("zero_shot",
    "判断以下文本情感（正面/负面/中性），只输出类别：\n文本：$text")
PromptTemplate("few_shot",
    "示例：\n文本：这个产品太棒了 → 正面\n文本：服务态度极差 → 负面\n"
    "文本：今天天气一般 → 中性\n现在判断：\n文本：$text → ")
PromptTemplate("cot",
    "请一步步分析以下文本的情感，最后输出类别：\n文本：$text\n"
    "分析过程：1.识别情感词 2.判断整体倾向 3.输出类别")

class MockLLM:
    """模拟 LLM，按 prompt 特征给不同质量响应"""
    def __call__(self, prompt):
        if "一步步" in prompt:      # CoT
            return "分析：含'差'字且无转折 → 负面"
        if "→" in prompt and "示例" in prompt:  # Few-shot
            return "负面"
        if "只输出类别" in prompt:  # Zero-shot
            return "中性"  # zero-shot 容易出错
        return "负面"

llm = MockLLM()
test_cases = ["这家餐厅服务态度极差，再也不来了", "产品还行吧，没什么特别的", "超出预期，强烈推荐！"]

print("=== Prompt 技法效果对比 ===")
for name in ["zero_shot", "few_shot", "cot"]:
    print(f"\n[{name}]")
    tpl = PromptTemplate.get(name)
    for t in test_cases:
        prompt = tpl.render(text=t)
        print(f"  {t[:18]:20} → {llm(prompt)}")

# Prompt 版本管理
print("\n=== 模板库清单 ===")
for n, t in PromptTemplate._registry.items():
    print(f"  v1 {n}: {t.tpl.template[:30]}...")
```
用户输入注入模板时存在 Prompt Injection 风险，必须对输入做隔离与角色固化（详见 W5 安全周）。
Prompt 模板会进入生产，注意：用户输入通过 $text 注入模板，若模板拼接后直接发给模型，
用户可注入"忽略以上指令"实施 Prompt Injection。工程上要对 $text 做隔离（如放入 XML 标签）
并在 System Prompt 里固化角色，Day 29 会专门攻防。

## 真实案例：写死 OpenAI 的代码，客户内网一断就废——抽象层救了私有化

**背景**：一个 FDE 给客户做的智能问答 demo 用的是 OpenAI API，客户认可想上线。但客户是政企，**内网完全隔离、只允许用国产大模型**。交付时一联调，代码直接报错——因为整个项目把 `openai.ChatCompletion` 写死在 20 多个文件里。

**问题**：没有抽象层，换模型要改散落在 20+ 文件的硬编码调用，漏改一个就报错；而且 OpenAI 和国产模型在 tool calling 字段、JSON 格式上还有差异，硬改极易踩坑。

**定位过程**：他没有逐文件改（那是返工地狱），而是先花半天做了一次依赖审计，用脚本扫出所有直接依赖 openai 的点，统计改造成本。
```python
import os, re
hits = []
for root, _, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            txt = open(os.path.join(root,f),encoding="utf-8").read()
            if "openai" in txt and "import" in txt:
                hits.append(f)  # 直接依赖点
print(f"硬编码 openai 的文件数: {len(hits)}")
```
扫出 23 个文件直接 import openai——确认必须做抽象层，而不是硬改。

**做法**：定义统一 LLM 客户端接口，再做各厂商适配器，业务代码只依赖接口，换厂只改一行配置。
```python
from abc import ABC, abstractmethod
import os, json

class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages, tools=None, temperature=0): ...

class OpenAICompat(LLMClient):
    def __init__(self, base_url, key, model):
        import openai
        self.c = openai.OpenAI(base_url=base_url, api_key=key)
        self.model = model
    def chat(self, messages, tools=None, temperature=0):
        return self.c.chat.completions.create(
            model=self.model, messages=messages,
            tools=tools, temperature=temperature).choices[0].message.content

def make_client():
    p = os.getenv("LLM_PROVIDER", "openai")
    if p == "openai":
        return OpenAICompat(None, os.environ["OPENAI_API_KEY"], "gpt-4o-mini")
    if p == "qwen":  # 通义：OpenAI 兼容协议，换 base_url 即可
        return OpenAICompat("https://dashscope.aliyuncs.com/compatible-mode/v1",
                            os.environ["DASHSCOPE_KEY"], "qwen-plus")
    if p == "zhipu":  # 智谱同样兼容
        return OpenAICompat("https://open.bigmodel.cn/api/paas/v4",
                            os.environ["ZHIPU_KEY"], "glm-4-flash")
```

**结果**：业务代码 0 行改动，靠 `LLM_PROVIDER=qwen` 一行环境变量切到国产模型，客户内网联调一次通过；后来客户要换智谱，又只改了 1 个环境变量。这层抽象成了该项目后续所有交付复用的底座。

**踩坑**：他一开始以为"国产模型都兼容 OpenAI 协议就完事"，结果发现 tool calling 的 `function` 字段在通义里叫法一致但智谱早期版本对 tool_choice 处理不同，导致工具调用偶发不触发。他在适配层加了字段归一化兜底才稳定。教训：**兼容协议≠行为完全一致**，适配层要兜差异。

**可复用经验**：任何给客户的 LLM 项目，第一天就做 `LLMClient` 抽象层，业务代码只认接口。这是 FDE 区别于纯算法岗的工程素养——**为"换底座"留好接口，私有化交付才不返工**。

## 面试高频问答
问:多厂商 API 你怎么选型?
答:看能力/成本/延迟/上下文长度/私有化需求。线上推理用 GPT-4o,降本用小模型,私有化用本地 Ollama 或智谱。

## 简历话术
- ❌ 弱表述:了解API 调用与 Prompt 工程
- ✅ 强表述:封装多厂商 LLM API 统一接口,实现模型选型对比与 Prompt 模板库,支持 OpenAI/智谱/Ollama 切换


## 进阶挑战

1. 接入真实智谱 GLM API（base_url=open.bigmodel.cn），跑通一次真实调用
2. 实现并发批量调用 + 速率限制（令牌桶），对比单次 vs 批量的吞吐
3. 做一个成本计算器：输入预期 QPS 和平均 token，输出月度成本估算
4. 为客服场景设计一个完整 Prompt 模板（角色+约束+输出格式），并写评测脚本
5. 实现 Prompt A/B 测试框架：随机分流，统计两类 Prompt 的准确率
6. 把 Prompt 模板存成 YAML 文件，实现热加载与版本对比

---

## 明日预告

**Day 4：Context Engineering：上下文管理**
> 🔵 FDE 工程基础与 LLM 原理 · 第 1 周
