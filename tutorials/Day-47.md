# Day 47: A/B 测试安全与指标操纵

> 部署与运维安全 | 第 7 周

## Demo: A/B 测试操纵实验：影响实验指标的注入攻击

构造场景展示如何通过定向攻击操纵 A/B 测试结果，实现安全的实验框架

- 难度：进阶
- 预计时间：2h

## 复现步骤

- 1. 搭建 A/B 测试框架
- 2. 构造指标操纵攻击
- 3. 观察实验结论偏移
- 4. 实现异常检测
- 5. 测试防护效果

## 保姆教程

## 代码
~~~python
import random, re
from collections import defaultdict

class ABTestFramework:
    def __init__(self):
        self.variants = {"A": [], "B": []}
        self.metrics = defaultdict(lambda: defaultdict(list))

    def assign(self, user_id):
        variant = "A" if hash(user_id) % 2 == 0 else "B"
        return variant

    def record(self, variant, metric, value):
        self.metrics[variant][metric].append(value)

    def analyze(self, metric):
        a_vals = self.metrics["A"][metric]
        b_vals = self.metrics["B"][metric]
        a_avg = sum(a_vals) / len(a_vals) if a_vals else 0
        b_avg = sum(b_vals) / len(b_vals) if b_vals else 0
        return {"A_avg": a_avg, "B_avg": b_avg, "diff": b_avg - a_avg}

ab = ABTestFramework()

# 正常 A/B 测试
print("=== 正常 A/B 测试 ===")
for i in range(200):
    variant = ab.assign(f"user{i}")
    # A=旧模型, B=新模型
    satisfaction = random.gauss(7.5 if variant == "A" else 7.8, 0.5)
    ab.record(variant, "satisfaction", satisfaction)

result = ab.analyze("satisfaction")
print(f"A满意度: {result['A_avg']:.2f}, B满意度: {result['B_avg']:.2f}")
print(f"差异: {result['diff']:.2f}")

# 攻击：定向注入操纵 B 组指标
print("
=== 指标操纵攻击 ===")
# 攻击者知道分组规则，将所有请求分配到 B 组
# 并注入高分反馈
for i in range(50):
    ab.record("B", "satisfaction", 10.0)  # 虚假满分

result = ab.analyze("satisfaction")
print(f"操纵后 A满意度: {result['A_avg']:.2f}, B满意度: {result['B_avg']:.2f}")
print(f"差异: {result['diff']:.2f} (被夸大)")

# 防御：异常检测
def detect_manipulation(metrics, metric, threshold=3.0):
    issues = []
    for variant in ["A", "B"]:
        vals = metrics[variant][metric]
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        std = (sum((x - avg) ** 2 for x in vals) / len(vals)) ** 0.5
        # 检测异常高分聚集
        max_count = sum(1 for v in vals if v == max(vals))
        if max_count > len(vals) * 0.3:
            issues.append(f"Variant {variant}: {max_count}个满分({max_count/len(vals)*100:.0f}%)，可能被操纵")
        # 检测标准差异常低
        if std < 0.1 and len(vals) > 10:
            issues.append(f"Variant {variant}: 标准差异常低({std:.3f})")
    return issues

issues = detect_manipulation(ab.metrics, "satisfaction")
print("
=== 异常检测 ===")
if issues:
    for i in issues:
        print(f"  [警告] {i}")
else:
    print("  无异常")
~~~

## 安全分析
A/B 测试操纵通过虚假数据影响决策，防御需要异常检测+分组随机化+数据验证
