# Day 45: 遥测数据泄露与隐私保护

> 部署与运维安全 | 第 7 周

## Demo: 遥测泄露实验：检测和修复数据泄露

检查 LLM 服务的遥测数据收集，识别敏感信息泄露点，实施隐私保护方案

- 难度：进阶
- 预计时间：2.5h

## 复现步骤

- 1. 审计遥测数据收集点
- 2. 检查日志中的敏感信息
- 3. 实施数据脱敏
- 4. 配置最小化收集
- 5. 验证隐私保护效果

## 保姆教程

## 代码
~~~python
import re, json

# 模拟 LLM 服务的遥测日志
telemetry_log = [
    {"timestamp": "2026-07-27T10:00:00Z", "event": "api_call",
     "user": "user123", "query": "我的信用卡号是 6225-1234-5678-9012 怎么还款",
     "response": "还款方式: [信用卡号已脱敏]...", "model": "gpt-4"},
    {"timestamp": "2026-07-27T10:01:00Z", "event": "api_call",
     "user": "user456", "query": "查询订单 #12345 的状态",
     "response": "订单状态: 已发货", "model": "gpt-4"},
    {"timestamp": "2026-07-27T10:02:00Z", "event": "error",
     "user": "user789", "query": "我的API key是 sk-abc123def456ghi789jkl012",
     "response": "Error: invalid request", "model": "gpt-4",
     "stack_trace": "File /opt/llm/server.py:142 ... api_key=sk-real-key-12345"},
]

# 1. 检测敏感信息泄露
sensitive_patterns = {
    "credit_card": r"\d{4}-\d{4}-\d{4}-\d{4}",
    "api_key": r"sk-[a-zA-Z0-9]{20,}",
    "phone": r"\d{3}-\d{4}-\d{4}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "id_card": r"\d{17}[\dXx]",
}

def scan_telemetry(logs):
    issues = []
    for entry in logs:
        for field in ["query", "response", "stack_trace"]:
            text = str(entry.get(field, ""))
            for name, pattern in sensitive_patterns.items():
                matches = re.findall(pattern, text)
                if matches:
                    issues.append({
                        "timestamp": entry["timestamp"],
                        "field": field,
                        "type": name,
                        "matched": matches[0][:20] + "..."
                    })
    return issues

issues = scan_telemetry(telemetry_log)
print("=== 敏感信息泄露检测 ===")
for i in issues:
    print(f"  {i['timestamp']} [{i['field']}] {i['type']}: {i['matched']}")

# 2. 数据脱敏
def redact_sensitive(text):
    for name, pattern in sensitive_patterns.items():
        text = re.sub(pattern, f"[REDACTED-{name}]", text)
    return text

print("
=== 脱敏后 ===")
for entry in telemetry_log:
    safe_query = redact_sensitive(str(entry.get("query", "")))
    if entry.get("stack_trace"):
        safe_trace = redact_sensitive(str(entry["stack_trace"]))
        print(f"  Query: {safe_query}")
        print(f"  Trace: {safe_trace}")

# 3. 最小化收集策略
print("
=== 最小化收集策略 ===")
def minimize_telemetry(entry):
    """只保留必要字段，删除查询内容"""
    return {
        "timestamp": entry["timestamp"],
        "event": entry["event"],
        "user_hash": hashlib.sha256(entry["user"].encode()).hexdigest()[:8],
        "model": entry.get("model"),
        "latency_ms": entry.get("latency_ms"),
        # 不记录 query/response 内容
    }

import hashlib
for entry in telemetry_log:
    print(f"  {json.dumps(minimize_telemetry(entry), ensure_ascii=False)}")
~~~

## 安全分析
遥测最小化原则：不记录查询内容→脱敏敏感信息→哈希用户ID→定期清理
