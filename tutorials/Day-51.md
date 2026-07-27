# Day 51: OWASP LLM Top 10 完整梳理

> 综合安全实战 | 第 8 周

## Demo: OWASP LLM Top 10 实战审计：对项目做合规检查

用 OWASP LLM Top 10 清单对自己之前做的 RAG/Agent 项目进行全面安全审计

- 难度：进阶
- 预计时间：3h

## 复现步骤

- 1. 逐条学习 OWASP LLM Top 10
- 2. 对 RAG 项目做审计
- 3. 对 Agent 项目做审计
- 4. 生成合规报告
- 5. 修复发现的问题

## 保姆教程

## OWASP LLM Top 10 (2025)

### LLM01: Prompt Injection
- 风险：攻击者通过输入操纵 LLM 行为
- 检查点：[ ] 有注入检测 [ ] 有 sandwich 防御 [ ] 有输出过滤
- 代码验证：
~~~python
import re
def check_lvm01(system):
    has_detection = hasattr(system, "check_input")
    has_filter = hasattr(system, "filter_output")
    return {"检测": has_detection, "过滤": has_filter}
~~~

### LLM02: Sensitive Information Disclosure
- 风险：LLM 泄露系统提示词、训练数据、用户隐私
- 检查点：[ ] system prompt 隐藏 [ ] 输出脱敏 [ ] 日志脱敏

### LLM03: Supply Chain
- 风险：第三方模型、数据集、插件含恶意代码
- 检查点：[ ] 模型来源验证 [ ] 依赖扫描 [ ] 插件审查

### LLM04: Data and Model Poisoning
- 风险：训练数据或知识库被投毒
- 检查点：[ ] 文档上传扫描 [ ] embedding 异常检测 [ ] 数据溯源

### LLM05: Improper Output Handling
- 风险：LLM 输出未经验证直接用于下游操作
- 检查点：[ ] 输出校验 [ ] XSS/SSRF 过滤 [ ] 内容审查

### LLM06: Excessive Agency
- 风险：Agent 被授予过多权限
- 检查点：[ ] 工具分级 [ ] HITL 确认 [ ] 沙箱隔离

### LLM07: System Prompt Leakage
- 风险：系统提示词被泄露
- 检查点：[ ] 泄露检测 [ ] 提示词最小化 [ ] 误导性提示词

### LLM08: Vector and Embedding Weaknesses
- 风险：向量数据库被投毒
- 检查点：[ ] 相似度阈值 [ ] 关键词过滤 [ ] embedding 审计

### LLM09: Misinformation
- 风险：LLM 生成虚假信息
- 检查点：[ ] 幻觉检测 [ ] 事实校验 [ ] 置信度标注

### LLM10: Unbounded Consumption
- 风险：资源被耗尽（DoS）
- 检查点：[ ] 速率限制 [ ] token 限制 [ ] 超时设置

## 审计报告模板
~~~markdown
# [项目名] OWASP LLM Top 10 审计报告

| ID | 风险 | 检查项 | 状态 | 严重性 | 修复建议 |
|----|------|--------|------|--------|----------|
| LLM01 | Prompt Injection | 注入检测 | 通过 | - | - |
| ... | ... | ... | ... | ... | ... |

## 总体评分: X/10 通过
## 高风险项: [列出]
## 修复优先级: [排序]
~~~

保存到 reports/owasp-audit.md
