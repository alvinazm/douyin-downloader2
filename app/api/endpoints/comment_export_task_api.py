import os
from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from starlette.responses import FileResponse
from app.api.models.APIResponseModel import ErrorResponseModel
from app.api.endpoints.comment_export_tasks import task_manager
from app.config import MAX_COMMENTS

router = APIRouter()


@router.post("/create_task")
async def create_export_task(
    background_tasks: BackgroundTasks,
    platform: str = Query(..., description="平台: douyin 或 tiktok"),
    aweme_id: str = Query(..., description="视频ID"),
    max_comments: int = Query(default=1000, description="最大评论数"),
    filename: str = Query(default=None, description="自定义文件名（不含扩展名）"),
):
    """
    创建评论导出任务（异步执行）
    """
    # 限制最大评论数
    if max_comments > MAX_COMMENTS:
        max_comments = MAX_COMMENTS

    # 生成文件名
    if not filename:
        filename = f"{platform}_comments_{aweme_id}"

    # 创建任务
    task = task_manager.create_task(platform, aweme_id, max_comments, filename)

    # 在后台执行任务
    background_tasks.add_task(task_manager.execute_task, task.task_id)

    return {
        "code": 200,
        "router": "/tasks/comments/create_task",
        "data": {
            "task_id": task.task_id,
            "platform": task.platform,
            "aweme_id": task.aweme_id,
            "max_comments": task.max_comments,
            "status": task.status,
            "file_path": task.file_path,
            "created_at": task.created_at.isoformat(),
        },
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    """
    task = task_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "code": 200,
        "router": "",
        "data": {
            "task_id": task.task_id,
            "platform": task.platform,
            "aweme_id": task.aweme_id,
            "max_comments": task.max_comments,
            "status": task.status,
            "progress": task.progress,
            "total_fetched": task.total_fetched,
            "file_path": task.file_path,
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
        },
    }


@router.get("/tasks")
async def get_all_tasks():
    """
    获取所有任务
    """
    tasks = task_manager.get_all_tasks()

    return {
        "code": 200,
        "router": "",
        "data": {
            "total": len(tasks),
            "tasks": [
                {
                    "task_id": task.task_id,
                    "platform": task.platform,
                    "aweme_id": task.aweme_id,
                    "max_comments": task.max_comments,
                    "status": task.status,
                    "progress": task.progress,
                    "total_fetched": task.total_fetched,
                    "file_path": task.file_path,
                    "error_message": task.error_message,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "completed_at": task.completed_at.isoformat()
                    if task.completed_at
                    else None,
                }
                for task in tasks
            ],
        },
    }


@router.get("/download/{task_id}")
async def download_task_file(task_id: str):
    """
    下载任务文件
    """
    task = task_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务未完成，无法下载")

    if not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    filename = os.path.basename(task.file_path)

    return FileResponse(
        path=task.file_path,
        filename=filename,
        media_type="text/csv",
    )


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, delete_file: bool = Query(default=False)):
    """
    删除任务
    """
    task = task_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_manager.delete_task(task_id, delete_file)

    return {
        "code": 200,
        "router": "",
        "data": {"task_id": task_id, "delete_file": delete_file},
    }
