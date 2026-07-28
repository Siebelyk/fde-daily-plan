# Day 27：客户沟通与方案设计

> 🟡 客户落地实战与面试 · 第 6 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-27.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-27.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 掌握把技术方案翻译成客户能懂的业务价值
2. 理解客户高管 vs 技术对接人的不同沟通策略
3. 构建方案文档生成器，输出客户可读的方案

## 推荐资料

- 📄 文章 [Anthropic - 客户落地与 Agent](https://www.anthropic.com/engineering/building-effective-agents)
- 📚 文档 [OpenAI Cookbook - 应用案例](https://cookbook.openai.com/)
- 📄 文章 [HBR - 需求沟通方法](https://hbr.org/2022/01/the-right-way-to-onboard-new-customers)

## Demo 练习：技术方案→业务价值翻译器

把技术方案翻译成客户能懂的业务价值。写一份'给客户讲'的方案——FDE 面试必考'你怎么跟客户沟通'。

| 难度 | 预计时间 |
|------|----------|
| 基础 | 2h |

### 复现步骤

1. 定义技术指标到业务价值的映射规则
2. 实现方案文档生成器，输出客户可读版本
3. 准备高管版与技术版两套话术

## 保姆教程

## 原理速览
FDE 最易被忽视的能力：沟通。6/6 JD 要求'客户沟通、需求拆解、方案转化'。
技术人常犯的错：跟客户讲'准确率95%、P99延迟300ms'，客户听不懂。
要翻译成'员工找资料时间从15分钟降到1分钟，效率提升15倍'。本实验做这个翻译器。

## 代码
```python
# 技术→业务价值映射表
VALUE_MAP = {
    "准确率95%": "100个问题95个答对，错误率从50%降到5%，减少返工",
    "P99延迟300ms": "响应快到无感，员工不用等，体验接近秒回",
    "成本下降50%": "同样的预算服务量翻倍，或同样服务量省一半钱",
    "私有化部署": "数据不离开公司内网，满足合规与安全要求",
    "RAG知识库": "新人不用翻文档找答案，直接问，培训周期缩短60%",
    "Agent自动化": "重复流程自动跑，人力释放到高价值工作",
}

def translate(tech_point):
    return VALUE_MAP.get(tech_point, f"（需补充业务价值翻译：{tech_point}）")

def gen_proposal(client, scene, tech_points, audience="高管"):
    doc = f"# {client} {scene} AI 落地方案\n\n"
    doc += f"## 给{'决策层' if audience=='高管' else '技术团队'}的版本\n\n"
    if audience == "高管":
        doc += "### 业务价值\n"
        for tp in tech_points:
            doc += f"- {translate(tp)}\n"
        doc += "\n### 投入产出\n- 一次性投入：开发与部署\n- 持续收益：效率提升×人员规模×工作时长\n"
    else:
        doc += "### 技术架构\n"
        for tp in tech_points: doc += f"- {tp}\n"
        doc += "\n### 集成方式\n- API对接 / 私有化部署 / 数据回流\n"
    return doc

tech = ["准确率95%", "P99延迟300ms", "成本下降50%", "私有化部署", "RAG知识库"]
print(gen_proposal("XX集团", "企业知识库", tech, "高管"))
print("="*40)
print(gen_proposal("XX集团", "企业知识库", tech, "技术"))
print("\n💡 同一方案，高管看价值，技术看架构，沟通对象不同话术不同")
```
方案文档按客户授权范围分享留存；演示用脱敏样本防数据外泄。
方案文档可能含客户业务数据与商业机密，分享与留存要按客户授权范围控制；
演示数据用脱敏样本，避免真实客户数据进入方案材料外泄。

## 进阶挑战

1. 为你的一个 RAG 项目写一版高管话术，练习3分钟讲清业务价值
2. 做一个'反对意见应对表'：客户嫌贵/嫌不准/嫌不稳怎么回
3. 录制一段模拟客户拜访视频，练习需求挖掘提问

---

## 明日预告

**Day 28：飞书/企微生态集成**
> 🟡 客户落地实战与面试 · 第 6 周
