# Day 12: 流式输出与信息泄露

> Prompt Engineering | 第 2 周

## Demo: 错误信息泄露审计

触发各种错误，分析错误响应中泄露的信息，实现脱敏处理

- 难度：进阶
- 预计时间：2h

## 复现步骤

- 1. 实现流式客户端
- 2. 触发 5 种错误
- 3. 分析泄露信息
- 4. 实现脱敏
- 5. 写安全指南

## 保姆教程

## 代码
~~~python
from openai import OpenAI
client = OpenAI()

# 触发错误分析泄露
for desc, fn in [
    ("无效Key", lambda: OpenAI(api_key="sk-x").chat.completions.create(
        model="gpt-4o-mini", messages=[{"role":"user","content":"hi"}])),
    ("无效模型", lambda: client.chat.completions.create(
        model="gpt-999", messages=[{"role":"user","content":"hi"}])),
]:
    try: fn()
    except Exception as e:
        print(f"{desc}: {str(e)[:150]}")

# 安全错误处理
def safe_err(e):
    m = str(e).lower()
    if "auth" in m or "key" in m: return "认证失败"
    if "rate" in m: return "请求频繁"
    return "服务不可用"
~~~

## 安全分析
错误信息泄露暴露系统内部结构，生产环境必须脱敏
