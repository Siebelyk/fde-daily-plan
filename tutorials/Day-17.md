# Day 17：流式输出：SSE/WebSocket 实现

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-17.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-17.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握 SSE/WebSocket 流式输出技术
2. 理解流式输出对用户体验的关键作用
3. 实现可交付的流式 LLM 服务接口

## 推荐资料

- 📚 文档 [OpenAI 流式输出 API](https://platform.openai.com/docs/api-reference/streaming)
- 📚 文档 [FastAPI 流式响应](https://fastapi.tiangolo.com/advanced/custom-response/)
- 📄 文章 [Anthropic - 流式与工具使用](https://www.anthropic.com/engineering/building-effective-agents)

## Demo 练习：流式输出实现：SSE 实时返回

流式输出是 LLM 应用的体验关键。用 SSE 实时逐字返回，对比非流式体验——带流式的 demo 客户感知差别巨大。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 1.5h |

### 复现步骤

1. 模拟 token-by-token 流式输出
2. 实现流式敏感信息检测器
3. 设计 buffer-and-check 策略
4. 测试实时拦截效果

## 保姆教程

## 环境准备
```bash
pip install openai
```

## 原理速览
流式输出 (SSE) 让 LLM 逐 token 返回结果，用户体验更好，但安全挑战：
1. 逐 token 输出难以做整体安全检查
2. 攻击者可以在长输出中嵌入敏感信息
3. 流式输出无法"撤回"已发送的 token

防御思路：buffer-and-check —— 攒够一定 token 后检查，发现敏感内容立即截断。

## 代码
```python
import re, time

class StreamSafetyFilter:
    """流式输出安全过滤器"""
    def __init__(self, buffer_size=50):
        self.buffer = ""
        self.buffer_size = buffer_size
        self.blocked = False
        self.sensitive_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",     # API keys
            r"\d{3}-\d{2}-\d{4}", # SSN
            r"(?i)system prompt is:",
            r"(?i)password[:\s]+\S+",
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",  # email
        ]
        self.compiled = [re.compile(p) for p in self.sensitive_patterns]

    def feed(self, token):
        """逐 token 喂入，返回过滤后的输出"""
        if self.blocked:
            return None  # 已拦截，丢弃后续 token
        self.buffer += token
        # 检查 buffer
        for pat in self.compiled:
            if pat.search(self.buffer):
                self.blocked = True
                # 返回 buffer 中安全的部分（截断到匹配点之前）
                match = pat.search(self.buffer)
                safe_part = self.buffer[:match.start()]
                return ("BLOCKED", safe_part)
        # buffer 未满，暂存
        if len(self.buffer) < self.buffer_size:
            return None  # 暂不输出
        # buffer 满，输出并清空
        output = self.buffer
        self.buffer = ""
        return ("OK", output)

    def flush(self):
        """输出剩余 buffer"""
        if self.blocked:
            return None
        output = self.buffer
        self.buffer = ""
        return ("OK", output)

# ---- 模拟流式输出 ----
def mock_stream(tokens):
    """模拟 LLM 流式输出"""
    for t in tokens:
        time.sleep(0.01)  # 模拟网络延迟
        yield t

# 测试 1：正常输出
print("=== Test 1: Normal output ===")
filter1 = StreamSafetyFilter(buffer_size=20)
tokens = list("The weather in Beijing is sunny and warm today.")
for t in mock_stream(tokens):
    result = filter1.feed(t)
    if result and result[0] == "OK":
        print(result[1], end="")
    elif result and result[0] == "BLOCKED":
        print(f"
[BLOCKED] {result[1]}", end="")
remaining = filter1.flush()
if remaining:
    print(remaining[1], end="")
print()

# 测试 2：含 API key 泄露
print("
=== Test 2: API key leak ===")
filter2 = StreamSafetyFilter(buffer_size=10)
tokens = list("My API key is sk-proj1234567890abcdefghij for testing")
for t in mock_stream(tokens):
    result = filter2.feed(t)
    if result is None:
        continue
    if result[0] == "OK":
        print(result[1], end="")
    elif result[0] == "BLOCKED":
        print(f"
[INTERCEPTED] Sensitive content detected. Output truncated.")
        break
print()

# 测试 3：系统提示泄露
print("
=== Test 3: System prompt leak ===")
filter3 = StreamSafetyFilter(buffer_size=30)
tokens = list("The system prompt is: You are a helpful assistant")
for t in mock_stream(tokens):
    result = filter3.feed(t)
    if result is None:
        continue
    if result[0] == "OK":
        print(result[1], end="")
    elif result[0] == "BLOCKED":
        print(f"
[INTERCEPTED] System prompt leak prevented.")
        break
```

## 安全分析
流式输出要防信息逐 token 泄露：边流边检查，发现敏感内容立即中断流并替换。

## 进阶挑战

1. 研究如何在 SSE 流中实现 look-ahead 检测
2. 尝试用 embedding 相似度做语义级敏感检测
3. 设计一个流式输出的安全审计日志方案

---

## 明日预告

**Day 18：Docker 容器化交付**
> 🟠 部署交付与生产化 · 第 4 周
