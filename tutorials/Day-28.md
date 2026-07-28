# Day 28：企微/飞书生态集成

> 🟡 客户落地实战与面试 · 第 6 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-28.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-28.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 FDE 集成客户已有系统的价值:能接生态才是真'落地'，不是孤立 demo
2. 实现企业微信机器人推送:向群聊发送 markdown 消息(真实可用代码)
3. 实现飞书多维表格写入:把 LLM 输出存进客户的多维表格，打通工作流
4. 掌握 OAuth + Webhook 两种集成模式的适用场景与安全要点

## 推荐资料

- 📚 文档 [企业微信开发者文档](https://developer.work.weixin.qq.com/document/path/91770)
- 📚 文档 [飞书开放平台文档](https://open.feishu.cn/document/)
- 📚 文档 [飞书多维表格 API](https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview)

## Demo 练习：企微机器人推送 + 飞书多维表格写入

真实交付高频需求:把 LLM 能力接进客户已有的企微/飞书。实现企微推送+飞书多维表格写入——能接生态才是'落地',面试讲这个体现交付能力。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 2h |

### 复现步骤

1. 配置企业微信机器人,获取 webhook URL
2. 实现企微 markdown 消息推送函数,发送测试消息到群
3. 配置飞书应用,获取 app_id/app_secret 和多维表格 token
4. 实现飞书多维表格 API 写入,把 LLM 结果存进表格

## 保姆教程

## 原理速览
FDE 交付到客户现场,客户系统往往不是白纸——他们用企微/飞书/钉钉。**能接进客户已有生态,你的方案才算"落地"**,否则只是个孤立 demo。
两种集成模式:
- **Webhook(出站)**:LLM 结果主动推到群聊/表格,简单直接,适合通知/报告场景
- **OAuth + API(双向)**:订阅群消息触发 LLM,回复到群,适合智能助手场景

### 真实场景
某 FDE 给客户做合同审查,客户说"我们用飞书管理合同"。FDE 没让客户改用新系统,而是接飞书多维表格:LLM 审查结果直接写回表格的"风险"列,客户不用切换工具,接受度立刻高。**融入客户习惯,而不是改变客户习惯**。

## 代码:企微推送 + 飞书多维表格集成
```python
import json, urllib.request

# ========== 1. 企业微信机器人推送 ==========
def send_wechat(webhook_url, content, msg_type="markdown"):
    """向企微群发送消息(真实可用,替换 webhook_url 即可)"""
    payload = json.dumps({
        "msgtype": msg_type,
        "markdown": {"content": content}
    }).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode())
            return "ok" if res.get("errcode") == 0 else f"error: {res}"
    except Exception as ex:
        return f"failed: {ex}"

# 模拟 LLM 审查结果推送到企微
audit_result = """# 合同审查报告
**合同**: XX采购合同 v2
**风险等级**: 🟡 中风险
**发现 3 项问题**:
1. 付款条款未约定逾期利息(建议补充)
2. 知识产权归属不明(需明确)
3. 终止条款偏向乙方(建议调整)
**建议**: 修订后可签"""
# webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
# print("企微推送:", send_wechat(webhook_url, audit_result))
print("[企微推送函数已就绪] 替换 webhook_url 即可发送到真实群聊")

# ========== 2. 飞书多维表格写入 ==========
def feishu_get_token(app_id, app_secret):
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())["tenant_access_token"]

def feishu_write_bitable(token, app_token, table_id, fields):
    """向飞书多维表格写入一行数据"""
    url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}"
           f"/tables/{table_id}/records")
    payload = json.dumps({"fields": fields}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {token}", "Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

# 模拟把审查结果写入多维表格
record = {
    "合同名称": "XX采购合同v2",
    "风险等级": "中风险",
    "问题数": 3,
    "审查建议": "修订后可签",
    "LLM原始报告": audit_result
}
# token = feishu_get_token("your_app_id", "your_secret")
# print("飞书写入:", feishu_write_bitable(token, "app_token", "table_id", record))
print("[飞书写入函数已就绪] 填入 app_id/secret/table_id 即可写入真实表格")
print("\n✅ 企微+飞书集成代码完成,这是真实交付的高频场景")
```

## 真实案例：让客户用独立 App，客户说"没人愿意再学一个工具"——接进企微飞书

**背景**：一个 FDE 做了 LLM 知识助手，让客户用独立 App/网页。客户反馈："员工每天用企微和飞书，没人愿意为了问个问题再装一个 App、学一个新工具。"adoption 卡死，产品上线没人用。

**问题**：FDE 造了一个新工具，但用户习惯在企微/飞书，新增工具=新增学习成本=没人用。FDE 要的不是"造工具"，是"把能力嵌进用户已经在用的地方"。

**定位过程**：他意识到 adoption 的敌人是"换工具的摩擦"，解法是"不造新 App，把助手接进企微机器人和飞书多维表格"——用户在每天用的群里直接 @ 机器人问，零学习成本。

**做法**：做企微机器人（webhook 接收消息→调 LLM→回发）+ 飞书多维表格写入（Agent 结果落表）。
```python
# 企微机器人：接收群消息，调LLM后回发
from fastapi import FastAPI, Request
import requests
app = FastAPI()
WECOM_TOKEN = "xxx"
def llm_answer(q):
    import openai
    r = openai.OpenAI().chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"user","content":q}])
    return r.choices[0].message.content

@app.post("/wecom/callback")
async def wecom(req: Request):
    data = await req.json()
    msg = data.get("text", {}).get("content", "").strip()
    if not msg: return "ok"
    ans = llm_answer(msg)                       # 调知识助手
    # 回发到企微群
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send",
        json={"key":"xxx","msgtype":"text","text":{"content":ans}})
    return "ok"

# 飞书多维表格：Agent把结果写入表格供团队查阅
def write_feishu_bitable(record):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE}/records"
    requests.post(url, headers={"Authorization":f"Bearer {TENANT_ACCESS}"},
        json={"fields":{"问题":record["q"],"答案":record["a"],"时间":record["t"]}})
```

**结果**：员工在企微群里 @ 机器人直接问产品问题、秒回，adoption 从"没人用 App"变成"日均 200+ 次群内调用"；飞书表格自动沉淀问答记录供团队查阅。客户从抗拒变成主动推广给更多部门。

**踩坑**：第一版他坚持做独立 App 还做了引导教程，用户依然不用——验证了"换工具的摩擦"比想象大。还有企微回调要校验 token 防伪造，他一开始没校验被刷垃圾消息；飞书 token 有时效，他加了自动刷新。另外企微消息有长度限制，长答案他做了分段发送。

**可复用经验**：FDE 集成的目标是"嵌进用户已有的工作流"，不是造新 App。企微机器人 + 飞书多维表格把 LLM 能力送进用户每天用的地方，adoption 才不卡。**最好的新工具是不让用户学新工具**——把能力挂在他们已经打开的企微/飞书里，是落地最关键的一步。

## 面试高频问答
问:客户已有飞书/企微怎么集成?
答:别让客户换工具。用企微 Webhook 推送、飞书 API 写多维表格,LLM 能力融入客户已有生态。最低摩擦落地。

## 简历话术
- ❌ 弱表述:了解企微/飞书生态集成
- ✅ 强表述:实现企微机器人推送+飞书多维表格写入,把 LLM 能力融入客户已有生态,零学习成本
Webhook URL 等于密码,泄露即被滥用,严禁放前端。飞书 token 需自动刷新。接收消息必须验签防伪造,避免被恶意触发消耗成本。
Webhook URL 等于密码,泄露了任何人都能向群发消息,必须保密且不放前端代码。飞书 token 有有效期,生产环境要自动刷新。接收群消息时验证飞书签名,防止伪造请求触发 LLM(消耗成本/泄露数据)。


## 进阶挑战

1. 给企微推送加签名校验,防止 webhook 被恶意调用
2. 实现飞书事件订阅:收到群消息自动触发 LLM 回复
3. 研究飞书妙搭(低代码)如何嵌入 LLM 能力,做无代码集成

---

## 明日预告

**Day 29：模型微调：SFT 与 LoRA**
> 🟡 客户落地实战与面试 · 第 6 周
