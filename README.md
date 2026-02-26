# 📰 Daily Hot News — 每日热点新闻邮件推送

每天早上自动抓取前一天的热点新闻（国际 + 中国国内），生成精美 HTML 邮件并推送到指定邮箱。

## 新闻来源

| 类别 | 来源 |
|------|------|
| 🌍 国际 | BBC World News · Google News · Al Jazeera |
| 🇨🇳 国内 | 百度热搜 · 微博热搜 · 今日头条 · Google News (中国) |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填写实际的 SMTP 配置：

```bash
cp .env.example .env
# 编辑 .env 填入邮箱配置
```

需要配置的环境变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `SMTP_HOST` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `SMTP_USE_SSL` | 是否使用 SSL | `true` |
| `SMTP_USERNAME` | SMTP 登录用户名 | `you@gmail.com` |
| `SMTP_PASSWORD` | SMTP 密码/应用专用密码 | `xxxx-xxxx-xxxx` |
| `SENDER_EMAIL` | 发件人邮箱 | `you@gmail.com` |
| `RECIPIENT_EMAIL` | 收件人邮箱（多个用逗号分隔） | `a@x.com,b@x.com` |

### 3. 运行

```bash
# 抓取新闻 + 发送邮件
python -m src.main

# 仅预览（不发邮件）
python -m src.main --dry-run

# 保存 HTML 到文件预览
python -m src.main --dry-run -o preview.html
```

或使用 Make：

```bash
make dry-run   # 终端预览
make preview   # 保存 HTML
make run       # 发送邮件
```

### 4. 定时任务（每天早上 7:00 自动推送）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天北京时间早上 7:00 执行，UTC 23:00）
0 23 * * * cd /path/to/project && python -m src.main >> /var/log/daily-news.log 2>&1
```

## 项目结构

```
├── src/
│   ├── main.py          # 入口：CLI 参数、流程编排
│   ├── config.py         # 从环境变量加载配置
│   ├── news_fetcher.py   # 多源新闻抓取（RSS + API）
│   ├── email_builder.py  # HTML 邮件模板渲染
│   └── email_sender.py   # SMTP 邮件发送
├── .env.example          # 环境变量示例
├── requirements.txt      # Python 依赖
├── Makefile             # 常用命令
└── README.md
```

## 常见 SMTP 配置

| 邮箱服务 | SMTP_HOST | SMTP_PORT | SMTP_USE_SSL |
|---------|-----------|-----------|-------------|
| Gmail | `smtp.gmail.com` | `465` | `true` |
| QQ 邮箱 | `smtp.qq.com` | `465` | `true` |
| 163 邮箱 | `smtp.163.com` | `465` | `true` |
| Outlook | `smtp.office365.com` | `587` | `false` |
| 阿里企业邮 | `smtp.qiye.aliyun.com` | `465` | `true` |

> **Gmail 用户**: 需开启 [应用专用密码](https://myaccount.google.com/apppasswords)，不能直接使用 Gmail 密码。
