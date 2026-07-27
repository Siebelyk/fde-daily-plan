# Day 13: 本地模型安全部署

> Prompt Engineering | 第 2 周

## Demo: Ollama 安全加固：从默认配置到安全部署

检查 Ollama 默认配置安全风险，写安全配置脚本加固

- 难度：进阶
- 预计时间：1.5h

## 复现步骤

- 1. 安装启动 Ollama
- 2. 检查默认监听和端口
- 3. 识别 3 个安全风险
- 4. 写安全配置
- 5. 验证

## 保姆教程

## 代码
~~~python
import subprocess, requests

result = subprocess.run(["lsof","-i",":11434"], capture_output=True, text=True)
print(f"监听: {result.stdout}")
print("无认证可访问:", requests.get("http://localhost:11434/api/tags").status_code == 200)
print("""
风险: 1.默认监听0.0.0.0 2.无认证 3.无限流
加固: export OLLAMA_HOST=127.0.0.1:11434
加nginx认证代理: if ($http_authorization != "Bearer key") {return 401;}
""")
~~~

## 安全分析
本地部署不等于安全，Ollama 默认无认证+对外监听是高危的
