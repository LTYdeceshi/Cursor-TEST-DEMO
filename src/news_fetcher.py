"""Fetch hot news from multiple international and Chinese domestic sources."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

REQUEST_TIMEOUT = 15


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    summary: str = ""
    published: str = ""
    hot_score: str = ""
    category: str = ""  # 'international' | 'domestic'


@dataclass
class FetchResult:
    international: list[NewsItem] = field(default_factory=list)
    domestic: list[NewsItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# RSS feed definitions
# ---------------------------------------------------------------------------

RSS_INTERNATIONAL = [
    {
        "name": "BBC World News",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
    },
    {
        "name": "Google News (World)",
        "url": (
            "https://news.google.com/rss/topics/"
            "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB"
            "?hl=en-US&gl=US&ceid=US:en"
        ),
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
    },
]

RSS_CHINA = [
    {
        "name": "Google News (中国)",
        "url": (
            "https://news.google.com/rss/search"
            "?q=%E4%B8%AD%E5%9B%BD+%E7%83%AD%E7%82%B9"
            "&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        ),
    },
]


# ---------------------------------------------------------------------------
# RSS fetcher
# ---------------------------------------------------------------------------


def _fetch_rss(name: str, url: str, max_items: int = 10) -> list[NewsItem]:
    """Parse an RSS feed and return NewsItem list."""
    items: list[NewsItem] = []
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            raise ValueError(f"RSS parse error: {feed.bozo_exception}")

        cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

        for entry in feed.entries:
            if len(items) >= max_items:
                break

            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue
                published = pub_dt.strftime("%Y-%m-%d %H:%M")

            summary = ""
            if hasattr(entry, "summary") and entry.summary:
                soup = BeautifulSoup(entry.summary, "html.parser")
                summary = soup.get_text(strip=True)[:200]

            items.append(
                NewsItem(
                    title=entry.get("title", "").strip(),
                    url=entry.get("link", ""),
                    source=name,
                    summary=summary,
                    published=published,
                )
            )
    except Exception as exc:
        logger.warning("RSS fetch failed [%s]: %s", name, exc)

    return items


# ---------------------------------------------------------------------------
# Baidu Hot Search (百度热搜)
# ---------------------------------------------------------------------------

BAIDU_HOT_API = "https://top.baidu.com/api/board?platform=wise&tab=realtime"


def _fetch_baidu_hot(max_items: int = 20) -> list[NewsItem]:
    items: list[NewsItem] = []
    try:
        resp = requests.get(BAIDU_HOT_API, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for card in data.get("data", {}).get("cards", []):
            for entry in card.get("content", []):
                if len(items) >= max_items:
                    return items

                word = entry.get("word", "") or entry.get("query", "")
                if not word:
                    continue

                desc = entry.get("desc", "")
                url = entry.get("url") or entry.get("rawUrl", "")
                if not url:
                    url = f"https://www.baidu.com/s?wd={word}"

                hot_score = entry.get("hotScore", "")

                items.append(
                    NewsItem(
                        title=word,
                        url=url,
                        source="百度热搜",
                        summary=desc if isinstance(desc, str) else "",
                        hot_score=str(hot_score) if hot_score else "",
                        category="domestic",
                    )
                )
    except Exception as exc:
        logger.warning("Baidu Hot fetch failed: %s", exc)

    return items


# ---------------------------------------------------------------------------
# Weibo Hot Search (微博热搜)
# ---------------------------------------------------------------------------

WEIBO_HOT_URL = "https://weibo.com/ajax/side/hotSearch"


def _fetch_weibo_hot(max_items: int = 20) -> list[NewsItem]:
    items: list[NewsItem] = []
    try:
        resp = requests.get(WEIBO_HOT_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        realtime = data.get("data", {}).get("realtime", [])
        for entry in realtime:
            if len(items) >= max_items:
                break

            word = entry.get("word", "")
            if not word:
                continue

            note = entry.get("note", word)
            num = entry.get("num", "")
            url = f"https://s.weibo.com/weibo?q=%23{word}%23"

            items.append(
                NewsItem(
                    title=note,
                    url=url,
                    source="微博热搜",
                    summary="",
                    hot_score=str(num) if num else "",
                    category="domestic",
                )
            )
    except Exception as exc:
        logger.warning("Weibo Hot fetch failed: %s", exc)

    return items


# ---------------------------------------------------------------------------
# Toutiao Hot (头条热榜)
# ---------------------------------------------------------------------------

TOUTIAO_HOT_URL = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"


def _fetch_toutiao_hot(max_items: int = 20) -> list[NewsItem]:
    items: list[NewsItem] = []
    try:
        resp = requests.get(TOUTIAO_HOT_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for entry in data.get("data", []):
            if len(items) >= max_items:
                break

            title = entry.get("Title", "")
            if not title:
                continue

            url = entry.get("Url", "")
            hot_value = entry.get("HotValue", "")

            items.append(
                NewsItem(
                    title=title,
                    url=url,
                    source="今日头条",
                    summary="",
                    hot_score=str(hot_value) if hot_value else "",
                    category="domestic",
                )
            )
    except Exception as exc:
        logger.warning("Toutiao Hot fetch failed: %s", exc)

    return items


# ---------------------------------------------------------------------------
# Public API: fetch everything
# ---------------------------------------------------------------------------


def _deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    seen: set[str] = set()
    result: list[NewsItem] = []
    for item in items:
        key = item.title.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def fetch_all_news() -> FetchResult:
    """Fetch news from all sources. Returns categorized, deduplicated results."""
    result = FetchResult()

    # --- International ---
    for src in RSS_INTERNATIONAL:
        fetched = _fetch_rss(src["name"], src["url"], max_items=10)
        for item in fetched:
            item.category = "international"
        result.international.extend(fetched)

    # --- Chinese domestic: RSS ---
    for src in RSS_CHINA:
        fetched = _fetch_rss(src["name"], src["url"], max_items=10)
        for item in fetched:
            item.category = "domestic"
        result.domestic.extend(fetched)

    # --- Chinese domestic: Hot search APIs ---
    result.domestic.extend(_fetch_baidu_hot())
    result.domestic.extend(_fetch_weibo_hot())
    result.domestic.extend(_fetch_toutiao_hot())

    # Deduplicate
    result.international = _deduplicate(result.international)
    result.domestic = _deduplicate(result.domestic)

    logger.info(
        "Fetched %d international, %d domestic items",
        len(result.international),
        len(result.domestic),
    )
    return result
