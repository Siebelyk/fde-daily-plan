# Day 29：模型微调：SFT 与 LoRA

> 🟡 客户落地实战与面试 · 第 6 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-29.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-29.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 Post-Training 全景：CPT 预训练、SFT 指令微调、RL 对齐
2. 掌握 SFT 数据构建与 LoRA 高效微调流程
3. 理解何时该微调、何时该 RAG，避免方案选型错误
4. 掌握语料处理 pipeline：清洗、去重、质量过滤、敏感信息脱敏
5. 理解数据标注流程与格式转换（SFT/评测集）
6. 了解 EasyDataset/Data-Juicer 等语料处理平台

## 推荐资料

- 🛠 工具 [LLaMA-Factory 微调框架](https://github.com/hiyouga/LLaMA-Factory)
- 🛠 工具 [Data-Juicer 语料处理](https://github.com/modelscope/data-juicer)
- 📝 论文 [LoRA - 低秩微调](https://arxiv.org/abs/2106.09685)

## Demo 练习：LLaMA-Factory SFT + 语料处理

微调是 1/6 岗位要求。用 LLaMA-Factory 跑 SFT+LoRA，处理语料——虽非主线但了解流程面试能加分。

| 难度 | 预计时间 |
|------|----------|
| 进阶 | 约 4.5h |

### 复现步骤

1. 构建 SFT 数据集（指令-输入-输出格式）
2. 配置 LoRA 微调参数（rank/alpha/dropout/目标层）
3. 演示微调与评测流程，理解何时该微调
4. 实现清洗：去空、去重复、去乱码、长度过滤
5. 实现敏感信息脱敏：手机号/身份证/邮箱打码
6. 把清洗后语料转成 SFT 训练集与评测集两种格式

## 保姆教程

## 原理速览
Post-Training = 模型出厂后的再训练。CPT 灌领域知识，SFT 学指令遵循，RL 对齐人类偏好。
FDE 多数场景用 RAG 而非微调（RAG 即插即用、可溯源），但客户要'风格统一/领域专精'时需微调。
本实验演示 SFT+LoRA 流程，重点是'何时该微调'的判断。

## 代码
```python
import json

# 1. 构建 SFT 数据集（Alpaca 格式）
def build_sft_dataset(items):
    data = []
    for instruction, inp, output in items:
        data.append({"instruction":instruction, "input":inp, "output":output})
    return data

samples = [
    ("用客户语气写退款回复", "订单号A123", "尊敬的客户，订单A123已受理退款，3-5工作日到账"),
    ("判断售后紧急程度", "客户投诉产品质量", "高紧急：产品质量投诉需2小时内响应"),
    ("总结工单", "用户反馈系统卡顿", "工单摘要：系统性能问题，已转技术团队"),
]
dataset = build_sft_dataset(samples)
print("=== SFT 数据集（Alpaca格式）===")
print(json.dumps(dataset[:2], ensure_ascii=False, indent=2))
print(f"共 {len(dataset)} 条，微调需扩到 1000+ 条才有效果")

# 2. LoRA 配置
LORA_CONFIG = {
    "base_model": "Qwen2.5-7B-Instruct",
    "lora_rank": 8,        # 秩，越大表达能力越强越易过拟合
    "lora_alpha": 16,      # 缩放系数，通常=2*rank
    "lora_dropout": 0.05,
    "target_modules": ["q_proj","k_proj","v_proj","o_proj"],  # 注意力层
    "learning_rate": 2e-4,
    "num_epochs": 3,
    "per_device_batch": 4,
    "gradient_accumulation": 4,
}
print("\n=== LoRA 微调配置 ===")
for k,v in LORA_CONFIG.items(): print(f"  {k}: {v}")

# 3. 何时微调 vs 何时 RAG
DECISION = [
    ("知识更新频繁", "RAG", "微调后知识固化，更新成本高"),
    ("统一输出风格", "微调", "RAG 难统一风格，微调直接改模型行为"),
    ("领域专精术语", "微调+RAG", "微调学术语表达，RAG补最新知识"),
    ("可溯源要求高", "RAG", "RAG答案带引用，微调答案不可溯源"),
    ("数据量少(<100条)", "RAG/Prompt", "微调数据不足易过拟合"),
]
print("\n=== 微调 vs RAG 选型 ===")
for scene, choice, reason in DECISION:
    print(f"  {scene:12} → {choice:8} ({reason})")
```
微调数据需合规脱敏；含客户数据微调有记忆泄露风险，敏感场景优先RAG。
微调数据来源要合规：含客户数据的微调可能把客户信息'记住'后泄露给其他用户
（训练数据记忆攻击）。金融/政企场景优先 RAG，确需微调用脱敏数据并做成员推断测试。

---

## 第二部分：语料处理 pipeline + 标注格式转换

## 原理速览
'有多少人工就有多少智能'——语料质量决定模型/系统上限。JD 要求熟悉语料处理平台。
FDE 落地时客户给的数据往往脏乱差，本实验实现最小语料处理 pipeline，是数据工程基本功。

## 代码
```python
import re, hashlib
from collections import defaultdict

raw = [
    "退款政策：7天内可退，联系客服400-1234-5678",
    "退款政策：7天内可退，联系客服400-1234-5678",  # 重复
    "",                                              # 空
    "保修1年，工程师电话13800138000，身份证110101199001011234",
    "asdfghjkl!!!",                                   # 乱码
    "客服热线4001234，邮箱support@company.com",
]

# 1. 清洗：去空、去重、长度过滤
def clean(docs):
    seen, out = set(), []
    for d in docs:
        if not d.strip() or len(d) < 8: continue   # 去空去短
        h = hashlib.md5(d.encode()).hexdigest()
        if h in seen: continue                      # 去重
        seen.add(h); out.append(d)
    return out

# 2. 敏感信息脱敏
PII_PATTERNS = {
    "phone": (r"1[3-9]\d{9}", "[手机]"),
    "idcard": (r"\d{17}[\dXx]", "[身份证]"),
    "email":  (r"[\w.-]+@[\w.-]+\.\w+", "[邮箱]"),
    "tel400": (r"400-?\d{3,4}-?\d{3,4}", "[客服电话]"),
}
def desensitize(text):
    for name, (pat, rep) in PII_PATTERNS.items():
        text = re.sub(pat, rep, text)
    return text

# 3. 质量过滤（mock：含正常中文比例）
def quality_filter(docs):
    return [d for d in docs if sum(1 for c in d if '\u4e00'<=c<='\u9fff')/max(len(d),1) > 0.2]

cleaned = quality_filter(clean(raw))
print("=== 清洗后 ===")
for d in cleaned: print(f"  原文: {d}")
print("\n=== 脱敏后 ===")
for d in cleaned: print(f"  脱敏: {desensitize(d)}")

# 4. 转标注格式
def to_sft(docs):
    return [{"instruction":"总结这段政策","input":d,"output":"(待标注)"} for d in docs]
def to_eval(docs):
    return [{"query":d,"gold":"(待标注)","relevant_docs":[i]} for i,d in enumerate(docs)]
print("\n=== SFT格式样例 ===")
import json; print(json.dumps(to_sft(cleaned)[:1], ensure_ascii=False, indent=2))
```
脱敏须彻底并反向校验无残留；客户数据留存销毁需明确期限与审计。
语料脱敏必须彻底：手机号/身份证/邮箱泄露=客户隐私事故。脱敏后还要做反向校验
（正则扫描确认无残留）。客户数据处理的留存与销毁要有明确期限与审计。

## 真实案例：通用模型"不够懂行业术语"，用 LoRA 微调一周行业准确率拉满

**背景**：一个 FDE 给客户用通用大模型做行业问答，客户反馈"它不够懂我们行业术语——把我们'探针卡盘'答成普通'卡盘'，专业问题净答偏"。通用模型没见过客户的垂直术语，准确率上不去。

**问题**：通用模型对垂直领域术语/工艺/参数理解浅，靠 prompt 纠正成本高且不稳定。需要在不大改模型的前提下，让它"记住"行业术语用法——这正是 LoRA 微调的场景。

**定位过程**：他先判断"该不该微调"——试过 RAG（把术语手册接进去）有效但慢、且术语上下文仍不内化；客户要求"快且准"，且有一定量高质量问答语料，符合微调条件。决定用 LoRA（只调少量参数，单卡能跑，不破坏原模型）。

**做法**：用 LLaMA-Factory 做 LoRA SFT，关键是先把原始语料清洗成指令格式。
```python
# 第1步：语料处理——原始问答清洗成ShareGPT指令格式
import json
raw = [("探针卡盘校准流程是什么？","先归零、再装标准件、按工艺手册步骤校准。"),
       ("晶圆对位偏差多少合格？","X/Y偏差≤2μm为合格，超差需重新对位。")]
def to_instruction(qa):
    return {"conversations":[{"from":"human","value":qa[0]},
                             {"from":"gpt","value":qa[1]}]}
data = [to_instruction(x) for x in raw]
json.dump(data, open("train.json","w",ensure_ascii=False),ensure_ascii=False)
# 第2步：LLaMA-Factory 配置（yaml示意）
config = """
model_name_or_path: Qwen/Qwen2-7B-Instruct
finetuning_type: lora        # 只调LoRA少量参数
lora_rank: 8; lora_alpha: 16
dataset: industry_qa
template: qwen
num_train_epochs: 3
learning_rate: 5e-5
cutoff_len: 1024
"""
# 命令：llamafactory-cli train config.yaml  （单卡可跑）
```
评估：用 30 道行业术语题测，对比微调前后准确率。

**结果**：通用模型在行业术语题准确率 62% → 88%（微调后"探针卡盘""晶圆对位偏差"等专业问答答准）；LoRA 只调了 0.5% 参数，单卡 8 小时训完，成本远低于全参微调。客户认可"现在懂我们的话了"。

**踩坑**：第一版他直接把原始文档丢去训练，模型学到的是"复述文档"而非"回答问题"——语料必须先转成"问-答"指令格式才有用。还有语料里有脏数据（错答、重复），他先清洗去重，脏数据训进去模型直接学坏。学习率一开始设太大（1e-4）把模型训崩，降到 5e-5 才稳。另外他没留评测集，差点过拟合，补了 hold-out 评测集监控。

**可复用经验**：垂直领域术语不准，先试 RAG，不够且有好语料再上 LoRA。关键是语料先清洗成"问-答指令格式"（不是原始文档），设小学习率 + 留评测集防过拟合。LoRA 调 0.5% 参数、单卡能跑、不毁原模型，是 FDE 做行业适配性价比最高的微调方式。


## 进阶挑战

1. 用 LLaMA-Factory 跑一次真实 LoRA 微调（小模型+小数据集）
2. 构建 100 条行业 SFT 数据，观察微调后风格变化
3. 实现一个微调 vs RAG 决策树，输入场景特征输出推荐方案
4. 接入 Data-Juicer 跑一次真实语料处理，对比自写 pipeline 效果
5. 实现去重用 MinHash（近似去重），对比精确 md5 去重的召回差异
6. 构建一个 50 条评测集，标注 query/gold/relevant_docs 三元组

---

## 明日预告

**Day 30：面试冲刺：知识图谱与模拟面试**
> 🟡 客户落地实战与面试 · 第 6 周
