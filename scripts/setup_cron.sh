#!/usr/bin/env bash
# ============================================
# 设置每日热点新闻定时推送 (北京时间 07:00)
# 使用方法: bash scripts/setup_cron.sh
# 前提: 已配置好 SMTP 环境变量 (见 .env.example)
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 检查必要环境变量
REQUIRED_VARS=(SMTP_HOST SMTP_PORT SMTP_PASSWORD SENDER_EMAIL RECIPIENT_EMAIL)
MISSING=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        MISSING+=("$var")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "[ERROR] 缺少环境变量: ${MISSING[*]}"
    echo "请先配置 .env 文件或 export 环境变量，参考 .env.example"
    exit 1
fi

# 构建 crontab 内容
CRON_CONTENT="# 每日热点新闻推送 (自动生成，勿手动编辑此块)
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.local/bin
PYTHONPATH=$HOME/.local/lib/python3.12/site-packages
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_USERNAME=${SMTP_USERNAME:-}
SMTP_PASSWORD=${SMTP_PASSWORD}
SENDER_EMAIL=${SENDER_EMAIL}
SENDER_NAME=${SENDER_NAME:-}
RECIPIENT_EMAIL=${RECIPIENT_EMAIL}
SMTP_USE_SSL=${SMTP_USE_SSL:-true}

# 北京时间 07:00 = UTC 23:00
0 23 * * * cd ${SCRIPT_DIR} && /usr/bin/python3 -m src.main >> /var/log/daily-news.log 2>&1
"

echo "$CRON_CONTENT" | crontab -

echo "✅ 定时任务已配置:"
echo "   时间: 每天北京时间 07:00 (UTC 23:00)"
echo "   收件人: ${RECIPIENT_EMAIL}"
echo "   日志: /var/log/daily-news.log"
echo ""
echo "验证: crontab -l"
