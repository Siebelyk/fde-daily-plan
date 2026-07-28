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

- 📚 文档 [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- 📚 文档 [Kubernetes Security for LLM Workloads](https://kubernetes.io/docs/concepts/security/)
- 🎬 视频 [Docker Security for ML Services](https://www.youtube.com/watch?v=k7v8e2p3z1R)

## Demo 练习：容器化交付：从 Dockerfile 到镜像分发

编写安全的 Dockerfile 和 K8s manifest，部署 LLM 推理服务并验证安全配置

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

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
容器交付安全基线：非 root + 最小镜像 + 资源限制 + 只读 FS + 网络隔离。

## 进阶挑战

1. 用 Trivy 做容器镜像漏洞扫描
2. 实现 K8s 的 Pod Security Standards (restricted)
3. 设计 GPU 资源的 QoS 策略

---

## 明日预告

**Day 19：K8s 部署与 LLM 服务监控**
> 🟠 部署交付与生产化 · 第 4 周
