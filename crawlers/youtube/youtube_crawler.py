import os
import re
import subprocess
import sys
import json
import tempfile
import asyncio
from typing import Optional, Dict, Any, List

import yt_dlp

# 让 YouTube 下载也能用 chrome-cookie-sniffer 推送的 Cookie
from crawlers.youtube.web.utils import TokenManager


class YouTubeCrawler:
    def __init__(self):
        self.platform = "youtube"

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})",
            r"^([a-zA-Z0-9_-]{11})$",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def fetch_video_info(self, url: str) -> Dict[str, Any]:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Cannot extract YouTube video ID from URL: {url}")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "socket_timeout": 30,
        }

        loop = asyncio.get_event_loop()

        def _sync_extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, _sync_extract)

        return {
            "video_id": video_id,
            "title": info.get("title"),
            "description": info.get("description"),
            "uploader": info.get("uploader"),
            "upload_date": info.get("upload_date"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "thumbnail": info.get("thumbnail"),
            "url": url,
            "platform": self.platform,
            "full_info": info,
        }

    async def get_download_url(
        self, url: str, with_watermark: bool = False
    ) -> Dict[str, Any]:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Cannot extract YouTube video ID from URL: {url}")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "best[ext=mp4]/best",
            "socket_timeout": 30,
        }

        loop = asyncio.get_event_loop()

        def _sync_extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])
                best_video = None
                best_audio = None

                for f in formats:
                    if f.get("ext") == "mp4":
                        if f.get("vcodec") != "none" and f.get("acodec") != "none":
                            best_video = f
                            break
                        elif f.get("vcodec") != "none" and best_video is None:
                            best_video = f
                        elif f.get("acodec") != "none" and best_audio is None:
                            best_audio = f

                result = {
                    "video_id": video_id,
                    "title": info.get("title"),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader"),
                    "platform": self.platform,
                }

                if best_video:
                    result["video_url"] = best_video.get("url")
                    result["nwm_video_url_HQ"] = best_video.get("url")

                if best_audio and not best_video.get("acodec"):
                    result["audio_url"] = best_audio.get("url")

                return result

        return await loop.run_in_executor(None, _sync_extract)

    @staticmethod
    def _cleanup_ytdl_temp_files(output_path: str, video_id: str = None) -> int:
        """清理 yt-dlp 下载过程中可能残留的临时文件

        yt-dlp 下载长视频走 DASH/HLS 分片时，会先把每个分片存为
        ``<title> [<id>].f616.mp4.part-FragXXX.part``，然后合并成完整 mp4。
        下载完成/失败时，残留的 .part 文件不会被自动清理，会变成"孤儿"留在
        output_path 里。常见临时文件后缀：
            - ``.part`` / ``.part-Frag*.part``  分片下载中间产物
            - ``.ytdl``                           旧版 yt-dlp 元数据
            - ``.temp``                           ffmpeg 合并过程中的临时文件

        Args:
            output_path: 下载目录
            video_id: 可选，若指定则只清理该 video 的临时文件，避免误删其他任务残留

        Returns:
            int: 清理掉的文件数量
        """
        cleaned = 0
        if not os.path.isdir(output_path):
            return 0

        # 临时文件清理策略：
        # - 指定 video_id：只清理该 video 的临时文件（避免误删其他并发任务）
        # - 不指定 video_id：兜底清理所有 .part 残留（用于"完成后全清"场景）
        # yt-dlp outtmpl 是 "%(title)s [%(id)s].%(ext)s"，
        # 生成的文件名形如 "标题 [video_id].f616.mp4.part-Frag0.part"，
        # 所以判别"是否属于某 video"的可靠标记就是文件名里含 "[video_id]"。
        # 注意：不要用 glob/fnmatch 的 "[]" —— 它们会当成字符类。
        # 用纯字符串包含判断最安全。
        needle = f"[{video_id}]" if video_id else None

        temp_suffixes = (".part", ".ytdl", ".temp")

        for fname in os.listdir(output_path):
            if not fname.endswith(temp_suffixes):
                continue
            if needle is not None and needle not in fname:
                continue
            fp = os.path.join(output_path, fname)
            if not os.path.isfile(fp):
                continue
            try:
                os.remove(fp)
                cleaned += 1
            except OSError:
                # 文件正在被占用/权限不足/已不存在 —— 静默忽略
                pass
        return cleaned

    @staticmethod
    def _build_ydl_headers_from_cookie(cookie_string: str) -> List[str]:
        """把 "k1=v1; k2=v2" 形式的 Cookie 拆成 ["k1: v1", "k2: v2"]，给 yt-dlp --add-header 用"""
        headers = []
        if not cookie_string:
            return headers
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                name, value = item.split("=", 1)
                # 过滤空值和占位
                if name and value and value not in ("test_value", ""):
                    headers.append(f"{name.strip()}: {value.strip()}")
        return headers

    async def download_video(
        self,
        url: str,
        output_path: str,
        filename: str = None,
        progress_callback: callable = None,
    ) -> str:
        os.makedirs(output_path, exist_ok=True)

        # 先用 url 提取 video_id，用于精确清理本次下载的临时文件
        video_id_for_cleanup = None
        try:
            video_id_for_cleanup = self.extract_video_id(url)
        except Exception:
            pass

        # 下载前清理：去掉上次中断下载留下的孤儿分片（避免和新下载的文件混在一起）
        # 只清理本次 video 的残留，避免误删其他并发下载任务
        pre_cleaned = self._cleanup_ytdl_temp_files(
            output_path, video_id_for_cleanup
        )
        if pre_cleaned:
            print(
                f"YouTubeCrawler: 预清理 {pre_cleaned} 个 yt-dlp 临时文件 (video_id={video_id_for_cleanup})"
            )

        # 从 TokenManager 读取 Cookie / UA / Referer
        cookie_string = TokenManager.get_cookie_string()
        headers = TokenManager.get_headers()
        ua = headers.get("User-Agent") or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        )
        referer = headers.get("Referer") or "https://www.youtube.com/"

        # yt-dlp 的 add_headers：把 cookie 拆成 Header 列表，避免 Cookie 头被截断
        add_headers = [f"User-Agent: {ua}", f"Referer: {referer}"]
        add_headers.extend(self._build_ydl_headers_from_cookie(cookie_string))

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": os.path.join(output_path, "%(title)s [%(id)s].%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 60,
            "overwrites": True,
            # 通过 add_headers 把每个 cookie 当成独立 header 注入，
            # 比 "cookiefile" 或 "cookiesfrombrowser" 更稳，且不依赖本地浏览器
            "add_headers": add_headers,
            # 网络不稳定（YouTube 降速 / SSL 断连）时的容错：
            # - retries: HTTP 整体重试次数（默认 10，提升到 15）
            # - fragment_retries: 单个分片下载失败时的重试次数（默认 10）
            # - file_access_retries: 文件操作重试（写入 .part 等）
            # - skip_unavailable_fragments: 跳过无法下载的分片（避免某个分片卡死导致整个失败）
            #   配合 retries 使用：可重试就先重试，重试失败才跳过
            "retries": 15,
            "fragment_retries": 15,
            "file_access_retries": 5,
            "skip_unavailable_fragments": True,
            # 并发分片下载（默认 1 串行；并发 4 让网络带宽跑满，YouTube 不限并发）
            "concurrent_fragment_downloads": 4,
            # 限制单个分片重试间隔，避免被 YouTube 风控
            "retry_sleep_functions": {
                "http": lambda n: min(2 ** n, 30),  # 指数退避，封顶 30s
                "fragment": lambda n: min(2 ** n, 30),
                "file_access": lambda n: 1,
            },
        }

        # 如果 config 配置了代理，也透传给 yt-dlp
        try:
            proxy_cfg = TokenManager.youtube_manager.get("proxies", {}) or {}
            proxy_url = proxy_cfg.get("http") or proxy_cfg.get("https")
            if proxy_url:
                ydl_opts["proxy"] = proxy_url
        except Exception:
            pass

        loop = asyncio.get_event_loop()
        downloaded_path = [None]
        download_error = [None]

        def _sync_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        ext = "mp4"
                        title = info.get("title", "video")
                        video_id = info.get("id", "unknown")
                        downloaded_path[0] = os.path.join(
                            output_path, f"{title} [{video_id}].{ext}"
                        )
                except Exception as e:
                    download_error[0] = e
                    raise

        try:
            await loop.run_in_executor(None, _sync_download)
        finally:
            # 下载后无论如何都清理本次下载残留的临时文件
            # 即使 yt-dlp 抛异常中断，也要清掉孤儿分片
            post_cleaned = self._cleanup_ytdl_temp_files(
                output_path, video_id_for_cleanup
            )
            if post_cleaned:
                print(
                    f"YouTubeCrawler: 后清理 {post_cleaned} 个 yt-dlp 临时文件 (video_id={video_id_for_cleanup})"
                )

        video_id = url.split("v=")[1].split("&")[0] if "v=" in url else None

        if filename and video_id:
            import glob as glob_module  # noqa: F401  保留以便未来调试

            pattern = os.path.join(output_path, f"*{video_id}*.mp4")
            matches = glob_module.glob(pattern)
            if matches:
                downloaded_path[0] = matches[0]
                print(f"DEBUG: found downloaded file: {downloaded_path[0]}")

        print(
            f"DEBUG: downloaded_path={downloaded_path[0]}, exists={os.path.exists(downloaded_path[0]) if downloaded_path[0] else False}"
        )

        if downloaded_path[0] and os.path.exists(downloaded_path[0]):
            if filename:
                final_path = os.path.join(output_path, filename)
                print(f"DEBUG: renaming {downloaded_path[0]} to {final_path}")
                import shutil

                shutil.copy2(downloaded_path[0], final_path)
                os.remove(downloaded_path[0])
                return final_path
            return downloaded_path[0]
        else:
            raise Exception(f"Failed to download video from {url}")


async def main():
    crawler = YouTubeCrawler()

    url = "https://www.youtube.com/watch?v=ABDIq-CVU9Y"

    print("Testing YouTube info extraction...")
    info = await crawler.fetch_video_info(url)
    print(f"Title: {info.get('title')}")
    print(f"Video ID: {info.get('video_id')}")
    print(f"Uploader: {info.get('uploader')}")

    print("\nTesting download URL extraction...")
    download_info = await crawler.get_download_url(url)
    print(f"Video URL: {download_info.get('video_url')}")


if __name__ == "__main__":
    asyncio.run(main())
