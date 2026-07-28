#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成全部输出文件（适配 42 天 / 6 周新结构）。
数据源：curriculum.json（由 restructure.py 生成）
输出：tutorials/*.md, notebooks/*.ipynb, README.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
DAYS = json.load(open(os.path.join(ROOT, "curriculum.json"), encoding="utf-8"))
GITHUB_REPO = "Siebelyk/fde-daily-plan"

TYPE_ICONS = {"视频": "🎬", "文章": "📄", "文档": "📚", "论文": "📝",
              "课程": "🎓", "工具": "🛠", "框架": "🧩", "书籍": "📖",
              "平台": "☁️", "报告": "📊", "指南": "🗺️"}

PHASE_COLORS = {
    "FDE 工程基础与 LLM 原理": "🔵",
    "RAG 构建与交付": "🟢",
    "Agent 开发与 MCP 集成": "🟣",
    "部署交付与生产化": "🟠",
    "AI 安全攻防（差异化能力）": "🔴",
    "客户落地实战与面试": "🟡",
}

WEEK_SUMMARY = {
    1: "从 FDE 岗位认知到 LLM 原理，掌握 API/Prompt/Context 工程，构建第一个可演示应用",
    2: "从分块到向量库到重排评测，构建可交付级 RAG 知识库（含安全检查点）",
    3: "从 ReAct Agent 到 LangChain 到 MCP，开发并编排多 Agent 业务工作流",
    4: "从 vLLM 部署到 K8s 到监控优化，交付生产级 LLM 服务",
    5: "Prompt Injection/RAG投毒/Agent注入/红队，构建安全 LLM 网关（差异化能力）",
    6: "从交付方法论到行业方案到客户沟通，完成面试冲刺",
}

def _type_label(t): return f"{TYPE_ICONS.get(t,'📌')} {t}"
def _phase_color(p): return PHASE_COLORS.get(p, "⚪")

def _split_tutorial_cells(tutorial_text):
    cells = []
    parts = re.split(r"```(\w*)\n", tutorial_text)
    i = 0
    if parts and parts[0]:
        cells.append(("markdown", parts[0]))
    while i + 2 < len(parts):
        lang, code = parts[i+1], parts[i+2]
        code_end = code.rfind("```")
        if code_end != -1:
            cells.append(("code", code[:code_end]))
            trailing = code[code_end+3:]
            if trailing.strip():
                cells.append(("markdown", trailing))
        else:
            cells.append(("code", code))
        i += 2
    if i < len(parts) and parts[i].strip():
        cells.append(("markdown", parts[i]))
    return cells

def generate_tutorial_md(idx, entry):
    day = entry["day"]; demo = entry["demo"]
    md = f"# Day {day}：{entry['title']}\n\n"
    md += f"> {_phase_color(entry['phase'])} {entry['phase']} · 第 {entry['week']} 周\n\n"
    nb_url = f"https://colab.research.google.com/github/{GITHUB_REPO}/blob/main/notebooks/Day-{day:02d}.ipynb"
    md += f'[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({nb_url})\n\n'
    md += f"[💻 在线运行 Notebook]({nb_url}) — 无需本地环境，浏览器直接跑\n\n---\n\n"
    md += "## 学习目标\n\n"
    for i, obj in enumerate(entry["objectives"], 1): md += f"{i}. {obj}\n"
    md += "\n## 推荐资料\n\n"
    for r in entry["resources"]:
        md += f"- {_type_label(r['type'])} [{r['title']}]({r['url']})\n"
    md += f"\n## Demo 练习：{demo['title']}\n\n{demo['description']}\n\n"
    md += f"| 难度 | 预计时间 |\n|------|----------|\n| {demo['difficulty']} | {demo['time']} |\n"
    md += "\n### 复现步骤\n\n"
    for i, step in enumerate(demo["steps"], 1): md += f"{i}. {step}\n"
    tutorial = demo["tutorial"].replace("{security_note}", demo["security_note"])
    md += f"\n## 保姆教程\n\n{tutorial}\n"
    md += "\n## 进阶挑战\n\n"
    for i, ch in enumerate(demo["challenges"], 1): md += f"{i}. {ch}\n"
    if idx + 1 < len(DAYS):
        nxt = DAYS[idx + 1]
        md += f"\n---\n\n## 明日预告\n\n**Day {nxt['day']}：{nxt['title']}**\n"
        md += f"> {_phase_color(nxt['phase'])} {nxt['phase']} · 第 {nxt['week']} 周\n"
    else:
        md += "\n---\n\n> 🎉 恭喜完成全部 42 天 FDE 交付课程！接下来整理项目集、准备面试话术。\n"
    return md

def generate_notebook(idx, entry):
    day = entry["day"]; demo = entry["demo"]
    tutorial = demo["tutorial"].replace("{security_note}", demo["security_note"])
    nb = {"nbformat":4,"nbformat_minor":5,
          "metadata":{"colab":{"provenance":[]},
                      "kernelspec":{"name":"python3","display_name":"Python 3"},
                      "language_info":{"name":"python"}},"cells":[]}
    def add_md(t): nb["cells"].append({"cell_type":"markdown","metadata":{},"source":t.splitlines(True)})
    def add_code(c): nb["cells"].append({"cell_type":"code","metadata":{},"source":c.splitlines(True),"outputs":[],"execution_count":None})
    add_md(f"# Day {day}：{entry['title']}\n\n{_phase_color(entry['phase'])} {entry['phase']} · 第 {entry['week']} 周\n\n"
          f"[在 GitHub 查看教程](https://github.com/{GITHUB_REPO}/blob/main/tutorials/Day-{day:02d}.md)")
    o="## 学习目标\n\n"
    for i,obj in enumerate(entry["objectives"],1): o+=f"{i}. {obj}\n"
    add_md(o)
    r="## 推荐资料\n\n"
    for x in entry["resources"]: r+=f"- {_type_label(x['type'])} [{x['title']}]({x['url']})\n"
    add_md(r)
    add_md(f"## Demo：{demo['title']}\n\n{demo['description']}\n\n难度：{demo['difficulty']} | 预计：{demo['time']}")
    for ct, src in _split_tutorial_cells(tutorial):
        add_code(src) if ct=="code" else add_md(src)
    c="## 进阶挑战\n\n"
    for i,ch in enumerate(demo["challenges"],1): c+=f"{i}. {ch}\n"
    add_md(c)
    if idx+1<len(DAYS):
        n=DAYS[idx+1]
        add_md(f"---\n\n## 明日预告\n\n**Day {n['day']}：{n['title']}**\n{_phase_color(n['phase'])} {n['phase']} · 第 {n['week']} 周")
    return nb

def generate_readme():
    L=[]
    L.append("# 我的FDE学习计划\n")
    L.append("> 面向 AI FDE (Forward Deployed Engineer) 方向的 **42 天交付主线**实战课程。")
    L.append("> FDE 交付为主线（5 周）+ AI 安全为差异化能力（1 周）。")
    L.append("> 每天 = 理论 + 可复现交付 Demo + 保姆教程 + 安全意识 + 进阶挑战。\n")
    L.append("![Python](https://img.shields.io/badge/Python-3.8+-blue)")
    L.append("![Days](https://img.shields.io/badge/Days-42-success)")
    L.append("![Focus](https://img.shields.io/badge/Focus-FDE%20Delivery-blue)")
    L.append("![License](https://img.shields.io/badge/License-MIT-green)\n")
    L.append("## 什么是 FDE？\n")
    L.append("FDE (Forward Deployed Engineer) 是 AI 行业最热门的工程岗位之一：")
    L.append("**把 AI 能力落地交付到客户现场**——既懂模型应用、又懂工程部署、还能对接客户业务。")
    L.append("本课程以 FDE 交付为主线，通过 42 天高强度实战，建立从构建到部署到客户落地的完整能力体系。\n")
    L.append("## 课程特色\n")
    L.append("- **交付主线**：5 周 FDE 交付工程（RAG 构建/Agent 开发/部署/客户落地），1 周 AI 安全差异化")
    L.append("- **JD 对标**：基于 6 个真实 FDE 岗位 JD 设计，覆盖 RAG/Agent/MCP/LangChain/部署/沟通高频要求")
    L.append("- **可演示**：每天 Demo 都是可复现、可演示给客户的交付物，而非纯理论")
    L.append("- **安全意识**：交付全程嵌入安全检查点，第 5 周系统攻防\n")
    L.append("## 课程路线图\n")
    for w in range(1,7):
        wdays=[e for e in DAYS if e["week"]==w]
        L.append(f"\n### 第 {w} 周：{PHASE_COLORS.get(wdays[0]['phase'],'⚪')} {wdays[0]['phase']}")
        L.append(f"_{WEEK_SUMMARY[w]}_\n")
        L.append("| Day | 主题 | Demo | 难度 |")
        L.append("|-----|------|------|------|")
        for e in wdays:
            d=e["day"]
            L.append(f"| [Day {d}](tutorials/Day-{d:02d}.md) | {e['title']} | {e['demo']['title']} | {e['demo']['difficulty']} |")
    L.append("\n## 快速开始\n")
    L.append("```bash")
    L.append("git clone https://github.com/Siebelyk/fde-daily-plan.git")
    L.append("cd fde-daily-plan")
    L.append("cat tutorials/Day-01.md   # 查看任意一天教程")
    L.append("```\n")
    L.append("## 每日推送\n")
    L.append("配置 `config.json` 后运行 `install.sh` 安装定时任务，每天自动推送学习计划到企业微信。\n")
    return "\n".join(L)

def main():
    with open(os.path.join(ROOT,"curriculum.json"),"w",encoding="utf-8") as f:
        json.dump(DAYS,f,ensure_ascii=False,indent=2)
    print(f"[OK] curriculum.json ({len(DAYS)} days)")
    td=os.path.join(ROOT,"tutorials"); os.makedirs(td,exist_ok=True)
    for idx,e in enumerate(DAYS):
        open(os.path.join(td,f"Day-{e['day']:02d}.md"),"w",encoding="utf-8").write(generate_tutorial_md(idx,e))
    print(f"[OK] tutorials/ ({len(DAYS)} files)")
    nd=os.path.join(ROOT,"notebooks"); os.makedirs(nd,exist_ok=True)
    for idx,e in enumerate(DAYS):
        open(os.path.join(nd,f"Day-{e['day']:02d}.ipynb"),"w",encoding="utf-8").write(json.dumps(generate_notebook(idx,e),ensure_ascii=False,indent=1))
    print(f"[OK] notebooks/ ({len(DAYS)} files)")
    open(os.path.join(ROOT,"README.md"),"w",encoding="utf-8").write(generate_readme())
    print(f"[OK] README.md")
    print(f"\n=== 完成：{len(DAYS)} 天 / 6 周 ===")
    sync_runtime()


def sync_runtime():
    """同步核心文件到推送运行时 ~/.fde-daily-plan（规避 TCC 对 ~/Documents 的限制）。"""
    import shutil
    runtime = os.path.expanduser("~/.fde-daily-plan")
    if not os.path.isdir(runtime):
        print("[SKIP] 运行时目录不存在（未运行 install.sh），跳过同步")
        return
    for f in ("daily-plan.py", "config.json", "curriculum.json"):
        shutil.copy2(os.path.join(ROOT, f), os.path.join(runtime, f))
    print(f"[OK] 已同步运行时 -> {runtime}")

if __name__=="__main__":
    main()
