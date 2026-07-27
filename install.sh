#!/bin/bash
# 安装 我的FDE学习计划定时任务到 macOS launchd
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.fde.daily-plan"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
PYTHON_BIN="$(which python3)"

# 从 config.json 读取推送时间
PUSH_HOUR=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('push_time','08:30').split(':')[0])" 2>/dev/null || echo "08")
PUSH_MIN=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('push_time','08:30').split(':')[1])" 2>/dev/null || echo "30")

echo "============================================"
echo "  我的FDE学习计划 - 定时任务安装"
echo "============================================"
echo ""
echo "  脚本路径:  $SCRIPT_DIR/daily-plan.py"
echo "  Python路径: $PYTHON_BIN"
echo "  推送时间:  每天 ${PUSH_HOUR}:${PUSH_MIN}"
echo ""

# 如果已存在先卸载
if launchctl list | grep -q "$LABEL" 2>/dev/null; then
  launchctl unload "$PLIST" 2>/dev/null || true
  echo "  已卸载旧版本"
fi

# 生成 plist
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
    <string>${SCRIPT_DIR}/daily-plan.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${PUSH_HOUR}</integer>
    <key>Minute</key>
    <integer>${PUSH_MIN}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${SCRIPT_DIR}/logs/stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${SCRIPT_DIR}/logs/stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
</dict>
</plist>
PLIST_EOF

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# 加载定时任务
launchctl load "$PLIST"

echo "  定时任务已安装并启动！"
echo ""
echo "  每天约 ${PUSH_HOUR}:${PUSH_MIN} 会自动弹通知，计划文件保存在:"
echo "  $SCRIPT_DIR/今日计划/"
echo ""
echo "  常用命令:"
echo "    手动测试:   python3 $SCRIPT_DIR/daily-plan.py"
echo "    手动测试+打开: python3 $SCRIPT_DIR/daily-plan.py --open"
echo "    查看状态:   launchctl list | grep fde"
echo "    卸载:       launchctl unload $PLIST"
echo "    修改时间:   编辑 config.json 的 push_time 字段后重新运行本脚本"
echo ""
echo "============================================"
