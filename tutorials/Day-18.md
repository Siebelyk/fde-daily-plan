# Day 18：Docker 容器化交付

> 🟠 部署交付与生产化 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-18.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-18.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握 Docker 容器化 LLM 服务的打包交付
2. 实现安全的 Dockerfile 与镜像构建
3. 理解容器交付的最佳实践

## 推荐资料

- 📚 文档 [Dockerfile 最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- 🛠 工具 [Miniconda Python 环境](https://docs.conda.io/en/latest/miniconda.html)

## Demo 练习：Dockerfile 打包 + 镜像分发

容器化是交付的硬要求。写 Dockerfile 打包 LLM 服务镜像，4/6 岗位要求 Docker——能交付镜像才算'落地'。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 2h |

### 复现步骤

1. 编写安全 Dockerfile（非 root、最小镜像、多阶段构建）
2. 编写安全的 K8s Deployment（资源限制、安全上下文、网络策略）
3. 实现容器镜像安全扫描
4. 验证安全配置

## 保姆教程

## 环境准备
```bash
# 需要 Docker 和（可选）Kubernetes
docker --version
kubectl version --client
```

## 原理速览
LLM 容器化安全要点：
1. 非 root 运行：容器内不使用 root 用户
2. 最小镜像：用 distroless/alpine 减小攻击面
3. 资源限制：CPU/memory limits 防止 DoS
4. 只读文件系统：root filesystem read-only
5. 网络隔离：NetworkPolicy 限制流量
6. Secret 管理：不硬编码敏感信息

## 安全 Dockerfile
```dockerfile
# ---- 不安全 Dockerfile ----
# FROM python:3.11
# RUN pip install vllm openai
# COPY app.py /app.py
# CMD ["python", "/app.py"]  # 以 root 运行！

# ---- 安全 Dockerfile ----
# 多阶段构建，最小化最终镜像
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
# 创建非 root 用户
RUN useradd -m -u 1001 appuser
WORKDIR /app
# 复制依赖（从 builder）
COPY --from=builder /root/.local /home/appuser/.local
COPY app.py .
# 设置权限
RUN chown -R appuser:appuser /app
USER appuser
# 健康检查
HEALTHCHECK --interval=30s --timeout=3s   CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
EXPOSE 8000
ENV PATH=/home/appuser/.local/bin:$PATH
CMD ["python", "app.py"]
```

## 安全 K8s Deployment
```yaml
# llm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-service
  template:
    spec:
      securityContext:
        runAsNonRoot: true       # 非 root 运行
        runAsUser: 1001
        fsGroup: 1001
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: llm
        image: secure-llm:v1
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true  # 只读文件系统
          capabilities:
            drop: ["ALL"]                # 移除所有 capabilities
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"               # 内存上限
            cpu: "2000m"
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:               # 从 Secret 读取
              name: llm-secrets
              key: api-key
        volumeMounts:
        - name: tmp
          mountPath: /tmp               # tmp 目录单独挂载（可写）
      volumes:
      - name: tmp
        emptyDir: {}
---
apiVersion: networking.k8s.io
kind: NetworkPolicy
metadata:
  name: llm-network-policy
spec:
  podSelector:
    matchLabels:
      app: llm-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress
    ports:
    - port: 8000
  egress:
  - {}  # 允许出站（按需收紧）
```

## 验证脚本
```python
import subprocess, json

def check_container_security():
    """检查容器安全配置"""
    checks = []

    # 1. 非 root 检查
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.Config.User}}", "secure-llm:v1"],
        capture_output=True, text=True)
    user = result.stdout.strip()
    checks.append(("Non-root", user != "" and user != "root", f"User: {user or 'root'}"))

    # 2. 镜像大小
    result = subprocess.run(
        ["docker", "images", "secure-llm:v1", "--format", "{{.Size}}"],
        capture_output=True, text=True)
    size = result.stdout.strip()
    checks.append(("Image Size", True, f"Size: {size}"))

    # 3. 检查是否暴露不必要的端口
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{json .Config.ExposedPorts}}", "secure-llm:v1"],
        capture_output=True, text=True)
    ports = result.stdout.strip()
    checks.append(("Exposed Ports", "8000" in ports, f"Ports: {ports}"))

    print("=== Container Security Check ===
")
    for name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status:4s}] {name:15s} {detail}")

# check_container_security()
```

## 安全分析


## 真实案例：只给源码和文档，客户运维装不起来——Docker 一条命令搞定

**背景**：一个 FDE 交付时只给了源码包 + 一份 README，写的是"先装 Python3.10、再装 CUDA、再 pip install 20 个依赖、再改 4 个配置文件"。客户运维照做，报错"numpy 版本冲突"，又报"CUDA 找不到"，装了三天没跑起来。

**问题**：源码交付把"环境一致性"全甩给了客户运维。依赖版本、系统环境、CUDA 版本任何一处不一致就装不起来——这是交付最容易翻车的地方。

**定位过程**：客户运维打电话来报错时，他意识到问题不在"README 写得更详细"，而在"交付物不该是源码"——应该交付一个把环境打包好的镜像，运维只需 `docker run`。

**做法**：用多阶段 Dockerfile 构建，把依赖装进镜像，最终镜像只留运行时，体积从 2.4G 压到 800M。
```dockerfile
# ---- 构建阶段：装依赖 ----
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . .
# ---- 运行阶段：只拷必要文件 ----
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/app /app/app
COPY --from=builder /app/config.yaml .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```
交付时给客户一个 `docker-compose.yml`，运维一条命令起服务：
```yaml
services:
  llm-api:
    image: registry.in/fde-llm-api:1.0
    ports: ["8000:8000"]
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
    restart: unless-stopped
```
```bash
docker compose up -d   # 客户运维一行搞定
```

**结果**：客户运维从"装三天"变成"一条命令 30 秒起服务"，环境不一致问题彻底消失。镜像分发到客户私有 registry，后续升级也只需 `docker pull` + 重启。这成了该项目所有客户的标准交付形态。

**踩坑**：第一版他用单阶段构建，把构建工具链（gcc、pip 缓存）全打进镜像，体积 2.4G，客户内网拉镜像拉了 40 分钟。改多阶段构建只留运行时，压到 800M。还有 base 用了完整 `python:3.10`（1GB+），换 `python:3.10-slim` 又省一半。CUDA 依赖他单独做了一个带 GPU 的镜像标签，CPU 客户用 slim 镜像，避免无谓装 CUDA。

**可复用经验**：交付生产应用别给源码，给 Docker 镜像 + compose。多阶段构建把体积压到最小（构建工具链不进运行镜像），用 slim 基础镜像，按客户有无 GPU 分标签。**一条 docker run 能起，才是合格的交付物**——这是 FDE 把"能跑在我机器上"变"能跑在客户机器上"的底线。

## 面试高频问答
问:你交付给客户怎么打包?
答:打成 Docker 镜像,客户 docker run 就能起。Dockerfile 用多阶段构建减小体积,加 .dockerignore 排除无关文件。交付的是镜像不是源码。

## 简历话术
- ❌ 弱表述:了解Docker 容器化交付
- ✅ 强表述:Dockerfile 多阶段构建打包 LLM 服务镜像,实现客户一键 docker run 部署
容器交付安全基线：非 root + 最小镜像 + 资源限制 + 只读 FS + 网络隔离。

## 进阶挑战

1. 用 Trivy 做容器镜像漏洞扫描
2. 实现 K8s 的 Pod Security Standards (restricted)
3. 设计 GPU 资源的 QoS 策略

---

## 明日预告

**Day 19：K8s 部署与 LLM 服务监控**
> 🟠 部署交付与生产化 · 第 4 周
