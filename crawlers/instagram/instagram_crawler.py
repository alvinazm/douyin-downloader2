import os
import re
import asyncio
from typing import Optional, Dict, Any, List

import yt_dlp

# 让 Instagram 下载也能用 chrome-cookie-sniffer 推送的 Cookie
from crawlers.instagram.web.utils import TokenManager


class InstagramCrawler:
    def __init__(self):
        self.platform = "instagram"

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r"instagram\.com/reel/([A-Za-z0-9_-]+)",
            r"instagram\.com/p/([A-Za-z0-9_-]+)",
            r"instagram\.com/tv/([A-Za-z0-9_-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _cleanup_ytdl_temp_files(output_path: str, video_id: str = None) -> int:
        """清理 yt-dlp 下载过程中可能残留的临时文件

        与 YouTubeCrawler 的同名方法行为一致：精确按 [video_id] 标记清理，
        避免 glob/fnmatch 把 [...] 当字符类导致误匹配。
        """
        cleaned = 0
        if not os.path.isdir(output_path):
            return 0

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
                if name and value and value not in ("test_value", ""):
                    headers.append(f"{name.strip()}: {value.strip()}")
        return headers

    def _build_common_ydl_opts(self, output_path: str, download: bool) -> Dict[str, Any]:
        """构造通用的 yt-dlp 选项：Cookie / UA / Referer / 重试 / 并发"""
        cookie_string = TokenManager.get_cookie_string()
        headers = TokenManager.get_headers()
        ua = headers.get("User-Agent") or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        )
        referer = headers.get("Referer") or "https://www.instagram.com/"

        add_headers = [f"User-Agent: {ua}", f"Referer: {referer}"]
        add_headers.extend(self._build_ydl_headers_from_cookie(cookie_string))

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "add_headers": add_headers,
            "retries": 15,
            "fragment_retries": 15,
            "file_access_retries": 5,
            "skip_unavailable_fragments": True,
            "concurrent_fragment_downloads": 4,
            "retry_sleep_functions": {
                "http": lambda n: min(2 ** n, 30),
                "fragment": lambda n: min(2 ** n, 30),
                "file_access": lambda n: 1,
            },
        }

        if download:
            ydl_opts.update(
                {
                    # Instagram 没有 mp4 视频流（通常 webm/VP9），原
                    # bestvideo[ext=mp4]+bestaudio[ext=m4a] 强制 mp4 会让 yt-dlp
                    # fallback 到 best[ext=mp4]/best 拿到奇怪格式或合并失败。
                    # 改为 bv*+ba/b：选最佳视频流 + 最佳音频流合并，fallback 到 best 单文件。
                    # 跟命令行 `yt-dlp -f best` 行为一致。
                    "format": "bv*+ba/b",
                    "outtmpl": os.path.join(output_path, "%(title)s [%(id)s].%(ext)s"),
                    "merge_output_format": "mp4",
                    "socket_timeout": 60,
                    "overwrites": True,
                    # 双保险 cookie 源：chrome-cookie-sniffer 推送的 cookie（add_headers）
                    # + 系统 Chrome 已登录的 sessionid（cookiesfrombrowser）
                    # 这样无论哪个 cookie 源有效，都能成功下载。
                    "cookiesfrombrowser": ("chrome",),
                }
            )

        # config 里配置的代理透传给 yt-dlp
        try:
            proxy_cfg = TokenManager.instagram_manager.get("proxies", {}) or {}
            proxy_url = proxy_cfg.get("http") or proxy_cfg.get("https")
            if proxy_url:
                ydl_opts["proxy"] = proxy_url
        except Exception:
            pass

        return ydl_opts

    async def fetch_video_info(self, url: str) -> Dict[str, Any]:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Cannot extract Instagram video ID from URL: {url}")

        ydl_opts = self._build_common_ydl_opts(output_path="", download=False)
        ydl_opts["extract_flat"] = False
        ydl_opts["socket_timeout"] = 30

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
            "uploader_id": info.get("uploader_id"),
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
            raise ValueError(f"Cannot extract Instagram video ID from URL: {url}")

        ydl_opts = self._build_common_ydl_opts(output_path="", download=False)
        ydl_opts["format"] = "best[ext=mp4]/best"
        ydl_opts["socket_timeout"] = 30

        loop = asyncio.get_event_loop()

        def _sync_extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])
                best_video = None

                for f in formats:
                    if f.get("ext") == "mp4" and f.get("url"):
                        if f.get("vcodec") != "none" and f.get("acodec") != "none":
                            best_video = f
                            break
                        elif f.get("vcodec") != "none" and best_video is None:
                            best_video = f

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

                return result

        return await loop.run_in_executor(None, _sync_extract)

    async def download_video(
        self,
        url: str,
        output_path: str,
        filename: str = None,
        progress_callback: callable = None,
    ) -> str:
        os.makedirs(output_path, exist_ok=True)

        video_id_for_cleanup = None
        try:
            video_id_for_cleanup = self.extract_video_id(url)
        except Exception:
            pass

        # 下载前清理本次 video 的孤儿临时文件
        pre_cleaned = self._cleanup_ytdl_temp_files(output_path, video_id_for_cleanup)
        if pre_cleaned:
            print(
                f"InstagramCrawler: 预清理 {pre_cleaned} 个 yt-dlp 临时文件 "
                f"(video_id={video_id_for_cleanup})"
            )

        ydl_opts = self._build_common_ydl_opts(output_path=output_path, download=True)

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
            post_cleaned = self._cleanup_ytdl_temp_files(output_path, video_id_for_cleanup)
            if post_cleaned:
                print(
                    f"InstagramCrawler: 后清理 {post_cleaned} 个 yt-dlp 临时文件 "
                    f"(video_id={video_id_for_cleanup})"
                )

        video_id = self.extract_video_id(url)

        if filename and video_id:
            import glob as glob_module  # noqa: F401  保留以便未来调试

            pattern = os.path.join(output_path, f"*{video_id}*.mp4")
            matches = glob_module.glob(pattern)
            if matches:
                downloaded_path[0] = matches[0]
                print(f"DEBUG: found downloaded file: {downloaded_path[0]}")

        print(
            f"DEBUG: downloaded_path={downloaded_path[0]}, "
            f"exists={os.path.exists(downloaded_path[0]) if downloaded_path[0] else False}"
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
    crawler = InstagramCrawler()

    url = "https://www.instagram.com/reel/DvoyPcWD3t8/"

    print("Testing Instagram info extraction...")
    info = await crawler.fetch_video_info(url)
    print(f"Title: {info.get('title')}")
    print(f"Video ID: {info.get('video_id')}")
    print(f"Uploader: {info.get('uploader')}")

    print("\nTesting download URL extraction...")
    download_info = await crawler.get_download_url(url)
    print(f"Video URL: {download_info.get('video_url')}")


if __name__ == "__main__":
    asyncio.run(main())
