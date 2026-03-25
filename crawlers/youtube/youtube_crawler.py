import os
import re
import subprocess
import sys
import json
import tempfile
import asyncio
from typing import Optional, Dict, Any

import yt_dlp


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

    async def download_video(
        self,
        url: str,
        output_path: str,
        filename: str = None,
        progress_callback: callable = None,
    ) -> str:
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": os.path.join(output_path, "%(title)s [%(id)s].%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 60,
            "overwrites": True,
        }

        loop = asyncio.get_event_loop()
        downloaded_path = [None]

        def _sync_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    ext = "mp4"
                    title = info.get("title", "video")
                    video_id = info.get("id", "unknown")
                    downloaded_path[0] = os.path.join(
                        output_path, f"{title} [{video_id}].{ext}"
                    )

        await loop.run_in_executor(None, _sync_download)

        video_id = url.split("v=")[1].split("&")[0] if "v=" in url else None

        if filename and video_id:
            import glob as glob_module

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
