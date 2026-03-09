import os
import csv
import asyncio
import time
from datetime import datetime
from fastapi import APIRouter, Request, Query, HTTPException
from starlette.responses import FileResponse
from crawlers.douyin.web.web_crawler import DouyinWebCrawler
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

router = APIRouter()
Crawler = DouyinWebCrawler()

# 读取配置文件
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "config.yaml",
)


async def fetch_all_comments(aweme_id: str, max_comments: int = None):
    """
    获取视频的所有评论（支持分页）
    """
    all_comments = []
    cursor = 0
    count = 20
    total_count = 0

    while True:
        try:
            response = await Crawler.fetch_video_comments(
                aweme_id=aweme_id, cursor=cursor, count=count
            )

            if not response or "comments" not in response:
                break

            comments = response.get("comments", [])
            if not comments:
                break

            all_comments.extend(comments)
            total_count += len(comments)

            # 如果达到最大评论数，停止获取
            if max_comments and total_count >= max_comments:
                all_comments = all_comments[:max_comments]
                break

            # 更新游标
            cursor = response.get("cursor", 0)
            if response.get("has_more", False) == False:
                break

            # 添加延迟，避免请求过快
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error fetching comments: {e}")
            break

    return all_comments


def parse_comment_data(comment):
    """
    解析单条评论数据，提取所需字段
    """
    try:
        user_info = comment.get("user", {})
        text = comment.get("text", "")
        digg_count = comment.get("digg_count", 0)
        create_time = comment.get("create_time", 0)

        # 将时间戳转换为可读时间
        if create_time:
            # 抖音的时间戳已经是秒级，不需要转换
            time_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = ""

        nickname = user_info.get("nickname", "未知用户")

        return {
            "评论人": nickname,
            "评论内容": text,
            "点赞量": digg_count,
            "评论时间": time_str,
        }
    except Exception as e:
        print(f"Error parsing comment: {e}")
        return None


async def save_comments_to_csv(comments, file_path: str):
    """
    将评论数据保存到CSV文件
    """
    try:
        # 创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 写入CSV文件
        with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()

            # 写入数据
            for comment in comments:
                parsed_data = parse_comment_data(comment)
                if parsed_data:
                    writer.writerow(parsed_data)

        return True
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return False


@router.get("/comments/export", response_model=None)
async def export_comments_to_csv(
    request: Request,
    aweme_id: str = Query(example="7372484719365098803", description="作品id/Video id"),
    max_comments: int = Query(
        default=100, description="最大评论数/Max comments to fetch"
    ),
    filename: str = Query(
        default=None, description="自定义文件名/Custom filename without extension"
    ),
):
    """
    # [中文]
    ### 用途:
    - 获取视频的所有评论并导出为CSV文件
    - 导出的内容包含：评论人、评论内容、点赞量、评论时间
    ### 参数:
    - aweme_id: 作品id
    - max_comments: 最大获取评论数，默认100
    - filename: 自定义文件名（不含扩展名），默认使用aweme_id
    ### 返回:
    - 返回CSV文件供下载

    # [English]
    ### Purpose:
    - Get all comments of a video and export them as a CSV file
    - Exported content includes: commenter, comment content, like count, comment time
    ### Parameters:
    - aweme_id: Video id
    - max_comments: Maximum number of comments to fetch, default 100
    - filename: Custom filename (without extension), default uses aweme_id
    ### Returns:
    - Return CSV file for download

    # [示例/Example]
    aweme_id: 7372484719365098803
    max_comments: 100
    """
    try:
        # 获取所有评论
        comments = await fetch_all_comments(aweme_id, max_comments)

        if not comments:
            return ErrorResponseModel(
                code=404,
                message="未找到评论/No comments found",
                router=request.url.path,
                params=dict(request.query_params),
            )

        # 生成文件名
        if not filename:
            filename = f"douyin_comments_{aweme_id}"

        # 确保下载目录存在
        download_path = download_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "download",
            "comments",
        )

        # 构建CSV文件路径
        csv_filename = f"{filename}.csv"
        csv_file_path = os.path.join(download_path, csv_filename)

        # 保存到CSV
        success = await save_comments_to_csv(comments, csv_file_path)

        if not success:
            return ErrorResponseModel(
                code=500,
                message="保存CSV文件失败/Failed to save CSV file",
                router=request.url.path,
                params=dict(request.query_params),
            )

        # 返回文件
        return FileResponse(
            path=csv_file_path, filename=csv_filename, media_type="text/csv"
        )

    except Exception as e:
        print(f"Error in export_comments_to_csv: {e}")
        return ErrorResponseModel(
            code=500,
            message=str(e),
            router=request.url.path,
            params=dict(request.query_params),
        )
