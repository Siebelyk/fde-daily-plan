# Day 12：流式输出与信息泄露

> 🔴 Prompt Injection 攻防实战 · 第 2 周

---

## 学习目标

1. 理解 SSE/流式输出的工作原理
2. 复现流式输出中的信息泄露攻击
3. 实现流式输出的安全防护

## 推荐资料

- 📖 文档 [OpenAI - Streaming API Reference](https://platform.openai.com/docs/api-reference/streaming)
- 📌 文章 [LLM Output Leakage Attacks](https://arxiv.org/abs/2308.05421)
- 📌 标准 [OWASP LLM02 - Insecure Output Handling](https://owasp.org/www-project-top-10-for-llms/)

## Demo 练习：流式输出信息泄露实验

模拟流式 API 输出中的 token-by-token 泄露，实现实时敏感信息检测和流式过滤

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 1.5h |

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
流式输出安全 = buffer-and-check + 敏感模式匹配 + 实时截断。关键是平衡延迟和安全：buffer 太小检测不全，太大延迟高。

## 进阶挑战

1. 研究如何在 SSE 流中实现 look-ahead 检测
   - 💡 **思路提示**：在 SSE 流中维护一个 buffer，每次收到新 token 时检查 buffer 尾部是否匹配敏感模式
   - 📎 **参考**：[SSE (Server-Sent Events) MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
2. 尝试用 embedding 相似度做语义级敏感检测
   - 💡 **思路提示**：用 sentence-transformers 编码输出片段，与敏感模式库做 cosine similarity 阈值检测
   - 📎 **参考**：[Sentence-Transformers 文档](https://www.sbert.net/)
3. 设计一个流式输出的安全审计日志方案
   - 💡 **思路提示**：记录每个 SSE event 的 timestamp、content、token_count、filtered_flag；用异步队列写入
   - 📎 **参考**：[Python asyncio.Queue 文档](https://docs.python.org/3/library/asyncio-queue.html)

---

## 明日预告

**Day 13：防御工程：输入过滤、输出检查与 Guardrails**
> 🔴 Prompt Injection 攻防实战 · 第 2 周
