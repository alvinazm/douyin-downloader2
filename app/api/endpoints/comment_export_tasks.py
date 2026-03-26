# 评论导出任务管理器
import asyncio
import os
import csv
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import BackgroundTasks
from crawlers.douyin.web.web_crawler import DouyinWebCrawler
from crawlers.tiktok.web.web_crawler import TikTokWebCrawler


class CommentExportTask:
    """评论导出任务"""

    def __init__(
        self,
        task_id: str,
        platform: str,
        aweme_id: str,
        max_comments: int,
        file_path: str,
    ):
        self.task_id = task_id
        self.platform = platform
        self.aweme_id = aweme_id
        self.max_comments = max_comments
        self.file_path = file_path
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.total_fetched = 0
        self.error_message: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.classification_status: Optional[str] = (
            None  # none, running, completed, failed
        )
        self.classification_progress: int = 0
        self.classification_summary: Optional[Dict[str, int]] = None
        self.classified_file_path: Optional[str] = None


class TaskManager:
    """任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, CommentExportTask] = {}
        self.douyin_crawler = DouyinWebCrawler()
        self.tiktok_crawler = TikTokWebCrawler()

    def create_task(
        self, platform: str, aweme_id: str, max_comments: int, filename: str
    ) -> CommentExportTask:
        """创建新任务"""
        import uuid

        task_id = str(uuid.uuid4())

        # 确保下载目录存在
        download_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "download",
            "comment",
        )
        os.makedirs(download_path, exist_ok=True)

        file_path = os.path.join(download_path, f"{filename}.csv")

        task = CommentExportTask(task_id, platform, aweme_id, max_comments, file_path)
        self.tasks[task_id] = task

        return task

    def get_task(self, task_id: str) -> Optional[CommentExportTask]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> list[CommentExportTask]:
        """获取所有任务"""
        return list(self.tasks.values())

    def delete_task(self, task_id: str, delete_file: bool = False):
        """删除任务"""
        task = self.tasks.get(task_id)
        if task:
            # 删除文件
            if delete_file and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                except:
                    pass
            # 删除任务
            del self.tasks[task_id]

    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: int | None = None,
        total_fetched: int | None = None,
        error_message: str | None = None,
    ):
        """更新任务状态"""
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.now()
            if progress is not None:
                task.progress = progress
            if total_fetched is not None:
                task.total_fetched = total_fetched
            if error_message is not None:
                task.error_message = error_message
            if status == "completed":
                task.completed_at = datetime.now()

    def update_classification_status(
        self,
        task_id: str,
        classification_status: str,
        classification_progress: int | None = None,
        classification_summary: Dict[str, int] | None = None,
        classified_file_path: str | None = None,
        error_message: str | None = None,
    ):
        """更新分类状态"""
        task = self.tasks.get(task_id)
        if task:
            task.classification_status = classification_status
            task.updated_at = datetime.now()
            if classification_progress is not None:
                task.classification_progress = classification_progress
            if classification_summary is not None:
                task.classification_summary = classification_summary
            if classified_file_path is not None:
                task.classified_file_path = classified_file_path
            if error_message is not None:
                task.error_message = error_message

    async def execute_task(self, task_id: str):
        """执行任务"""
        task = self.get_task(task_id)
        if not task:
            return

        self.update_task_status(task_id, "running", progress=0)

        try:
            if task.platform == "douyin":
                await self._execute_douyin_task(task)
            elif task.platform == "tiktok":
                await self._execute_tiktok_task(task)
            else:
                raise ValueError(f"Unsupported platform: {task.platform}")

            self.update_task_status(
                task_id, "completed", progress=100, total_fetched=task.total_fetched
            )
        except Exception as e:
            self.update_task_status(task_id, "failed", error_message=str(e))

    async def _execute_douyin_task(self, task: CommentExportTask):
        """执行抖音导出任务"""
        cursor = 0
        count = 20
        total_count = 0

        # 创建CSV文件并写入表头
        with open(task.file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # 流式获取和写入评论
            while True:
                response = await self.douyin_crawler.fetch_video_comments(
                    aweme_id=task.aweme_id, cursor=cursor, count=count
                )

                if not response or "comments" not in response:
                    break

                comments = response.get("comments", [])
                if not comments:
                    break

                # 写入这一批评论
                for comment in comments:
                    if total_count >= task.max_comments:
                        break

                    parsed_data = self._parse_comment_data(comment)
                    if parsed_data:
                        writer.writerow(parsed_data)
                        total_count += 1

                        # 更新进度
                        task.total_fetched = total_count
                        progress = int((total_count / task.max_comments) * 100)
                        self.update_task_status(
                            task.task_id, "running", progress=progress
                        )

                # 如果达到最大评论数，停止获取
                if total_count >= task.max_comments:
                    break

                # 更新游标
                cursor = response.get("cursor", 0)
                if response.get("has_more", False) == False:
                    break

                # 添加延迟，避免请求过快
                await asyncio.sleep(0.3)

    async def _execute_tiktok_task(self, task: CommentExportTask):
        """执行TikTok导出任务"""
        cursor = 0
        count = 20
        total_count = 0

        # 创建CSV文件并写入表头
        with open(task.file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # 流式获取和写入评论
            while True:
                try:
                    response = await self.tiktok_crawler.fetch_post_comment(
                        aweme_id=task.aweme_id,
                        cursor=cursor,
                        count=count,
                        current_region="US",
                    )

                    if not response or "comments" not in response:
                        break

                    comments = response.get("comments", [])
                    if not comments:
                        break

                    # 写入这一批评论
                    for comment in comments:
                        if total_count >= task.max_comments:
                            break

                        parsed_data = self._parse_comment_data(comment)
                        if parsed_data:
                            writer.writerow(parsed_data)
                            total_count += 1

                            # 更新进度
                            task.total_fetched = total_count
                            progress = int((total_count / task.max_comments) * 100)
                            self.update_task_status(
                                task.task_id, "running", progress=progress
                            )

                    # 如果达到最大评论数，停止获取
                    if total_count >= task.max_comments:
                        break

                    # 更新游标
                    cursor = response.get("cursor", 0)
                    if response.get("has_more", False) == False:
                        break

                    # 添加延迟，避免请求过快
                    await asyncio.sleep(0.3)

                except Exception as e:
                    raise Exception(f"无法获取TikTok评论。错误: {str(e)}")

    def _parse_comment_data(self, comment):
        """解析单条评论数据"""
        try:
            user_info = comment.get("user", {})
            text = comment.get("text", "")
            digg_count = comment.get("digg_count", 0)
            create_time = comment.get("create_time", 0)

            if create_time:
                time_str = datetime.fromtimestamp(create_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            else:
                time_str = ""

            nickname = user_info.get("nickname", "Unknown User")

            return {
                "评论人": nickname,
                "评论内容": text,
                "点赞量": digg_count,
                "评论时间": time_str,
            }
        except Exception as e:
            print(f"Error parsing comment: {e}")
            return None


# 全局任务管理器实例
task_manager = TaskManager()
