# Day 48: Docker 化 LLM 服务安全

> 部署与运维安全 | 第 7 周

## Demo: Docker 安全实验：LLM 服务的容器化加固

检查 LLM Docker 部署的安全配置，实施容器加固方案

- 难度：进阶
- 预计时间：2.5h

## 复现步骤

- 1. 检查默认 Dockerfile 安全
- 2. 实施最小权限运行
- 3. 配置资源限制
- 4. 镜像漏洞扫描
- 5. 编写安全 docker-compose

## 保姆教程

## 安全 Dockerfile
~~~dockerfile
FROM python:3.11-slim AS base

# 不以 root 运行
RUN groupadd -r llm && useradd -r -g llm llm
USER llm

# 安装依赖
COPY --chown=llm:llm requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY --chown=llm:llm . /app
WORKDIR /app

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 非特权启动
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", "--host", "0.0.0.0", "--port", "8000"]
~~~

## 安全 docker-compose.yml
~~~yaml
version: "3.8"
services:
  llm:
    build: .
    ports:
      - "127.0.0.1:8000:8000"  # 仅本地映射
    user: "1000:1000"          # 非 root
    read_only: true            # 只读文件系统
    cap_drop:                  # 删除所有 capabilities
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges:true  # 禁止提权
    tmpfs:
      - /tmp:size=100M          # 临时文件挂载
    mem_limit: 8g              # 内存限制
    cpus: 4                    # CPU 限制
    ulimits:
      nofile: 1024             # 文件描述符限制
    networks:
      - internal               # 内部网络隔离
    environment:
      - API_KEY=${API_KEY}
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    depends_on:
      - llm
    networks:
      - internal
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro

networks:
  internal:
    driver: bridge
    internal: true  # 无外网访问
~~~

## 安全检查脚本
~~~python
import subprocess, re

checks = [
    ("非root运行", "docker inspect --format '{{.Config.User}}' llm-service"),
    ("只读文件系统", "docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' llm-service"),
    ("无特权模式", "docker inspect --format '{{.HostConfig.Privileged}}' llm-service"),
    ("capabilities已删", "docker inspect --format '{{.HostConfig.CapDrop}}' llm-service"),
    ("资源限制", "docker inspect --format '{{.HostConfig.Memory}}' llm-service"),
    ("网络隔离", "docker inspect --format '{{.NetworkSettings.Networks}}' llm-service"),
]

for name, cmd in checks:
    print(f"[{name}] {cmd}")
print("
运行以上命令检查容器安全配置")
~~~

## 安全分析
Docker 加固 = 非root+只读+cap_drop+资源限制+网络隔离，这是容器安全基线
