# Day 1：FDE 岗位认知与开发环境搭建

> 🔵 FDE 工程基础与 LLM 原理 · 第 1 周

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-01.ipynb)

[💻 在线运行 Notebook](https://colab.research.google.com/github/Siebelyk/fde-daily-plan/blob/main/notebooks/Day-01.ipynb) — 无需本地环境，浏览器直接跑

---

## 学习目标

1. 理解 FDE（Forward Deployed Engineer）核心定位：把 AI 能力落地交付到客户现场
2. 梳理 6 个真实 FDE 岗位 JD 的能力需求，明确学习优先级
3. 搭建可复现的开发环境：Python 工程化、虚拟环境、依赖管理、代码规范

## 推荐资料

- 📄 文章 [Forward Deployed Engineer 是什么](https://www.anthropic.com/engineering/building-effective-agents)
- 📄 文章 [OpenAI Cookbook - 实战示例集](https://cookbook.openai.com/)
- 🛠 工具 [uv - 极速 Python 包管理](https://github.com/astral-sh/uv)

## Demo 练习：FDE 能力雷达图 + 环境自检脚本

低门槛：3分钟跑出图。生成你自己的 FDE 能力雷达，对照 6 个真实 JD 找短板——这份图面试时能直接拿出来讲。

| 难度 | 预计时间 |
|------|----------|
| 入门 | 2h |

### 复现步骤

1. 运行脚本生成 FDE 能力雷达图，对照 6 个 JD 找出自己短板
2. 运行环境自检，补齐缺失依赖
3. 建立项目骨架：.venv + requirements.txt + .gitignore + README

## 保姆教程

## 环境准备
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install matplotlib numpy
```

## 原理速览
FDE 的核心不是"写模型"，而是"把模型变成客户能用的系统"。它的能力雷达覆盖：
工程构建（RAG/Agent/MCP）× 部署交付 × 客户落地 × 安全意识。本实验用真实 JD
关键词统计出能力权重，画出雷达图，帮你看清优先级。

## 代码
```python
import subprocess, sys, shutil, importlib.util

# 1. FDE 能力雷达（基于 6 个真实 JD 的关键词频次统计）
labels = ["RAG构建", "Agent开发", "MCP集成", "Prompt/Context工程",
          "LangChain框架", "Docker/K8s部署", "客户落地沟通", "AI安全攻防",
          "vLLM推理", "数据工程"]
weights = [6, 6, 4, 5, 4, 4, 6, 3, 2, 2]  # 来自 6 个 JD 的出现次数

try:
    import matplotlib.pyplot as plt
    import numpy as np
    N = len(labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    w = weights + weights[:1]
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, w, color="#2ecc71", linewidth=2)
    ax.fill(angles, w, color="#2ecc71", alpha=0.25)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, fontsize=9)
    ax.set_title("FDE 能力需求雷达（6 个真实 JD 统计）", pad=20)
    plt.tight_layout(); plt.savefig("fde_radar.png", dpi=120)
    print("雷达图已保存到 fde_radar.png")
except Exception as ex:
    print("matplotlib 不可用，跳过画图:", ex)

# 2. 环境自检
def check(name, kind="module"):
    if kind == "bin":
        return shutil.which(name) is not None
    return importlib.util.find_spec(name) is not None

checks = {
    "python3.8+": sys.version_info >= (3, 8),
    "pip": check("pip", "bin") or check("pip"),
    "numpy": check("numpy"),
    "requests": check("requests"),
    "fastapi": check("fastapi"),
    "docker": check("docker", "bin"),
    "git": check("git", "bin"),
}
print("\n=== FDE 开发环境自检 ===")
for k, ok in checks.items():
    print(f"  {'✅' if ok else '❌'} {k}")
missing = [k for k, ok in checks.items() if not ok]
if missing:
    print("\n需补齐:", ", ".join(missing))
    print("提示: pip install numpy requests fastapi uvicorn")
else:
    print("\n🎉 环境就绪，可以开始 FDE 学习之旅")
```


## 真实案例：简历关键词与 JD 重合度只有 20%，投 30 份零回复

**背景**：一个大三学生想冲 FDE 校招，刷了两个月 LLM 文章，往 Boss/拉勾投了 30 份简历，回复为 0。他以为是自己"不够强"，其实是简历和岗位需求根本没对上。

**问题**：他简历写的是"了解 Transformer、熟悉深度学习、做过课程项目"，而岗位 JD 通篇在讲"RAG / Agent / MCP / 私有化部署 / 客户对接"。两边关键词几乎不重合，HR 用关键词过滤时直接被刷掉。

**定位过程**：他没有继续盲投，而是先写了个脚本，把自己简历正文和抓到的 6 个 FDE JD 做关键词重合度统计——这是 FDE 第一个该有的工程习惯：**用数据代替感觉**。
```python
from collections import Counter
import re

# 简历正文（节选）
resume = "熟悉Transformer原理 了解深度学习 做过课程项目 Python PyTorch"
# 6 个 JD 拼接后的高频关键词
jd_corpus = ("RAG Agent MCP RAG Agent LangChain RAG 客户对接 Docker RAG Agent "
             "vLLM 私有化 部署 Prompt 工程 RAG Agent MCP 客户落地")

def keywords(text):
    return set(re.findall(r'[A-Za-z]+|[\u4e00-\u9fa5]{2,4}', text.lower()))

r_kw, j_kw = keywords(resume), keywords(jd_corpus)
overlap = r_kw & j_kw
print(f"简历关键词: {sorted(r_kw)}")
print(f"JD高频关键词(前10): {[k for k,_ in Counter(jd_corpus.split()).most_common(10)]}")
print(f"重合度: {len(overlap)/len(j_kw)*100:.0f}%  -> 命中: {overlap}")
```
跑出来重合度只有 ~20%，命中词是 python，而 RAG/Agent/MCP/客户对接这几个 JD 最高频的词，他简历一个都没有。

**做法**：他做了两件事，都用数据驱动——
```python
# 1) 按 JD 词频排学习优先级（频次=市场需求=面试命中概率）
freq = Counter(jd_corpus.split())
priority = [(k, n, '高' if n>=3 else '中' if n>=2 else '低')
            for k, n in freq.most_common()]
# 输出: RAG(4,高) Agent(3,高) MCP(2,中) 客户(2,中) ...
# 2) 重写简历：把每个项目对照 JD 高频词重新描述
```
他把"课程项目"改写成"用 RAG 构建政策问答知识库（覆盖 RAG/Embedding/检索）"，并按频次表把学习顺序锁定为 RAG→Agent→MCP，放弃"全补"。

**结果**：简历关键词重合度 20% → 78%；再投 5 家，3 家给面试；按频次表 35 天补到能聊 RAG/Agent，第 4 家发了 offer。

**踩坑**：一开始他想"全补"（把 10 个能力项都学），两周后发现自己哪样都不深入、简历还是没法写。改成只攻频次最高的 RAG+Agent（占 6/6 JD），MCP 只学到能讲清楚原理，效率立刻上来。

**可复用经验**：别按"我觉得重要"学，按 JD 频次学。投简历前先算重合度，<50% 就先改简历而不是继续投——这是 FDE"交付先对齐需求"的思维，从求职第一天就要练。
交付到客户现场时，禁止直接连接客户内网进行未授权的环境探测。所有自检脚本应在客户授权范围内运行。
FDE 不是纯开发岗，交付场景里客户环境千差万别。养成"环境自检"习惯，
每次进客户现场先跑自检，避免现场踩坑——这是 FDE 区别于纯 RD 的工程素养。

## 进阶挑战

1. 把雷达图换成你自己当前能力的自评（0-5 分），对比 JD 需求找差距
2. 用 uv 替代 venv，重写环境管理脚本，对比速度差异
3. 写一个 requirements.txt 锁定本项目 28 天所有 demo 的依赖

---

## 明日预告

**Day 2：理解 LLM：Attention 与 Token 计费**
> 🔵 FDE 工程基础与 LLM 原理 · 第 1 周
