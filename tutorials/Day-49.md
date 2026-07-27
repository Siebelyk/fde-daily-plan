# Day 49: 本周回顾 + 安全部署项目

> 部署与运维安全 | 第 7 周

## Demo: 安全 LLM 服务部署项目：完整 DevSecOps 流程

构建含安全配置、监控告警、日志审计的完整 LLM 服务部署方案

- 难度：项目
- 预计时间：3h

## 复现步骤

- 1. 编写安全 Dockerfile+compose
- 2. 配置 Nginx 反代+认证
- 3. 实施监控+告警
- 4. 配置日志审计
- 5. 编写部署文档+安全checklist

## 保姆教程

## 项目结构
~~~text
secure-llm-deploy/
├── Dockerfile              # 安全容器构建
├── docker-compose.yml      # 安全编排
├── nginx/
│   ├── nginx.conf          # 反代+认证
│   └── ssl/                # TLS 证书
├── monitoring/
│   ├── prometheus.yml      # 监控配置
│   └── alerts.yml         # 告警规则
├── scripts/
│   ├── security-check.sh  # 安全检查
│   └── deploy.sh          # 安全部署脚本
└── README.md
~~~

## 安全检查脚本
~~~bash
#!/bin/bash
# security-check.sh

echo "=== LLM 服务安全检查 ==="

# 1. 容器安全
echo "[1] 容器安全"
docker inspect llm-service --format='User: {{.Config.User}}'
docker inspect llm-service --format='ReadOnly: {{.HostConfig.ReadonlyRootfs}}'
docker inspect llm-service --format='Privileged: {{.HostConfig.Privileged}}'

# 2. 网络安全
echo "[2] 网络安全"
curl -sk https://localhost/v1/models -w "Status: %{http_code}
" -o /dev/null
curl -s http://localhost:8000/v1/models -w "Direct(should fail): %{http_code}
" -o /dev/null

# 3. API认证
echo "[3] API认证"
curl -sk https://localhost/v1/models -w "NoAuth(should 401): %{http_code}
" -o /dev/null
curl -sk -H "Authorization: Bearer $API_KEY" https://localhost/v1/models -w "Auth: %{http_code}
" -o /dev/null

# 4. 速率限制
echo "[4] 速率限制"
for i in $(seq 1 20); do
  curl -sk -H "Authorization: Bearer $API_KEY" https://localhost/v1/models -w "%{http_code} " -o /dev/null
done
echo ""

# 5. 日志审计
echo "[5] 日志审计"
docker logs llm-service --tail 5 2>&1 | grep -v "query\|response"

echo "=== 检查完成 ==="
~~~

## 监控告警示例
~~~yaml
# alerts.yml
groups:
  - name: llm-security
    rules:
      - alert: HighRequestRate
        expr: rate(llm_requests_total[1m]) > 100
        for: 1m
        labels: { severity: warning }
        annotations: { summary: "请求频率异常" }

      - alert: InjectionDetected
        expr: increase(llm_injection_blocked_total[5m]) > 10
        for: 0m
        labels: { severity: critical }
        annotations: { summary: "大量注入攻击被拦截" }

      - alert: ErrorRateHigh
        expr: rate(llm_errors_total[5m]) / rate(llm_requests_total[5m]) > 0.1
        for: 2m
        labels: { severity: warning }
        annotations: { summary: "错误率超过10%" }
~~~

## 安全分析
安全部署 = 容器加固+反代认证+监控告警+日志审计+定期安全检查
