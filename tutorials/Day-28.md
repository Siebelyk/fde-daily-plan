# Day 28：飞书/企微生态集成

> 🟡 客户落地实战与面试 · 第 6 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-28.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-28.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握企业微信 webhook 与飞书 API 集成，打通办公链路
2. 理解 JD 高频要求：打通飞书/企微/腾讯文档等办公链路
3. 实现一个企微推送 + 飞书多维表格读写的集成 demo

## 推荐资料

- 📚 文档 [企业微信机器人 webhook](https://developer.work.weixin.qq.com/document/path/91770)
- 📚 文档 [飞书开放平台 API](https://open.feishu.cn/document/)
- 📚 文档 [飞书多维表格 API](https://open.feishu.cn/document/server-docs/docs/bitable-v1/)

## Demo 练习：企微推送 + 飞书多维表格集成

实现企业微信机器人推送 + 飞书多维表格数据读写，打通办公链路

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 2h |

### 复现步骤

1. 实现企微 webhook 推送（markdown/text/卡片）
2. 实现飞书多维表格记录读写（mock）
3. 把 AI 生成的结果推送到企微群并写入飞书表格

## 保姆教程

## 原理速览
FDE 落地常要把 AI 能力嵌进客户已有的办公工具（飞书/企微），而非让客户改用新系统。
JD 反复要求'打通飞书/企微/腾讯文档办公链路'。本实验实现最常用的两种集成。

## 代码
```python
import json, urllib.request

# 1. 企业微信机器人推送
def wechat_push(webhook, content, msgtype="markdown"):
    payload = json.dumps({"msgtype":msgtype, msgtype:{"content":content}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error":str(e)}

# 演示（用你配置的 webhook，此处 mock 不真发）
def mock_wechat_push(content):
    print(f"[企微推送] {content[:60]}...")
    return {"errcode":0}

# 2. 飞书多维表格读写（mock）
BITABLE = []
def feishu_add_record(table_id, fields):
    record = {"record_id":f"rec{len(BITABLE)+1}", "fields":fields}
    BITABLE.append(record)
    return record
def feishu_list(table_id):
    return BITABLE

# 3. 集成闭环：AI生成 → 推企微 + 写飞书
def ai_pipeline(topic):
    # mock AI 生成日报
    report = f"【AI日报】{topic}：今日完成3项任务，效率提升15%"
    mock_wechat_push(report)                      # 推企微群
    rec = feishu_add_record("tblXXX", {"日报":report, "日期":"2026-07-28"})  # 写飞书
    return report, rec

report, rec = ai_pipeline("RAG 项目交付")
print(f"\n生成: {report}")
print(f"飞书记录: {rec}")
print(f"飞书表当前记录数: {len(feishu_list('tblXXX'))}")
print("\n💡 你的每日学习推送脚本就是这个模式（daily-plan.py 已用企微 webhook）")
```
企微webhook URL与飞书app_secret等同令牌，需保密入环境变量；集成最小权限。
企微 webhook URL 等于一个权限令牌，泄露=任何人可往群里发消息，必须保密不入库。
飞书 app_secret 同理走环境变量。集成时注意最小权限：只授需要的表格读写权限。

## 进阶挑战

1. 接入真实飞书多维表格 API，跑通一次记录写入
2. 实现企微卡片消息（带按钮交互），让群友可点击触发AI任务
3. 做一个飞书机器人：群里@它提问，它调RAG回答并@回复

---

## 明日预告

**Day 29：模型微调：SFT 数据与 LoRA 配置**
> 🟡 客户落地实战与面试 · 第 6 周
