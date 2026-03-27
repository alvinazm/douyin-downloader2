import os
import logging
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import LOG_PATH

router = APIRouter()


class ParserLogEntry(BaseModel):
    platform: str
    url: str
    comment_count: int
    result: str
    detail: str = ""


class FetchCommentsLogEntry(BaseModel):
    platform: str
    aweme_id: str
    url: str
    max_comments: int
    result: str
    detail: str = ""


def get_logger(log_name: str):
    log_file = os.path.join(
        LOG_PATH, f"{log_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
    )
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(f"{log_name}_{datetime.now().strftime('%Y-%m-%d')}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_comment_export(platform: str, aweme_id: str, stage: str, **kwargs):
    """
    记录评论导出各阶段日志
    stage: submit | fetching | completed | failed
    """
    logger = get_logger("fetch_comments")

    base_msg = f"[{platform.upper()}] 视频ID: {aweme_id}"

    if stage == "submit":
        msg = (
            f"{base_msg} | "
            f"操作: 用户提交导出CSV | "
            f"请求数量: {kwargs.get('max_comments', 0)}"
        )
    elif stage == "fetching":
        msg = (
            f"{base_msg} | 操作: 获取评论 | 已获取: {kwargs.get('fetched_count', 0)}条"
        )
    elif stage == "completed":
        msg = (
            f"{base_msg} | "
            f"操作: 生成CSV文件 | "
            f"文件: {kwargs.get('file_path', '')} | "
            f"总评论数: {kwargs.get('total_count', 0)}"
        )
    elif stage == "failed":
        msg = f"{base_msg} | 操作: 导出失败 | 错误: {kwargs.get('error', '')}"
    else:
        msg = f"{base_msg} | {kwargs}"

    logger.info(msg)


def log_comment_classify(platform: str, aweme_id: str, stage: str, **kwargs):
    """
    记录AI评论分类各阶段日志
    stage: submit | progress | completed | failed
    """
    logger = get_logger("classification")

    base_msg = f"[{platform.upper()}] 视频ID: {aweme_id}"

    if stage == "submit":
        msg = (
            f"{base_msg} | "
            f"操作: 用户提交AI分类 | "
            f"评论总数: {kwargs.get('total_comments', 0)} | "
            f"批次大小: {kwargs.get('batch_size', 20)} | "
            f"并发数: {kwargs.get('workers', 5)}"
        )
    elif stage == "progress":
        msg = (
            f"{base_msg} | "
            f"操作: AI分类中 | "
            f"进度: {kwargs.get('progress', 0)}% | "
            f"已完成批次: {kwargs.get('completed_batches', 0)}/{kwargs.get('total_batches', 0)}"
        )
    elif stage == "completed":
        msg = (
            f"{base_msg} | "
            f"操作: 生成已分类CSV | "
            f"文件: {kwargs.get('file_path', '')} | "
            f"分类统计: {kwargs.get('summary', {})}"
        )
    elif stage == "failed":
        msg = f"{base_msg} | 操作: 分类失败 | 错误: {kwargs.get('error', '')}"
    else:
        msg = f"{base_msg} | {kwargs}"

    logger.info(msg)


@router.post("/parser")
async def log_parser_activity(entry: ParserLogEntry):
    """
    记录评论解析活动日志
    """
    logger = get_logger("parser_comments")

    log_message = (
        f"[{entry.platform.upper()}] "
        f"URL: {entry.url} | "
        f"评论数: {entry.comment_count} | "
        f"结果: {entry.result}"
    )

    if entry.detail:
        log_message += f" | 详情: {entry.detail}"

    logger.info(log_message)

    return {"code": 200, "message": "日志记录成功"}


@router.post("/fetch_comments")
async def log_fetch_comments(entry: FetchCommentsLogEntry):
    """
    记录导出CSV活动日志
    """
    logger = get_logger("fetch_comments")

    log_message = (
        f"[{entry.platform.upper()}] "
        f"视频ID: {entry.aweme_id} | "
        f"URL: {entry.url} | "
        f"请求数量: {entry.max_comments} | "
        f"结果: {entry.result}"
    )

    if entry.detail:
        log_message += f" | 详情: {entry.detail}"

    logger.info(log_message)

    return {"code": 200, "message": "日志记录成功"}
