# Day 38: Human-in-the-Loop 绕过攻击

> 多 Agent 安全 | 第 6 周

## Demo: HITL 绕过实验：操纵 Agent 跳过人工确认

构造场景展示攻击者如何通过注入使 Agent 绕过人工确认直接执行高危操作

- 难度：进阶
- 预计时间：2h

## 复现步骤

- 1. 搭建带 HITL 的 Agent
- 2. 构造绕过确认的注入
- 3. 观察高危操作被执行
- 4. 实现强制确认机制
- 5. 测试效果

## 保姆教程

## 代码
~~~python
import re

class HITLAgent:
    def __init__(self):
        self.high_risk = {"send_email", "delete", "transfer", "execute_sql"}
        self.pending_confirmations = {}

    def decide(self, action, params):
        if action in self.high_risk:
            # 需要 Human-in-the-Loop 确认
            conf_id = f"conf_{len(self.pending_confirmations)}"
            self.pending_confirmations[conf_id] = (action, params)
            return {"need_confirm": True, "conf_id": conf_id, "action": action}

        # 低风险直接执行
        return {"executed": True, "action": action, "result": f"完成 {action}"}

    def confirm(self, conf_id, approved):
        if conf_id not in self.pending_confirmations:
            return "确认ID不存在"
        action, params = self.pending_confirmations.pop(conf_id)
        if approved:
            return {"executed": True, "action": action, "result": f"已确认执行 {action}"}
        return {"rejected": True, "action": action}

agent = HITLAgent()

# 正常流程：高危操作需要确认
print("=== 正常 ===")
r = agent.decide("send_email", {"to": "user@example.com"})
print(f"决策: {r}")
if r.get("need_confirm"):
    r2 = agent.confirm(r["conf_id"], True)
    print(f"确认后: {r2}")

# 攻击：通过注入让 Agent 认为是低风险
print("
=== HITL 绕过攻击 ===")
# 攻击者注入：将高危操作伪装成低风险
attack_action = "search"  # 伪装名称
attack_params = {"query": "'; DROP TABLE users; --"}
# 但实际调用的是高危操作
print(f"伪装操作: {agent.decide(attack_action, attack_params)}")
print("高危SQL注入被当作搜索直接执行！")

# 防御：操作+参数双重校验
def safe_decide(agent, action, params, user_role="user"):
    # 1. 操作名白名单
    safe_actions = {"search", "read", "summarize", "get_weather"}
    if action not in safe_actions and action not in agent.high_risk:
        return {"blocked": True, "reason": f"未知操作 {action}"}

    # 2. 参数危险内容检测
    for v in params.values():
        if re.search(r"(?i)(drop|delete|truncate|;--|insert|update)", str(v)):
            return {"blocked": True, "reason": "参数含危险操作"}

    # 3. 高危操作强制确认（不可绕过）
    if action in agent.high_risk and user_role != "admin":
        return {"need_confirm": True, "action": action}

    return agent.decide(action, params)

print("
=== 防御 ===")
print(f"  {safe_decide(agent, 'search', {'query': 'DROP TABLE users'})}")
print(f"  {safe_decide(agent, 'send_email', {'to': 'a@b.com'})}")
~~~

## 安全分析
HITL 绕过的核心是伪装高危操作为低风险，防御需要操作名+参数双重校验+强制确认
