"""
Instagram 博主最新视频抓取（按 timestamp 倒序）

实现思路参考 /Users/azm/MyProject/ins-dl/docs/ins-fetch-latest.md：
1. Playwright + 系统 Chrome（已登录）打开 /<username>/reels/ Tab 抓 shortcode 列表
2. yt-dlp --cookies-from-browser chrome --dump-single-json 取每条 reel 的 timestamp
3. 按 timestamp 倒序排序，取最近 N 条

依赖：
- playwright（pip install playwright）—— 不需要 playwright install chromium（用系统 Chrome）
- yt-dlp ≥ 2024.x
- 系统已装 Google Chrome
- Chrome 至少登录过一次 Instagram
"""
import asyncio
import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

import yt_dlp

from crawlers.utils.logger import logger


# 北京时区，用于格式化输出
BJ_TZ = timezone(timedelta(hours=8))

# 短代码（reel id）格式：Instagram shortcode 是 11 字符的字母数字
_SHORTCODE_RE = re.compile(r"^[A-Za-z0-9_-]{6,20}$")


def _parse_username_from_url(url: str) -> Optional[str]:
    """
    从 URL 提取 username。
    支持：
      - https://www.instagram.com/<user>/reels/
      - https://www.instagram.com/<user>/reel/
      - https://www.instagram.com/<user>/
    """
    if not url:
        return None
    m = re.search(r"instagram\.com/([A-Za-z0-9._]+)(?:/reels?/?|/|$)", url)
    if m:
        return m.group(1)
    return None


def _get_shortcodes_via_playwright(username: str, limit: int) -> List[str]:
    """
    用 Playwright + 系统 Chrome 抓博主 /reels/ Tab 下的 shortcode 列表。

    重要：用 channel="chrome" 让 Playwright 用系统已登录的 Chrome，
    绕过 Instagram 的 challenge 墙。参考 ins-fetch-latest.md 文档步骤 1。

    网络容错：国内/弱网环境访问 IG 经常 ERR_TIMED_OUT。加重试 3 次，
    失败则返回空列表（上层用 warning 提示用户）。
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        try:
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="en-US",
            )
            page = ctx.new_page()

            url = f"https://www.instagram.com/{username}/reels/"

            for attempt in range(1, 4):
                try:
                    logger.info(
                        f"[InstagramCreatorLatest] 抓取 /reels/ 列表 "
                        f"(尝试 {attempt}/3, username={username})"
                    )
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_selector("a[href*=\'/reel/\']", timeout=30000)

                    hrefs = page.evaluate(
                        f"""() => {{
                            const arr = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                            const codes = arr
                                .map(a => (a.href.split(\'/reel/\')[1] || \'\').split(\'/\')[0])
                                .filter(v => v && /^[A-Za-z0-9_-]{{6,20}}$/.test(v));
                            return Array.from(new Set(codes)).slice(0, {limit});
                        }}"""
                    )
                    if hrefs:
                        return list(hrefs)
                    logger.warning(
                        f"[InstagramCreatorLatest] 抓到空 shortcode 列表，"
                        f"重试中... (尝试 {attempt}/3)"
                    )
                except (PWTimeout, Exception) as e:
                    logger.warning(
                        f"[InstagramCreatorLatest] 抓取失败 (尝试 {attempt}/3): "
                        f"{type(e).__name__}: {e}; username={username}"
                    )

                if attempt < 3:
                    import time
                    wait_sec = 2 if attempt == 1 else 5
                    logger.info(
                        f"[InstagramCreatorLatest] 等待 {wait_sec}s 后重试..."
                    )
                    time.sleep(wait_sec)

            logger.error(
                f"[InstagramCreatorLatest] 重试 3 次仍失败: username={username}"
            )
            return []
        finally:
            browser.close()


def _fetch_reel_meta(shortcode: str) -> Optional[Dict[str, Any]]:
    """
    用 yt-dlp 取单条 reel 的元数据。
    --cookies-from-browser chrome 用 Chrome 登录态绕过 challenge，
    --skip-download 不下载，只取元数据。
    """
    url = f"https://www.instagram.com/reel/{shortcode}/"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "cookiesfrombrowser": ("chrome",),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            return None
        return {
            "shortcode": shortcode,
            "url": url,
            "title": info.get("title"),
            "description": info.get("description"),
            "uploader": info.get("uploader") or info.get("uploader_id"),
            "uploader_id": info.get("uploader_id"),
            "timestamp": info.get("timestamp"),  # Unix 秒
            "upload_date": info.get("upload_date"),  # YYYYMMDD
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "comment_count": info.get("comment_count"),
            "thumbnail": info.get("thumbnail"),
        }
    except Exception as e:
        logger.warning(
            f"[InstagramCreatorLatest] yt-dlp 取元数据失败: shortcode={shortcode}, err={e}"
        )
        return None


def _format_publish_time(ts: Optional[int]) -> Optional[str]:
    """Unix 秒 -> 'YYYY-MM-DD HH:MM:SS' (UTC+8)"""
    if not ts:
        return None
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc).astimezone(BJ_TZ)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def get_creator_latest_reels(url: str, n: int = 2, list_limit: int = 20) -> Dict[str, Any]:
    """
    同步版本：获取博主最近 N 条视频，按 timestamp 倒序。

    Args:
        url: 作者 reels 链接，如 https://www.instagram.com/<user>/reels/
        n: 返回多少条（默认 2）
        list_limit: 列表抓取上限（默认 20），用于排序

    Returns:
        dict: { username, items: [...], warning?: str }
    """
    username = _parse_username_from_url(url)
    if not username:
        raise ValueError(f"无法从 URL 提取 username: {url!r}")

    n = max(1, min(int(n or 2), 20))
    list_limit = max(n, min(int(list_limit or 20), 50))

    logger.info(
        f"[InstagramCreatorLatest] 抓取 @{username} 最近 {n} 条 (list_limit={list_limit})"
    )

    # 步骤 1: Playwright 抓 shortcode 列表
    shortcodes = _get_shortcodes_via_playwright(username, list_limit)
    if not shortcodes:
        return {
            "username": username,
            "items": [],
            "warning": (
                "未能在 /reels/ Tab 抓到任何 shortcode。"
                "可能原因：1) 博主不存在 / 私密账号；"
                "2) Chrome 未登录 Instagram；3) Instagram 触发 challenge 墙。"
                "详见 /Users/azm/MyProject/ins-dl/docs/ins-fetch-latest.md 故障排查。"
            ),
        }

    logger.info(
        f"[InstagramCreatorLatest] @{username} 抓到 {len(shortcodes)} 个 shortcode"
    )

    # 步骤 2: yt-dlp 取每条 reel 的元数据
    items: List[Dict[str, Any]] = []
    for sc in shortcodes:
        meta = _fetch_reel_meta(sc)
        if meta and meta.get("timestamp"):
            meta["formatted_publish_time"] = _format_publish_time(meta.get("timestamp"))
            items.append(meta)

    # 步骤 3: 按 timestamp 倒序排序，取最近 N 条
    items.sort(key=lambda x: x.get("timestamp") or 0, reverse=True)
    items = items[:n]

    return {
        "username": username,
        "items": items,
        "warning": None if items else "yt-dlp 全部失败，请查看 server.log。",
    }


async def get_creator_latest_reels_async(
    url: str, n: int = 2, list_limit: int = 20
) -> Dict[str, Any]:
    """异步包装（Playwright + yt-dlp 都是阻塞调用，放到线程池执行）。"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: get_creator_latest_reels(url, n=n, list_limit=list_limit)
    )
