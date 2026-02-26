# 📰 Daily Hot News — 每日热点新闻邮件推送

每天早上自动抓取前 24 小时的热点新闻（国内 + 国际），国际新闻自动翻译为中文，生成精美 HTML 邮件并推送到指定邮箱。

## 特性

- 🇨🇳 **国内热点优先** — 国内新闻排在邮件最前面
- 🌍 **国际新闻中文化** — 自动翻译为中文，无阅读障碍
- ⏰ **每日定时推送** — 北京时间每天早上 7:00 自动发送
- 📊 **热度排序** — 百度热搜、今日头条按热度值排序

## 新闻来源

| 类别 | 来源 |
|------|------|
| 🇨🇳 国内 | 百度热搜 · 微博热搜 · 今日头条 · Google News (中国) |
| 🌍 国际 | BBC World News · Google News · Al Jazeera（自动翻译为中文） |

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

**方式一：一键配置（推荐）**

```bash
bash scripts/setup_cron.sh
```

**方式二：手动配置 crontab**

```bash
crontab -e

# 添加以下行（北京时间 07:00 = UTC 23:00）
0 23 * * * cd /path/to/project && /usr/bin/python3 -m src.main >> /var/log/daily-news.log 2>&1
```

**验证定时任务：**

```bash
crontab -l              # 查看当前定时任务
tail -f /var/log/daily-news.log  # 查看运行日志
```

## 项目结构

```
├── src/
│   ├── main.py          # 入口：CLI 参数、流程编排
│   ├── config.py         # 从环境变量加载配置
│   ├── news_fetcher.py   # 多源新闻抓取（RSS + API）
│   ├── translator.py     # Google Translate 国际新闻翻译
│   ├── email_builder.py  # HTML 邮件模板渲染
│   └── email_sender.py   # SMTP 邮件发送
├── scripts/
│   └── setup_cron.sh     # 一键配置定时任务
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
