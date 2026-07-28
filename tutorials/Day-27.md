# Day 27：客户沟通与方案设计

> 🟡 客户落地实战与面试 · 第 6 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-27.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-27.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握 FDE 客户沟通核心方法论：SPIN 提问挖掘需求 + 价值翻译
2. 学会把技术方案翻译成客户能懂的业务语言，避免技术自嗨
3. 处理客户异议的实战话术：'太贵''不安全''自己也能做'三大经典异议
4. 输出一份可交付的客户方案沟通模板，面试可直接演示

## 推荐资料

- 📄 文章 [SPIN 销售法-需求挖掘](https://hbr.org/2022/01/the-right-way-to-onboard-new-customers)
- 📚 文档 [产品需求文档模板](https://www.productplan.com/learn/prd/)

## Demo 练习：SPIN 需求挖掘 + 价值翻译 + 异议处理

FDE 面试必考'你怎么跟客户沟通'。实现需求挖掘+价值翻译+异议处理三件套，输出可直接拿去面试演示的客户沟通脚本。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 2h |

### 复现步骤

1. 用 SPIN 提问法结构化挖掘客户真实需求(场景-痛点-影响-需求确认)
2. 把技术指标翻译成业务价值(准确率→节省工时/降低风险/提升营收)
3. 处理三大经典客户异议,准备标准话术
4. 生成一份完整的客户方案沟通脚本,模拟演示

## 保姆教程

## 原理速览
FDE 6/6 岗位要求"客户沟通/需求拆解/驻场",但很多技术人只会讲参数不会讲价值。
客户不关心你的 RAG 用了什么 embedding 模型,他关心的是"能省我多少人天""能避免什么风险"。
沟通能力的核心 = **挖掘真需求(别客户说啥就做啥) + 翻译成业务语言 + 管理预期**。

### SPIN 提问法:FDE 挖需求的黄金框架
- **S (Situation) 情景**:"你们现在知识查询是怎么做的?"(了解现状,别评判)
- **P (Problem) 问题**:"文档太多找不到,新员工上手慢吗?"(挖痛点)
- **I (Implication) 影响**:"找不到 SOP 导致操作失误,一年损失多少?"(放大痛点,让他自己算账)
- **N (Need-payoff) 需求确认**:"如果有个系统能 3 秒找到准确答案,能省多少培训成本?"(让他自己说出价值)

### 价值翻译表(技术指标 → 业务语言)
| 技术人说的 | 客户听不懂 | 应该这么说 |
|---|---|---|
| 准确率 92% | ? | 100 个问题 92 个一次答对,减少人工二次核对 |
| 召回率 85% | ? | 知识库 1000 篇文档,能找到 850 篇相关内容 |
| P95 延迟 800ms | ? | 95% 的问题 1 秒内出答案,比人查文档快 100 倍 |
| 向量检索 | ? | 像懂语义的搜索,能理解'怎么报销'是在问流程 |

## 代码:客户沟通脚本生成器
```python
# FDE 客户沟通三件套:需求挖掘 + 价值翻译 + 异议处理
from dataclasses import dataclass
from typing import List

@dataclass
class ClientNeed:
    industry: str
    situation: str      # S:现状
    problem: str        # P:痛点
    implication: str    # I:影响
    need_payoff: str    # N:需求确认

@dataclass
class ValueTranslation:
    tech_metric: str     # 技术指标
    customer_lang: str   # 业务语言

# 三大经典异议的标准话术
OBJECTION_HANDLERS = {
    "太贵了": "理解您的顾虑。我们先算笔账:您说现在每月花 X 人天查文档,按人均 800/天就是 Y 元。这套系统部署后预计减少 70% 查询工时,3 个月回本,之后都是净省。我们可以先做 POC 验证效果,按效果付费。",
    "数据不安全": "这正是我们的设计重点:模型和数据都私有化部署在您内网,全程审计留痕,数据不出域。我们已服务 N 家政企/金融客户,均通过安全审查,可以提供部署架构图给您安全团队评审。",
    "我们自己也能做": "当然可以,这也是贵司技术实力的体现。我们的价值在于帮您把 3 个月的周期压缩到 3 周上线,避免踩坑。我们的方案您也可以当参考,即使自研也能少走弯路。"
}

def generate_pitch(need: ClientNeed, values: List[ValueTranslation]) -> str:
    """生成完整的客户方案沟通脚本"""
    pitch = f"""===== 客户方案沟通脚本 [{need.industry}] =====

【1. 需求挖掘 - SPIN 提问】
S 现状: {need.situation}
P 痛点: {need.problem}
I 影响: {need.implication}
N 需求确认: {need.need_payoff}

【2. 价值翻译 - 技术指标转业务语言】"""
    for v in values:
        pitch += f"
  - {v.tech_metric} → {v.customer_lang}"
    pitch += "

【3. 异议预案】"
    for obj, reply in OBJECTION_HANDLERS.items():
        pitch += f"
  客户说'{obj}':
    → {reply}"
    pitch += "

【4. 收尾 - 明确下一步】
  今天对齐了需求和预期效果,我回去整理一份 POC 方案,包含部署架构、排期和效果验证指标,下周二前发您评审,您看可以吗?"
    return pitch

# 示例:金融客户知识库场景
need = ClientNeed(
    industry="金融",
    situation="你们投研团队现在查报告、查合规文件是怎么操作的?",
    problem="几百份研报散落在各处,新人找不到,老员工也要翻半天",
    implication="找资料慢导致响应客户需求慢,合规查询出错还可能被监管处罚",
    need_payoff="如果有个系统能 3 秒从所有研报里找到答案并标明出处,你们投研效率能提升多少?"
)
values = [
    ValueTranslation("准确率 92%", "100 个问题 92 个一次答对,减少人工核对工时"),
    ValueTranslation("引用溯源", "每个答案都标注来源报告和页码,合规审计可追溯"),
    ValueTranslation("私有化部署", "数据不出内网,满足金融监管要求"),
]
print(generate_pitch(need, values))

# 保存脚本到文件,面试可直接展示
with open("client_pitch_finance.md","w") as f: f.write(generate_pitch(need, values))
print("\n✅ 客户沟通脚本已生成,可直接用于面试演示")
```

## 真实案例
某 FDE 跟银行客户对接,客户第一句话是"我们要做大模型"。如果直接上技术方案就输了——FDE 用 SPIN 挖出真实痛点是"合规查询太慢被监管约谈",最终交付的不是"大模型平台"而是"合规问答助手",3 周上线解决核心问题。**客户说的往往不是真需求,挖出来的才是**。

客户沟通中切忌过度承诺:不保证准确率100%、不承诺上线零问题。用POC验证效果后再承诺,管理预期避免交付扯皮。涉及数据安全主动提私有化方案。
客户沟通中切忌过度承诺:不保证准确率 100%、不承诺上线后零问题。用"预计""目标""POC 验证后确认"等措辞管理预期,避免交付后扯皮。涉及数据安全时主动提私有化方案,别等客户问。


## 进阶挑战

1. 录制一段 3 分钟客户沟通模拟,用脚本演练 SPIN 提问全流程
2. 针对你目标行业的一个真实场景,写一份'技术→业务'价值翻译卡
3. 研究一个 FDE 搞砸客户沟通的反面案例,提炼三条避坑原则

---

## 明日预告

**Day 28：企微/飞书生态集成**
> 🟡 客户落地实战与面试 · 第 6 周
