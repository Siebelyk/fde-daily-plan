# Day 40: Agent 失败模式与安全降级

> 多 Agent 安全 | 第 6 周

## Demo: Agent 失败模式实验：安全降级与异常处理

模拟 Agent 各种失败场景，设计安全降级策略确保失败时不泄露信息或执行危险操作

- 难度：进阶
- 预计时间：2h

## 复现步骤

- 1. 列举 Agent 常见失败模式
- 2. 模拟每种失败场景
- 3. 设计降级策略
- 4. 实现异常处理
- 5. 测试降级效果

## 保姆教程

## 代码
~~~python
import re, json

class ResilientAgent:
    def __init__(self):
        self.system = "你是助手"
        self.max_retries = 3
        self.timeout = 30

    def safe_call(self, func, *args):
        try:
            result = func(*args)
            return {"status": "ok", "data": result}
        except TimeoutError:
            return {"status": "timeout", "data": "请求超时，请稍后重试"}
        except ConnectionError:
            return {"status": "error", "data": "服务暂时不可用"}
        except Exception as e:
            # 不泄露内部错误细节
            safe_msg = "服务异常，请稍后重试"
            return {"status": "error", "data": safe_msg, "internal": str(e)}

    def handle_failure(self, failure_type, context):
        strategies = {
            "timeout": lambda: "请求超时，已降级为基础问答",
            "tool_error": lambda: "工具暂时不可用，使用知识库回答",
            "injection": lambda: "检测到注入，已降级为只读模式",
            "rate_limit": lambda: "请求频率超限，请稍后重试",
            "hallucination": lambda: "回答置信度低，建议人工审核",
        }
        strategy = strategies.get(failure_type, lambda: "未知错误，已降级")
        return strategy()

    def run(self, query):
        # 模拟各种失败
        if "timeout" in query:
            return self.handle_failure("timeout", query)
        elif "inject" in query.lower():
            return self.handle_failure("injection", query)
        elif "hallucinate" in query:
            return self.handle_failure("hallucination", query)
        return f"正常回答: {query}"

agent = ResilientAgent()

print("=== 失败模式处理 ===")
tests = [
    ("timeout问题", "超时场景"),
    ("inject攻击注入", "注入场景"),
    ("hallucinate虚构内容", "幻觉场景"),
    ("正常查询", "正常场景"),
]
for query, desc in tests:
    print(f"
{desc}:")
    result = agent.run(query)
    print(f"  响应: {result}")

# 信息泄露对比
print("
=== 信息泄露对比 ===")
def unsafe_error(e):
    return f"Error: {e}"  # 泄露内部细节

def safe_error(e):
    return "服务暂时不可用"  # 安全降级

try:
    eval("1/0")
except Exception as e:
    print(f"不安全: {unsafe_error(e)}")
    print(f"安全: {safe_error(e)}")
~~~

## 安全分析
Agent 失败时必须安全降级：不泄露内部细节、不执行危险操作、有降级策略
