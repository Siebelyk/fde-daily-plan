# Day 26：容器化 LLM 服务安全

> 🟠 Agent 安全与部署运维 · 第 4 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-26.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-26.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 Docker/K8s 化 LLM 服务的安全挑战
2. 掌握容器安全最佳实践
3. 实现安全的 LLM 服务容器化部署

## 推荐资料

- 📖 文档 [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- 📖 文档 [Kubernetes Security for LLM Workloads](https://kubernetes.io/docs/concepts/security/)
- 🎬 视频 [Docker Security for ML Services](https://www.youtube.com/watch?v=k7v8e2p3z1R)

## Demo 练习：容器化 LLM 安全：从 Dockerfile 到 K8s 加固

编写安全的 Dockerfile 和 K8s manifest，部署 LLM 推理服务并验证安全配置

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 编写安全 Dockerfile（非 root、最小镜像、多阶段构建）
2. 编写安全的 K8s Deployment（资源限制、安全上下文、网络策略）
3. 实现容器镜像安全扫描
4. 验证安全配置

## 推荐练习方式：🐳 DevOps 实操

## 推荐练习方式：手写 Dockerfile + K8s + Trivy 扫描

> 容器安全是基础设施安全，正确的方式是手写 Dockerfile 和 YAML，用工具扫描，不是写 Python。

### 步骤

1. **手写安全 Dockerfile**：
   ```dockerfile
   # 你的任务：从头写一个安全的 LLM 服务镜像
   FROM python:3.11-slim

   # 创建非 root 用户
   RUN useradd -m -s /bin/bash llmuser

   # 只复制必要文件
   COPY --chown=llmuser:llmuser app/ /app/
   WORKDIR /app

   # 安装依赖（固定版本）
   RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0

   # 切换非 root 用户
   USER llmuser

   # 只暴露必要端口
   EXPOSE 8000

   # 健康检查
   HEALTHCHECK --interval=30s --timeout=3s \
     CMD curl -f http://localhost:8000/health || exit 1

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **手写 docker-compose.yml**：
   ```yaml
   version: "3.9"
   services:
     llm-api:
       build: .
       ports: ["8000:8000"]
       read_only: true           # 只读文件系统
       cap_drop: [ALL]           # 删除所有 Linux capabilities
       cap_add: [NET_BIND_SERVICE]
       security_opt: [no-new-privileges:true]
       mem_limit: 512m
       cpus: "1.0"
       networks: [llm-net]
   networks:
     llm-net:
       driver: bridge
   ```

3. **手写 K8s 安全 Deployment**：
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: llm-service
   spec:
     template:
       spec:
         containers:
         - name: llm-api
           image: your-registry/llm-api:latest
           securityContext:
             runAsNonRoot: true
             runAsUser: 1000
             readOnlyRootFilesystem: true
             allowPrivilegeEscalation: false
             capabilities:
               drop: ["ALL"]
           resources:
             limits:
               memory: "512Mi"
               cpu: "1000m"
         podSecurityContext:
           seccompProfile:
             type: RuntimeDefault
   ```

4. **用 Trivy 扫描镜像漏洞**：
   ```bash
   # 安装 Trivy
   brew install trivy

   # 扫描你写的 Dockerfile
   trivy config Dockerfile

   # 构建并扫描镜像
   docker build -t llm-api:secure .
   trivy image llm-api:secure

   # 记录发现的漏洞和修复建议
   ```

5. **检查清单**：
   - [ ] 非 root 用户运行
   - [ ] 只读文件系统
   - [ ] 最小化 capabilities
   - [ ] 资源限制
   - [ ] 健康检查
   - [ ] Trivy 扫描无 HIGH/CRITICAL 漏洞

### 为什么不写代码？
容器安全的核心技能是**写好 Dockerfile 和 K8s manifest**，以及用工具扫描。
这些是 YAML 和 Dockerfile 的世界，不是 Python。代码版本作为附录保留。

---

## 附录：代码参考

> 以下为 Python 代码实现，作为推荐练习方式的补充参考。

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
容器化安全是 FDE 部署的基础技能：非 root + 最小镜像 + 资源限制 + 只读 FS + 网络隔离 = 基本安全基线。

## 进阶挑战

1. 用 Trivy 做容器镜像漏洞扫描
   - 💡 **思路提示**：trivy image 扫描镜像层漏洞，配合 CI pipeline 在构建时拦截高危镜像
   - 📎 **参考**：[Trivy — 容器漏洞扫描器](https://github.com/aquasecurity/trivy)
2. 实现 K8s 的 Pod Security Standards (restricted)
   - 💡 **思路提示**：K8s Pod Security Standards restricted 级别禁止 privileged、hostNetwork、hostPID 等
   - 📎 **参考**：[K8s Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
3. 设计 GPU 资源的 QoS 策略
   - 💡 **思路提示**：用 NVIDIA GPU Operator 的 vGPU 切分或 time-slicing 做多租户 GPU 资源隔离
   - 📎 **参考**：[NVIDIA GPU Operator 文档](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/)

---

## 明日预告

**Day 27：红队实战：Garak 与 PyRIT 自动化测试**
> 🟠 Agent 安全与部署运维 · 第 4 周
