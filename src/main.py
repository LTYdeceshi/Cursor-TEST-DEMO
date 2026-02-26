"""Entry point: fetch hot news → build email → send (or dry-run)."""

import argparse
import logging
import sys
from pathlib import Path

from .email_builder import build_html, build_subject
from .email_sender import send_email
from .news_fetcher import fetch_all_news

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="每日热点新闻邮件推送",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  python -m src.main --dry-run          # 仅抓取并预览，不发送邮件
  python -m src.main --dry-run -o out.html  # 保存 HTML 到文件
  python -m src.main                    # 抓取并发送邮件 (需配置环境变量)
""",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅抓取新闻并生成 HTML，不发送邮件",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="dry-run 模式下将 HTML 保存到指定文件",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("开始抓取热点新闻 ...")
    news = fetch_all_news()

    intl_count = len(news.international)
    dom_count = len(news.domestic)
    logger.info("抓取完成: 国际 %d 条, 国内 %d 条", intl_count, dom_count)

    if intl_count == 0 and dom_count == 0:
        logger.warning("未获取到任何新闻，请检查网络连接")
        sys.exit(1)

    subject = build_subject()
    html = build_html(news)

    if args.dry_run:
        if args.output:
            out_path = Path(args.output)
            out_path.write_text(html, encoding="utf-8")
            logger.info("HTML 已保存到 %s", out_path)
        else:
            print("\n" + "=" * 60)
            print(f"Subject: {subject}")
            print("=" * 60)
            print(f"国际热点: {intl_count} 条")
            for i, item in enumerate(news.international, 1):
                print(f"  {i}. [{item.source}] {item.title}")
            print(f"\n国内热点: {dom_count} 条")
            for i, item in enumerate(news.domestic, 1):
                score = f" 🔥{item.hot_score}" if item.hot_score else ""
                print(f"  {i}. [{item.source}] {item.title}{score}")
            print("=" * 60)
        logger.info("Dry-run 完成，未发送邮件")
    else:
        logger.info("正在发送邮件 ...")
        send_email(subject, html)
        logger.info("邮件发送成功! ✉️")


if __name__ == "__main__":
    main()
