"""Translate international news items to Chinese using Google Translate."""

import logging
import time

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

TRANSLATOR = GoogleTranslator(source="en", target="zh-CN")
DELAY_BETWEEN_ITEMS = 0.15  # seconds, avoid rate-limiting


def _translate(text: str) -> str:
    """Translate a single string; return original on failure."""
    if not text:
        return text
    try:
        return TRANSLATOR.translate(text)
    except Exception as exc:
        logger.warning("翻译失败 [%s...]: %s", text[:30], exc)
        return text


def translate_news_items(items: list) -> list:
    """Translate title and summary of each NewsItem to Chinese (in-place)."""
    total = len(items)
    if total == 0:
        return items

    logger.info("开始翻译 %d 条国际新闻 ...", total)

    for idx, item in enumerate(items, 1):
        item.title = _translate(item.title)
        if item.summary:
            item.summary = _translate(item.summary)
        if idx < total:
            time.sleep(DELAY_BETWEEN_ITEMS)

    logger.info("翻译完成")
    return items
