#!/usr/bin/env python3
# FDE 每日学习计划生成器 — 根据日期计算进度并推送 macOS 通知 + 企业微信
import json, os, sys, subprocess, urllib.request
from datetime import datetime, date

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---- 读取配置与课程 ----
with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as f:
    config = json.load(f)
with open(os.path.join(ROOT, "curriculum.json"), encoding="utf-8") as f:
    curriculum = json.load(f)

# ---- 计算天数 ----
today = date.today()
start = date.fromisoformat(config["start_date"])
days_elapsed = (today - start).days
day_index = days_elapsed + 1  # Day 1 = start_date

weekday_cn = "一二三四五六日"[today.weekday()]
date_str = today.strftime("%Y-%m-%d")

# ---- 生成 Markdown ----
def generate_plan(day, entry):
    objectives = entry["objectives"] if isinstance(entry["objectives"], list) else [entry["objectives"]]
    md = f"# FDE 每日学习计划 — Day {day}\n\n"
    md += f"> {date_str} 周{weekday_cn} | {entry['phase']} | 第 {entry['week']} 周\n\n---\n\n"
    md += f"## 今日主题\n\n**{entry['title']}**\n\n"
    md += "## 学习目标\n\n"
    for i, obj in enumerate(objectives, 1):
        md += f"{i}. {obj}\n"
    md += "\n## 推荐资料\n\n"
    for r in entry["resources"]:
        md += f"- [{r['type']}] [{r['title']}]({r['url']})\n"
    demo = entry["demo"]
    md += f"\n## 今日 Demo 练习\n\n**{demo['title']}**\n\n{demo['description']}\n\n"
    md += f"- 难度：{demo['difficulty']}\n- 预计时间：{demo['time']}\n"
    if "steps" in demo:
        md += "\n### 复现步骤\n\n"
        for s in demo["steps"]:
            md += f"- {s}\n"
    if "tutorial" in demo:
        md += f"\n### 保姆教程\n\n{demo['tutorial']}\n"
    md += "\n---\n\n## 学习记录\n\n"
    md += "- [ ] 完成阅读推荐资料\n- [ ] 完成 Demo 练习\n- [ ] 记录学习笔记\n- [ ] 遇到的问题与解决思路：\n"
    return md

# ---- 生成企业微信 markdown（企业微信不支持 --- / - [ ] / 代码块） ----
def generate_wechat_md(day, entry):
    objectives = entry["objectives"] if isinstance(entry["objectives"], list) else [entry["objectives"]]
    lines = []
    lines.append(f"# FDE 每日学习计划 — Day {day}")
    lines.append(f"> **{date_str} 周{weekday_cn}** | {entry['phase']} | 第 {entry['week']} 周")
    lines.append("")
    lines.append(f"### 今日主题：**{entry['title']}**")
    lines.append("")
    lines.append("**学习目标**")
    for i, obj in enumerate(objectives, 1):
        lines.append(f"{i}. {obj}")
    lines.append("")
    lines.append("**推荐资料**")
    for r in entry["resources"]:
        lines.append(f"- [{r['type']}] [{r['title']}]({r['url']})")
    demo = entry["demo"]
    lines.append("")
    lines.append(f"### Demo 练习：{demo['title']}")
    lines.append(f"> {demo['description']}")
    lines.append(f"难度：{demo['difficulty']} | 预计：{demo['time']}")
    if "steps" in demo:
        lines.append("")
        lines.append("**复现步骤**")
        for s in demo["steps"]:
            lines.append(f"- {s}")
    if "tutorial" in demo:
        github_repo = config.get("github_repo", "")
        if github_repo:
            tut_link = f"{github_repo}/blob/main/tutorials/Day-{day:02d}.md"
            lines.append("")
            lines.append(f"**保姆教程**：[点击查看完整教程]({tut_link})")
        else:
            tutorial = demo["tutorial"]
            if len(tutorial) > 800:
                tutorial = tutorial[:800] + "\n...(完整教程见本地文件)"
            lines.append("")
            lines.append("**保姆教程**")
            lines.append(tutorial)
    return "\n".join(lines)

# ---- 主逻辑 ----
output_dir = os.path.join(ROOT, "今日计划")
os.makedirs(output_dir, exist_ok=True)

if day_index < 1:
    plan_text = f"# FDE 学习计划尚未开始\n\n开始日期：{config['start_date']}\n\n今天是 {date_str}，距离开始还有 {1 - day_index} 天。"
    notify_title, notify_body = "FDE 学习计划", f"距离开始还有 {1 - day_index} 天，做好准备！"
    wechat_md = f"# FDE 学习计划尚未开始\n\n开始日期：{config['start_date']}\n今天是 {date_str}，距离开始还有 {1 - day_index} 天，做好准备！"
elif day_index > config["total_days"]:
    plan_text = f"# FDE 学习计划已完成！\n\n你在 {config['start_date']} 开始，已坚持 {config['total_days']} 天。\n\n恭喜完成全部课程！"
    notify_title, notify_body = "FDE 学习计划", f"全部 {config['total_days']} 天课程已完成，恭喜！"
    wechat_md = f"# FDE 学习计划已完成！\n\n坚持了 {config['total_days']} 天，恭喜完成全部课程！"
else:
    entry = curriculum[day_index - 1]
    plan_text = generate_plan(day_index, entry)
    wechat_md = generate_wechat_md(day_index, entry)
    notify_title = f"FDE Day {day_index} | {entry['title']}"
    notify_body = f"{entry['phase']} - 今日 Demo: {entry['demo']['title']} ({entry['demo']['time']})"

# ---- 写入文件 ----
filename = f"Day-{day_index:02d}-{date_str}.md"
filepath = os.path.join(output_dir, filename)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(plan_text)

# ---- 打印到终端 ----
print(plan_text)
print(f"\n已保存到: {filepath}\n")

# ---- 发送 macOS 通知 ----
def send_notification(title, body):
    safe_title = title.replace('"', '\\"')
    safe_body = body.replace('"', '\\"')
    script = f'display notification "{safe_body}" with title "{safe_title}" sound name "Glass"'
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True)
    except Exception:
        pass

send_notification(notify_title, notify_body)

# ---- 发送企业微信推送 ----
def send_wechat(md_content):
    webhook = config.get("wechat_webhook", "")
    if not webhook:
        return "skipped (no webhook configured)"
    payload = json.dumps({"msgtype": "markdown", "markdown": {"content": md_content}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("errcode") == 0:
                return "ok"
            return f"error: {result.get('errmsg', result)}"
    except Exception as e:
        return f"failed: {e}"

wechat_status = send_wechat(wechat_md)
print(f"企业微信推送: {wechat_status}")

# ---- 打开文件（仅 --open 时） ----
if "--open" in sys.argv:
    try:
        subprocess.run(["open", filepath], capture_output=True)
    except Exception:
        pass
