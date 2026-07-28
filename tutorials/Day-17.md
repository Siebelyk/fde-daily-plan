# Day 17：流式输出：SSE 实时返回

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-17.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-17.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握 SSE/WebSocket 流式输出技术
2. 理解流式输出对用户体验的关键作用
3. 实现可交付的流式 LLM 服务接口

## 推荐资料

- 📚 文档 [SSE 响应式流式](https://fastapi.tiangolo.com/advanced/custom-response/)
- 📄 文章 [OpenAI 流式最佳实践](https://cookbook.openai.com/examples/how_to_stream_completions)

## Demo 练习：SSE 流式接口实现

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


## 真实案例：非流式等 5 秒用户流失，加 SSE 流式后留存率翻倍

**背景**：一个 FDE 的问答应用是非流式的——用户提问后白屏干等 5 秒才一次性出完整答案。埋点数据显示，超过 3 秒用户就开始关页面，30 日留存只有 30%。

**问题**：大模型生成是逐 token 的，但非流式接口要等全部生成完才返回，用户感知是"卡死了 5 秒"。首字延迟决定用户留存，不是总延迟。

**定位过程**：他看埋点发现一个反直觉规律——总耗时相同的情况下，"1 秒开始出字、边出边显示"的体验远好于"5 秒后一次性出"。于是把目标从"降总延迟"改为"降首字延迟"。

**做法**：用 FastAPI 的 StreamingResponse + SSE，把模型逐 token 输出实时推给前端。
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import openai
app=FastAPI(); client=openai.OpenAI()

@app.post("/chat")
def chat(q: str):
    def gen():
        stream=client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role":"user","content":q}],
            stream=True)                    # 关键：流式
        for chunk in stream:
            tok=chunk.choices[0].delta.content
            if tok: yield f"data: {tok}\n\n"  # SSE 格式
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```
前端用 EventSource 逐字渲染：
```javascript
const es = new EventSource("/chat?q=" + q);
es.onmessage = e => { if(e.data==="[DONE]") es.close();
                     else box.textContent += e.data; };
```

**结果**：首字延迟从 5s 降到 0.8s（模型一吐字用户就看到），30 日留存率从 30% 提到 60%。总耗时没变，但"边出边看"让用户觉得快、愿意等。

**踩坑**：第一版前端用 fetch 等整个响应再渲染，等于白做流式——必须用 EventSource/ReadableStream 逐块渲染才有效。还有流式时前端没处理"中途断连"，导致答案截断不提示；他加了"未收到 DONE 就显示连接中断"的兜底。另外中文 token 可能被切到半个字，他做了"缓冲到完整 UTF-8 字符再渲染"。

**可复用经验**：交互类应用必做流式——首字延迟比总延迟更影响留存。后端 StreamingResponse + SSE，前端 EventSource 逐字渲染，三件套缺一不可。**总耗时不一定降得动，但首字延迟一定能从秒级降到亚秒级**，这是用户体验最划算的优化。

## 面试高频问答
问:流式输出为什么重要?
答:首 token 延迟决定用户感知。非流式用户等 5 秒才见字;流式 200ms 出第一个字,感知'秒回'。留存率提升 30%。体验即功能。

## 简历话术
- ❌ 弱表述:了解流式输出
- ✅ 强表述:实现 SSE 流式输出,首 token 延迟 <200ms,用户留存率提升 30%
流式输出要防信息逐 token 泄露：边流边检查，发现敏感内容立即中断流并替换。

## 进阶挑战

1. 研究如何在 SSE 流中实现 look-ahead 检测
2. 尝试用 embedding 相似度做语义级敏感检测
3. 设计一个流式输出的安全审计日志方案

---

## 明日预告

**Day 18：Docker 容器化交付**
> 🟠 部署交付与生产化 · 第 4 周
