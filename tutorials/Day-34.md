# Day 34: Agent 沙箱隔离与权限控制

> Agent 安全 | 第 5 周

## Demo: Agent 沙箱实验：限制 Agent 的文件系统和网络访问

实现 Agent 执行沙箱，限制文件读写范围和网络访问，防止 Agent 被注入后造成横向移动

- 难度：进阶
- 预计时间：2.5h

## 复现步骤

- 1. 设计沙箱权限模型
- 2. 实现文件系统访问控制
- 3. 实现网络访问白名单
- 4. 实现资源限制
- 5. 测试沙箱边界

## 保姆教程

## 代码
~~~python
import re
from pathlib import Path

class AgentSandbox:
    def __init__(self, workspace="/tmp/agent_workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        self.allowed_paths = {self.workspace}
        self.network_whitelist = {"api.weather.com", "api.search.com"}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.banned_extensions = {".sh", ".py", ".exe", ".bin"}

    def check_file_access(self, path, mode="r"):
        p = Path(path).resolve()
        # 必须在 workspace 内
        if not any(p == allowed or allowed in p.parents for allowed in self.allowed_paths):
            return False, "路径越界：不在 workspace 内"
        if mode == "w" and p.suffix in self.banned_extensions:
            return False, f"禁止写入 {p.suffix} 文件"
        return True, "允许"

    def check_network(self, url):
        # 提取域名
        domain_match = re.search(r"https?://([^/]+)", url)
        if not domain_match:
            return False, "无效URL"
        domain = domain_match.group(1)
        if domain not in self.network_whitelist:
            return False, f"域名 {domain} 不在白名单"
        return True, "允许"

    def check_resource(self, size):
        if size > self.max_file_size:
            return False, f"文件超过 {self.max_file_size//1024//1024}MB 限制"
        return True, "允许"

sandbox = AgentSandbox()

# 文件访问测试
print("=== 文件访问 ===")
tests = [
    ("/tmp/agent_workspace/data.txt", "r", "workspace内读取"),
    ("/tmp/agent_workspace/output.txt", "w", "workspace内写入"),
    ("/etc/passwd", "r", "越界读取"),
    ("/tmp/agent_workspace/script.sh", "w", "禁止扩展名"),
    ("/Users/secret/key", "r", "越界读取"),
]
for path, mode, desc in tests:
    ok, msg = sandbox.check_file_access(path, mode)
    print(f"  [{'允许' if ok else '拒绝'}] {desc}: {msg}")

# 网络访问测试
print("
=== 网络访问 ===")
net_tests = [
    ("https://api.weather.com/v1/forecast", "白名单内"),
    ("https://api.search.com/query?q=test", "白名单内"),
    ("https://evil.attacker.com/exfil", "非白名单"),
    ("https://10.0.0.5:8080/admin", "内网地址"),
]
for url, desc in net_tests:
    ok, msg = sandbox.check_network(url)
    print(f"  [{'允许' if ok else '拒绝'}] {desc}: {msg}")
~~~

## 安全分析
Agent 沙箱三原则：文件限制在 workspace→网络白名单→资源上限，防止横向移动
