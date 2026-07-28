#!/bin/bash
# 安装 我的FDE学习计划定时任务到 macOS launchd
# 关键设计：推送运行时放在 ~/.fde-daily-plan（非 TCC 保护区），
#           规避 launchd 无法访问 ~/Documents 的限制；
#           项目内 今日计划/ 用符号链接指向运行时，保持可见性。
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.fde.daily-plan"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
RUNTIME="$HOME/.fde-daily-plan"
PYTHON_BIN="$(which python3)"
UID_NUM="$(id -u)"

# 从 config.json 读取推送时间
PUSH_HOUR=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('push_time','08:30').split(':')[0])" 2>/dev/null || echo "08")
PUSH_MIN=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('push_time','08:30').split(':')[1])" 2>/dev/null || echo "30")

echo "============================================"
echo "  我的FDE学习计划 - 定时任务安装"
echo "============================================"
echo "  项目目录:   $SCRIPT_DIR"
echo "  运行时目录: $RUNTIME (非 TCC 保护区，规避 ~/Documents 限制)"
echo "  Python:     $PYTHON_BIN"
echo "  推送时间:   每天 ${PUSH_HOUR}:${PUSH_MIN}"
echo ""

# ---- 1. 搭建运行时目录并同步核心文件 ----
mkdir -p "$RUNTIME/logs" "$RUNTIME/今日计划"
for f in daily-plan.py config.json curriculum.json; do
  cp "$SCRIPT_DIR/$f" "$RUNTIME/$f"
done
echo "  [OK] 已同步运行时文件"

# ---- 2. 迁移 今日计划 并建立符号链接 ----
if [ -L "$SCRIPT_DIR/今日计划" ]; then
  echo "  [OK] 今日计划 已是符号链接"
elif [ -d "$SCRIPT_DIR/今日计划" ]; then
  # 把现有计划文件搬到运行时，再替换为符号链接
  cp "$SCRIPT_DIR/今日计划/"*.md "$RUNTIME/今日计划/" 2>/dev/null || true
  rm -rf "$SCRIPT_DIR/今日计划"
  ln -s "$RUNTIME/今日计划" "$SCRIPT_DIR/今日计划"
  echo "  [OK] 今日计划 已迁移并链接到运行时"
else
  ln -s "$RUNTIME/今日计划" "$SCRIPT_DIR/今日计划"
  echo "  [OK] 已创建 今日计划 符号链接"
fi

# ---- 3. 卸载旧任务（兼容 load 与 bootstrap 两种历史加载方式）----
launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
launchctl unload "$PLIST" 2>/dev/null || true
echo "  [OK] 已清理旧任务"

# ---- 4. 生成 plist（指向运行时，日志也在运行时）----
cat > "$PLIST" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON_BIN}</string>
    <string>${RUNTIME}/daily-plan.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${PUSH_HOUR}</integer>
    <key>Minute</key>
    <integer>${PUSH_MIN}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${RUNTIME}/logs/stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${RUNTIME}/logs/stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
</dict>
</plist>
PLIST_EOF
echo "  [OK] 已生成 plist"

# ---- 5. 加载定时任务（现代 bootstrap 命令）----
launchctl bootstrap "gui/$UID_NUM" "$PLIST"
echo "  [OK] 定时任务已加载"

# ---- 6. 立即触发一次测试 ----
echo ""
echo "  立即触发测试运行..."
launchctl kickstart -k "gui/$UID_NUM/$LABEL" 2>&1 || true
sleep 2

# ---- 7. 检查结果 ----
echo ""
echo "  === 运行时日志(stdout 末尾) ==="
tail -5 "$RUNTIME/logs/stdout.log" 2>/dev/null || echo "  (无输出)"
echo "  === 运行时日志(stderr 末尾) ==="
tail -5 "$RUNTIME/logs/stderr.log" 2>/dev/null || echo "  (无错误)"
echo "  === 今日计划 ==="
ls -1 "$RUNTIME/今日计划/" 2>/dev/null | tail -5 || echo "  (空)"

echo ""
echo "  定时任务已安装！每天约 ${PUSH_HOUR}:${PUSH_MIN} 自动推送。"
echo "  常用命令:"
echo "    手动触发:   launchctl kickstart -k gui/$UID_NUM/$LABEL"
echo "    查看状态:   launchctl list | grep fde"
echo "    卸载:       launchctl bootout gui/$UID_NUM/$LABEL"
echo "    重新同步:   修改课程后运行 build_all.py（会自动同步运行时）"
echo "============================================"
