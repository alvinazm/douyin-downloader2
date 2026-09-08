"""
YouTube TokenManager

为 yt-dlp 提供 Cookie/UA/代理。Cookie 由 chrome-cookie-sniffer 通过
POST /api/hybrid/update_cookie 推送（service=youtube）写入 config，
下载时由 download_video 读取并以 --add-header 方式传给 yt-dlp。
"""
import os
import yaml

from crawlers.utils.utils import load_yaml_or_default
from crawlers.utils.logger import logger as _crawler_logger_yt

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))
# 本地配置缺失时回退到空配置。
config = load_yaml_or_default(
    os.path.join(path, "config.yaml"), default={}, logger=_crawler_logger_yt
)


class TokenManager:
    youtube_manager = config.get("TokenManager", {}).get("youtube", {})

    @classmethod
    def get_cookie_string(cls) -> str:
        """返回 YouTube Cookie 字符串，动态从 config 读取"""
        try:
            return cls.youtube_manager.get("headers", {}).get("Cookie", "") or ""
        except Exception:
            return ""

    @classmethod
    def get_headers(cls) -> dict:
        """返回完整 headers（UA + Referer + Cookie），用于 yt-dlp"""
        headers = cls.youtube_manager.get("headers", {}) or {}
        return {k: v for k, v in headers.items() if v}

    @classmethod
    def update_cookie_string(cls, cookie: str) -> None:
        """更新 utils 模块 config 中的 cookie，使后续 get_cookie_string() 立即读到新值"""
        global config
        if "TokenManager" not in config or not isinstance(
            config.get("TokenManager"), dict
        ):
            config["TokenManager"] = {}
        if (
            "youtube" not in config["TokenManager"]
            or not isinstance(config["TokenManager"].get("youtube"), dict)
        ):
            config["TokenManager"]["youtube"] = {}
        yt_conf = config["TokenManager"]["youtube"]
        if "headers" not in yt_conf or not isinstance(yt_conf.get("headers"), dict):
            yt_conf["headers"] = {}
        yt_conf["headers"]["Cookie"] = cookie
        # 刷新类引用，避免持有旧子字典引用
        cls.youtube_manager = yt_conf
