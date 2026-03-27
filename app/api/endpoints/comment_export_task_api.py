# 使用MinMax API进行评论分类
import os
import csv
import json
import time
import yaml
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from starlette.responses import FileResponse, JSONResponse
from openai import OpenAI
from app.api.models.APIResponseModel import ErrorResponseModel
from app.api.endpoints.comment_export_tasks import task_manager
from app.api.endpoints.logger import log_comment_export, log_comment_classify
from app.config import MAX_COMMENTS

router = APIRouter()

MINIMAX_API_KEY = None
OPENAI_BASE_URL = "https://api.minimaxi.com/v1"

SYSTEM_PROMPT = """You are a comment classifier. Classify each comment into one of these categories:
- praise: 正面反馈、赞美、感谢
- question: 提问、询问信息
- neutral: 通用反应（笑哈哈、哇）、仅表情包
- constructive: 建设性批评、建议、详细反馈
- spam: 推广链接、垃圾信息、机器人重复内容
- hate: 仇恨、侮辱、威胁

For each comment, also provide:
- confidence: 0-100, confidence level
- action: recommended action (delete, reply, thank, ignore)
- reason: brief reason in Chinese for the classification

Return JSON array like: [{"id":"c0","category":"question","confidence":85,"action":"reply","reason":"..."}]"""


def load_config():
    global MINIMAX_API_KEY
    global OPENAI_BASE_URL
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )

    env_path = os.path.join(project_root, ".env")
    MINIMAX_API_KEY = None
    OPENAI_BASE_URL = "https://api.minimaxi.com/v1"

    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "MINIMAX_API_KEY":
                            MINIMAX_API_KEY = value
                        elif key == "OPENAI_BASE_URL":
                            OPENAI_BASE_URL = value

    if not MINIMAX_API_KEY:
        config_path = os.path.join(project_root, "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        minimax_config = config.get("MINIMAX_API_KEY", {})
        if isinstance(minimax_config, dict):
            MINIMAX_API_KEY = minimax_config.get("MINIMAX_API_KEY")
        else:
            MINIMAX_API_KEY = minimax_config
        OPENAI_BASE_URL = config.get("OPENAI_BASE_URL", "https://api.minimaxi.com/v1")

    return MINIMAX_API_KEY, OPENAI_BASE_URL


def extract_json(text):
    text = text.strip()
    text = re.sub(r"<think>[\s\S]*?</think>", "", text)
    matches = re.findall(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if matches:
        return matches[-1]
    return text


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

    # 生成文件名（始终使用时间戳确保唯一）
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{platform}_comments_{aweme_id}_{timestamp}"

    # 创建任务
    task = task_manager.create_task(platform, aweme_id, max_comments, filename)

    # 记录日志 - 用户提交导出CSV
    log_comment_export(platform, aweme_id, "submit", max_comments=max_comments)

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

    classified_file_path = task.file_path.replace(".csv", "_classified.csv")
    if task.classification_status != "completed" and task.status == "completed":
        if os.path.exists(classified_file_path):
            task.classification_status = "completed"
            task.classified_file_path = classified_file_path

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
            "classification_status": task.classification_status or "none",
            "classification_progress": task.classification_progress or 0,
            "classification_summary": task.classification_summary,
            "classified_file_path": task.classified_file_path,
        },
    }


@router.get("/tasks")
async def get_all_tasks():
    """
    获取所有任务
    """
    tasks = task_manager.get_all_tasks()

    task_list = []
    for task in tasks:
        classified_file_path = task.file_path.replace(".csv", "_classified.csv")
        classification_status = task.classification_status or "none"
        if classification_status != "completed" and task.status == "completed":
            if os.path.exists(classified_file_path):
                classification_status = "completed"
                task.classification_status = "completed"
                task.classified_file_path = classified_file_path

        task_list.append(
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
                "classification_status": classification_status,
                "classification_progress": task.classification_progress or 0,
                "classification_summary": task.classification_summary,
                "classified_file_path": task.classified_file_path,
            }
        )

    return {
        "code": 200,
        "router": "",
        "data": {
            "total": len(task_list),
            "tasks": task_list,
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

    try:
        task_manager.delete_task(task_id, delete_file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "code": 200,
        "router": "",
        "data": {"task_id": task_id, "delete_file": delete_file},
    }


@router.post("/classify/{task_id}")
async def start_classify(
    task_id: str,
    batch_size: int = Query(default=20, description="每批评论数量"),
    workers: int = Query(default=5, description="并发线程数"),
):
    """
    启动AI评论分类（异步执行）
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务未完成，无法分类")

    if not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="评论文件不存在")

    if task.classification_status == "running":
        raise HTTPException(status_code=400, detail="分类正在进行中")

    # 统计评论总数用于日志
    total_comments = 0
    with open(task.file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("评论内容"):
                total_comments += 1

    # 记录日志 - 用户提交AI分类
    log_comment_classify(
        task.platform,
        task.aweme_id,
        "submit",
        total_comments=total_comments,
        batch_size=batch_size,
        workers=workers,
    )

    task_manager.update_classification_status(task_id, "running", 0)
    asyncio.get_event_loop().run_in_executor(
        None, execute_classify_task_sync, task_id, batch_size, workers
    )

    return {
        "code": 200,
        "router": "/tasks/comments/classify",
        "data": {"task_id": task_id, "status": "started", "message": "分类任务已启动"},
    }


def execute_classify_task_sync(task_id: str, batch_size: int, workers: int):
    """同步执行分类任务（在后台线程中运行）"""
    from app.api.endpoints.comment_export_tasks import task_manager

    api_key, base_url = load_config()
    if not api_key:
        task_manager.update_classification_status(
            task_id, "failed", error_message="MINIMAX_API_KEY not configured"
        )
        # 记录分类失败 - API未配置
        task = task_manager.get_task(task_id)
        if task:
            log_comment_classify(
                task.platform,
                task.aweme_id,
                "failed",
                error="MINIMAX_API_KEY not configured",
            )
        return

    task = task_manager.get_task(task_id)
    if not task:
        return

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        comments = []
        original_rows = []
        with open(task.file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if row.get("评论内容"):
                    original_rows.append(row)
                    comments.append(
                        {"comment_id": f"c{i}", "text": row["评论内容"][:500]}
                    )

        total_batches = (len(comments) + batch_size - 1) // batch_size

        def classify_single_batch(args):
            idx, batch = args
            comment_text = "\n".join(
                [f"[{c['comment_id']}] {c['text'][:500]}" for c in batch]
            )

            try:
                response = client.chat.completions.create(
                    model="MiniMax-M2.7",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Classify these comments:\n\n{comment_text}",
                        },
                    ],
                    temperature=1.0,
                    max_tokens=4096,
                )
                raw = response.choices[0].message.content
                text = extract_json(raw)
                batch_results = json.loads(text)

                if isinstance(batch_results, list):
                    return batch_results
                else:
                    return [batch_results]
            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                return [
                    {
                        "id": c["comment_id"],
                        "category": "error",
                        "confidence": 0,
                        "action": "flag_review",
                        "reason": f"Classification error: {str(e)[:100]}",
                    }
                    for c in batch
                ]

        batches = [
            (i, comments[i : i + batch_size])
            for i in range(0, len(comments), batch_size)
        ]
        results = []
        completed = 0

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(classify_single_batch, batch): batch
                for batch in batches
            }
            for future in as_completed(futures):
                batch_results = future.result()
                results.extend(batch_results)
                completed += 1
                progress = int((completed / total_batches) * 100)
                task_manager.update_classification_status(task_id, "running", progress)
                # 记录分类进度
                log_comment_classify(
                    task.platform,
                    task.aweme_id,
                    "progress",
                    progress=progress,
                    completed_batches=completed,
                    total_batches=total_batches,
                )
                time.sleep(0.5)

        class_map = {c["id"]: c for c in results}
        classified = []
        for i, comment in enumerate(comments):
            cid = comment["comment_id"]
            cls = class_map.get(
                cid,
                {
                    "category": "unclassified",
                    "confidence": 0,
                    "action": "flag_review",
                    "reason": "Not classified",
                },
            )
            classified.append(
                {
                    **comment,
                    "classification": cls.get("category", "unclassified"),
                    "confidence": cls.get("confidence", 0),
                    "action": cls.get("action", "flag_review"),
                    "reason": cls.get("reason", ""),
                }
            )

        output_filename = task.file_path.replace(".csv", "_classified.csv")
        fieldnames = list(original_rows[0].keys()) + [
            "classification",
            "confidence",
            "action",
            "reason",
        ]
        with open(output_filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, c in enumerate(classified):
                row = dict(original_rows[i])
                row["classification"] = c.get("classification", "")
                row["confidence"] = c.get("confidence", "")
                row["action"] = c.get("action", "")
                row["reason"] = c.get("reason", "")
                writer.writerow(row)

        counts = {}
        for c in classified:
            cat = c.get("classification", "unknown")
            counts[cat] = counts.get(cat, 0) + 1

        task_manager.update_classification_status(
            task_id, "completed", 100, counts, output_filename
        )
        # 记录分类完成
        log_comment_classify(
            task.platform,
            task.aweme_id,
            "completed",
            file_path=output_filename,
            summary=counts,
        )

    except Exception as e:
        task_manager.update_classification_status(
            task_id, "failed", error_message=str(e)
        )
        # 记录分类失败
        log_comment_classify(task.platform, task.aweme_id, "failed", error=str(e))


@router.get("/download_classified/{task_id}")
async def download_classified_file(task_id: str):
    """
    下载已分类的评论文件
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    classified_path = task.file_path.replace(".csv", "_classified.csv")
    if not os.path.exists(classified_path):
        raise HTTPException(status_code=404, detail="分类文件不存在，请先执行分类")

    filename = os.path.basename(classified_path)
    return FileResponse(path=classified_path, filename=filename, media_type="text/csv")


@router.get("/classification_status/{task_id}")
async def get_classification_status(task_id: str):
    """
    获取评论分类状态
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "code": 200,
        "router": "/tasks/comments/classification_status",
        "data": {
            "task_id": task_id,
            "classification_status": task.classification_status or "none",
            "classification_progress": task.classification_progress,
            "classification_summary": task.classification_summary,
            "classified_file_path": task.classified_file_path,
            "error_message": task.error_message,
        },
    }
