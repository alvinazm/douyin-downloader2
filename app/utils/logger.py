import logging
import sys
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class RequestFormatter(logging.Formatter):
    """带请求ID的日志格式化器"""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey
        + "%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
        + reset,
        logging.INFO: blue
        + "%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
        + reset,
        logging.WARNING: yellow
        + "%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
        + reset,
        logging.ERROR: red
        + "%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
        + reset,
        logging.CRITICAL: bold_red
        + "%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
        + reset,
    }

    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "N/A"
        return logging.Formatter(self.FORMATS.get(record.levelno)).format(record)


class RequestLogger:
    """请求级别日志记录器"""

    def __init__(self, name: str = "DouyinDownloader"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # 设置日志目录
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)

        # 文件处理器 - 每天一个日志文件，保留30天
        log_file = log_dir / f"download_video_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(RequestFormatter())

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 避免日志重复
        self.logger.propagate = False

    def _get_request_id(self) -> str:
        """获取或创建请求ID"""
        return str(uuid.uuid4().hex)[:8]

    def debug(self, message: str, request_id: Optional[str] = None, **kwargs):
        extra = {"request_id": request_id or self._get_request_id()}
        self.logger.debug(message, extra=extra, **kwargs)

    def info(self, message: str, request_id: Optional[str] = None, **kwargs):
        extra = {"request_id": request_id or self._get_request_id()}
        self.logger.info(message, extra=extra, **kwargs)

    def warning(self, message: str, request_id: Optional[str] = None, **kwargs):
        extra = {"request_id": request_id or self._get_request_id()}
        self.logger.warning(message, extra=extra, **kwargs)

    def error(
        self,
        message: str,
        request_id: Optional[str] = None,
        exc_info: bool = False,
        **kwargs,
    ):
        extra = {"request_id": request_id or self._get_request_id()}
        self.logger.error(message, extra=extra, exc_info=exc_info, **kwargs)

    def critical(self, message: str, request_id: Optional[str] = None, **kwargs):
        extra = {"request_id": request_id or self._get_request_id()}
        self.logger.critical(message, extra=extra, **kwargs)


# 全局日志实例
app_logger = RequestLogger("DouyinDownloader")


def get_logger(name: str = None) -> RequestLogger:
    """获取日志记录器"""
    if name:
        return RequestLogger(name)
    return app_logger
