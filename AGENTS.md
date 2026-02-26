# AGENTS.md

## Cursor Cloud specific instructions

This is a Python application that fetches daily hot news (international + Chinese domestic) and sends a formatted HTML email. See `README.md` for full usage and SMTP configuration reference.

### Quick reference

- **Run (dry-run):** `python3 -m src.main --dry-run`
- **Run (send email):** `python3 -m src.main` (requires SMTP env vars)
- **HTML preview:** `python3 -m src.main --dry-run -o preview.html`
- **Lint:** `make lint`
- **Install deps:** `pip3 install -r requirements.txt`

### Non-obvious notes

- Use `python3` not `python` — this environment doesn't have a `python` symlink.
- International news is auto-translated to Chinese via Google Translate (`deep-translator`). Translation of ~30 items takes ~10-20 seconds.
- The Weibo hot search API (`weibo.com/ajax/side/hotSearch`) returns 403 from non-Chinese IPs. This is expected; the app gracefully falls back to other Chinese sources (百度热搜, 今日头条, Google News 中国).
- Email sending requires env vars (see `.env.example`). `SMTP_USERNAME` can be a display name (e.g. "每日新闻"), the code auto-detects and uses `SENDER_EMAIL` for SMTP login.
- The `--dry-run` flag skips all SMTP validation, useful for testing news fetching independently.
- Cron is configured for daily 07:00 Beijing time (UTC 23:00). Use `crontab -l` to verify, `crontab -e` to edit.
