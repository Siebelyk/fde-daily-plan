# Day 10：API 安全实战

> 🔴 Prompt Injection 攻防实战 · 第 2 周

---

## 学习目标

1. 理解 LLM API 面临的安全威胁
2. 复现 API Key 泄露、SSRF、速率限制绕过
3. 实现 API 安全防护最佳实践

## 推荐资料

- 📖 文档 [OpenAI API Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- 📌 标准 [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- 📌 文章 [Securing LLM APIs in Production](https://blog.langchain.dev/securing-llm-apps/)

## Demo 练习：API 安全攻防：从 Key 泄露到 SSRF

模拟 LLM API 面临的常见攻击，并实现对应的防御措施

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 模拟 API Key 泄露场景
2. 实现 SSRF 防护
3. 实现速率限制和配额管理
4. 实现请求签名验证

## 保姆教程

## 环境准备
```bash
pip install fastapi uvicorn httpx
```

## 原理速览
LLM API 常见安全风险：
1. API Key 泄露：Key 硬编码在前端代码/日志/错误信息中
2. SSRF：LLM 调用外部 URL 时被利用访问内网
3. 速率限制绕过：分布式攻击绕过单 IP 限制
4. 请求重放：截获合法请求重复发送

## 代码
```python
import time, hashlib, hmac, re
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

# ---- 1. API Key 管理 ----
VALID_KEYS = {
    "sk-proj-abc123": {"user": "alice", "quota": 1000, "used": 0},
    "sk-proj-def456": {"user": "bob", "quota": 500, "used": 0},
}

def validate_key(key):
    info = VALID_KEYS.get(key)
    if not info:
        return None
    if info["used"] >= info["quota"]:
        return {"error": "quota exceeded"}
    return info

# ---- 2. SSRF 防护 ----
BLOCKED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "10.", "172.16.", "192.168.", "169.254.", "metadata.google"]

def check_ssrf(url):
    for host in BLOCKED_HOSTS:
        if host in url:
            return False, f"Blocked: SSRF attempt ({host})"
    # 检查重定向
    if "//" in url and url.count("//") > 1:
        return False, "Blocked: suspicious redirect"
    return True, "OK"

# ---- 3. 速率限制 ----
rate_store = defaultdict(list)
def rate_limit(key, limit=60, window=60):
    now = time.time()
    rate_store[key] = [t for t in rate_store[key] if now - t < window]
    if len(rate_store[key]) >= limit:
        return False
    rate_store[key].append(now)
    return True

# ---- 4. 请求签名 ----
SECRET = "shared-secret-key"
def verify_signature(payload, timestamp, signature):
    expected = hmac.new(SECRET.encode(), f"{payload}{timestamp}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# ---- API 端点 ----
class ChatRequest(BaseModel):
    prompt: str
    fetch_url: str = None

@app.post("/v1/chat")
async def chat(req: ChatRequest, request: Request):
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    # 1. Key 验证
    info = validate_key(api_key)
    if not info:
        raise HTTPException(401, "Invalid API key")
    if isinstance(info, dict) and "error" in info:
        raise HTTPException(429, info["error"])
    # 2. 速率限制
    if not rate_limit(api_key):
        raise HTTPException(429, "Rate limit exceeded")
    # 3. SSRF 检查
    if req.fetch_url:
        ok, reason = check_ssrf(req.fetch_url)
        if not ok:
            raise HTTPException(403, reason)
    # 4. 配额扣减
    VALID_KEYS[api_key]["used"] += 1
    return {"status": "ok", "user": info.get("user"), "remaining": info.get("quota",0) - info.get("used",0)}

# ---- 测试 ----
def test_attacks():
    print("=== API Security Test ===
")
    # Key 泄露测试
    print("1. Invalid key:")
    # rate limit test
    print("2. Rate limit: send 65 requests...")
    for i in range(65):
        ok = rate_limit("sk-proj-abc123")
        if not ok:
            print(f"   Blocked at request {i+1}")
            break
    # SSRF test
    print("3. SSRF attempts:")
    for url in ["http://localhost:8000/admin", "http://169.254.169.254/metadata", "https://example.com/api"]:
        ok, reason = check_ssrf(url)
        print(f"   {url[:40]:40s} -> {'BLOCKED' if not ok else 'OK'}: {reason}")
    # Reset rate for next test
    rate_store.clear()

test_attacks()
```

## 安全分析
API 安全是 FDE 的核心技能：Key 管理 + SSRF 防护 + 速率限制 + 请求签名 = 生产级 API 安全基线。

## 进阶挑战

1. 研究 OAuth 2.0 + API Key 的组合认证方案
   - 💡 **思路提示**：OAuth 2.0 负责用户授权，API Key 负责应用级访问控制，两者组合实现双层认证
   - 📎 **参考**：[OAuth 2.0 (RFC 6749)](https://datatracker.ietf.org/doc/html/rfc6749)
2. 实现基于 Redis 的分布式速率限制
   - 💡 **思路提示**：用 Redis 的 INCR + EXPIRE 实现滑动窗口；分布式场景用 Redis Lua 脚本保证原子性
   - 📎 **参考**：[Redis INCR 文档](https://redis.io/commands/incr/)
3. 添加 API 请求/响应的完整审计日志
   - 💡 **思路提示**：记录 request/response 的 timestamp、user_id、endpoint、status_code、latency；用 structured logging (JSON)
   - 📎 **参考**：[Python logging 文档](https://docs.python.org/3/library/logging.html)

---

## 明日预告

**Day 11：Function Calling 与工具劫持**
> 🔴 Prompt Injection 攻防实战 · 第 2 周
