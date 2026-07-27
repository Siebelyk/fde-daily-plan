# Day 10: API 安全实战

> Prompt Engineering | 第 2 周

## Demo: API Key 泄露检测与防护实战

写安全的 API 客户端（key 管理、错误处理、日志脱敏），写 key 泄露扫描工具

- 难度：进阶
- 预计时间：2h

## 复现步骤

- 1. 写不安全客户端（硬编码 key）
- 2. 写正则扫描工具
- 3. 重写安全版本
- 4. 测试调用
- 5. 写 checklist

## 保姆教程

## 代码
~~~python
import os, re, time
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# 扫描工具
def scan_keys(code):
    patterns = [r'sk-[a-zA-Z0-9]{20,}',
                r'(?i)(api_?key|secret)\s*=\s*["'].*["']']
    for p in patterns:
        m = re.findall(p, code)
        if m: print(f"发现: {m[:2]}")

# 安全客户端
class SafeClient:
    def __init__(self):
        self.key = os.getenv("OPENAI_API_KEY")
        if not self.key: raise ValueError("No key in env")
        self.client = OpenAI(api_key=self.key)
    def chat(self, msgs, retries=3):
        for i in range(retries):
            try:
                return self.client.chat.completions.create(
                    model="gpt-4o-mini", messages=msgs, timeout=30
                ).choices[0].message.content
            except Exception:
                if i < retries-1: time.sleep(2**i)
                else: raise
~~~

## 安全分析
API key 泄露是最常见事故。安全客户端：不硬编码、日志脱敏、超时重试
