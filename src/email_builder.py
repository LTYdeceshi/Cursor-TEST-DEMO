"""Build a styled HTML email from fetched news items."""

from datetime import datetime, timedelta, timezone

from jinja2 import Template

from .news_fetcher import FetchResult

EMAIL_TEMPLATE = Template(
    """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{{ subject }}</title>
<style>
  body { margin:0; padding:0; background:#f4f5f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; color:#1a1a1a; }
  .container { max-width:680px; margin:0 auto; background:#ffffff; }
  .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:32px 24px; text-align:center; }
  .header h1 { margin:0; color:#fff; font-size:24px; font-weight:600; }
  .header p { margin:8px 0 0; color:rgba(255,255,255,0.85); font-size:14px; }
  .section { padding:24px; }
  .section-title { font-size:18px; font-weight:600; color:#333; margin:0 0 16px; padding-bottom:8px; border-bottom:2px solid #667eea; display:inline-block; }
  .news-list { list-style:none; margin:0; padding:0; }
  .news-item { padding:12px 0; border-bottom:1px solid #eee; }
  .news-item:last-child { border-bottom:none; }
  .news-title a { color:#1a1a1a; text-decoration:none; font-weight:500; font-size:15px; line-height:1.5; }
  .news-title a:hover { color:#667eea; }
  .news-meta { margin-top:4px; font-size:12px; color:#888; }
  .news-meta .source { background:#f0f0f0; padding:2px 8px; border-radius:3px; margin-right:8px; }
  .news-meta .hot { color:#ff4757; font-weight:500; }
  .news-summary { margin-top:6px; font-size:13px; color:#666; line-height:1.6; }
  .divider { height:1px; background:#eee; margin:0; }
  .footer { padding:20px 24px; text-align:center; font-size:12px; color:#aaa; background:#fafafa; }
  .empty-msg { color:#999; font-style:italic; padding:16px 0; }
  .badge-intl { background:#e3f2fd; color:#1565c0; padding:2px 8px; border-radius:3px; font-size:12px; margin-right:6px; }
  .badge-cn { background:#fce4ec; color:#c62828; padding:2px 8px; border-radius:3px; font-size:12px; margin-right:6px; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📰 每日热点速递</h1>
    <p>{{ date_str }} | 国际 &amp; 国内热点一览</p>
  </div>

  <!-- 国际热点 -->
  <div class="section">
    <div class="section-title">🌍 国际热点</div>
    {% if international %}
    <ul class="news-list">
      {% for item in international %}
      <li class="news-item">
        <div class="news-title">
          <span class="badge-intl">{{ item.source }}</span>
          <a href="{{ item.url }}" target="_blank">{{ item.title }}</a>
        </div>
        {% if item.summary %}
        <div class="news-summary">{{ item.summary }}</div>
        {% endif %}
        <div class="news-meta">
          {% if item.published %}<span>🕐 {{ item.published }}</span>{% endif %}
        </div>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <p class="empty-msg">暂无国际热点信息</p>
    {% endif %}
  </div>

  <div class="divider"></div>

  <!-- 国内热点 -->
  <div class="section">
    <div class="section-title">🇨🇳 国内热点</div>
    {% if domestic %}
    <ul class="news-list">
      {% for item in domestic %}
      <li class="news-item">
        <div class="news-title">
          <span class="badge-cn">{{ item.source }}</span>
          <a href="{{ item.url }}" target="_blank">{{ item.title }}</a>
        </div>
        {% if item.summary %}
        <div class="news-summary">{{ item.summary }}</div>
        {% endif %}
        <div class="news-meta">
          {% if item.hot_score %}<span class="hot">🔥 {{ item.hot_score }}</span>{% endif %}
          {% if item.published %}<span>🕐 {{ item.published }}</span>{% endif %}
        </div>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <p class="empty-msg">暂无国内热点信息</p>
    {% endif %}
  </div>

  <div class="footer">
    此邮件由 <strong>Daily Hot News</strong> 自动生成并发送<br/>
    数据来源: BBC · Google News · 百度热搜 · 微博热搜 · 今日头条
  </div>
</div>
</body>
</html>"""
)


def build_subject(target_date: datetime | None = None) -> str:
    if target_date is None:
        target_date = datetime.now(timezone(timedelta(hours=8))) - timedelta(days=1)
    return f"📰 每日热点速递 — {target_date.strftime('%Y年%m月%d日')}"


def build_html(news: FetchResult, target_date: datetime | None = None) -> str:
    if target_date is None:
        target_date = datetime.now(timezone(timedelta(hours=8))) - timedelta(days=1)

    date_str = target_date.strftime("%Y年%m月%d日 %A")

    international = [
        {
            "title": n.title,
            "url": n.url,
            "source": n.source,
            "summary": n.summary,
            "published": n.published,
        }
        for n in news.international
    ]
    domestic = [
        {
            "title": n.title,
            "url": n.url,
            "source": n.source,
            "summary": n.summary,
            "published": n.published,
            "hot_score": n.hot_score,
        }
        for n in news.domestic
    ]

    return EMAIL_TEMPLATE.render(
        subject=build_subject(target_date),
        date_str=date_str,
        international=international,
        domestic=domestic,
    )
