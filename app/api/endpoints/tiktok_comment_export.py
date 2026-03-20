import os
import csv
import asyncio
from datetime import datetime
from fastapi import APIRouter, Request, Query
from starlette.responses import FileResponse
from crawlers.tiktok.web.web_crawler import TikTokWebCrawler
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
from app.config import MAX_COMMENTS

router = APIRouter()
Crawler = TikTokWebCrawler()


async def fetch_and_save_comments_stream(
    aweme_id: str, file_path: str, max_comments: int | None = None
):
    """
    流式获取TikTok评论并保存到CSV文件，避免超时
    """
    cursor = 0
    count = 20
    total_count = 0

    try:
        # 创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 打开CSV文件并写入表头
        with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # 流式获取和写入评论
            while True:
                response = await Crawler.fetch_post_comment(
                    aweme_id=aweme_id, cursor=cursor, count=count, current_region="US"
                )

                if not response or "comments" not in response:
                    break

                comments = response.get("comments", [])
                if not comments:
                    break

                # 立即写入这一批评论
                for comment in comments:
                    if max_comments and total_count >= max_comments:
                        break

                    parsed_data = parse_comment_data(comment)
                    if parsed_data:
                        writer.writerow(parsed_data)
                        total_count += 1

                # 如果达到最大评论数，停止获取
                if max_comments and total_count >= max_comments:
                    break

                # 更新游标
                cursor = response.get("cursor", 0)
                if response.get("has_more", False) == False:
                    break

                # 添加延迟，避免请求过快
                await asyncio.sleep(0.3)

        return total_count

    except Exception as e:
        error_msg = f"无法获取TikTok评论。错误: {str(e)}"
        print(f"Error in fetch_and_save_comments_stream: {e}")
        import traceback

        traceback.print_exc()
        raise Exception(error_msg)


async def fetch_all_comments(aweme_id: str, max_comments: int | None = None):
    """
    获取TikTok视频的所有评论（支持分页）
    """
    all_comments = []
    cursor = 0
    count = 20
    total_count = 0

    while True:
        try:
            response = await Crawler.fetch_post_comment(
                aweme_id=aweme_id, cursor=cursor, count=count, current_region="US"
            )

            if not response or "comments" not in response:
                break

            comments = response.get("comments", [])
            if not comments:
                break

            all_comments.extend(comments)
            total_count += len(comments)

            if max_comments and total_count >= max_comments:
                all_comments = all_comments[:max_comments]
                break

            cursor = response.get("cursor", 0)
            if response.get("has_more", False) == False:
                break

            await asyncio.sleep(0.5)

        except Exception as e:
            error_msg = f"无法获取TikTok评论。错误: {str(e)}"
            print(f"Error fetching comments: {e}")
            import traceback

            traceback.print_exc()
            raise Exception(error_msg)

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

        if create_time:
            time_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
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


async def save_comments_to_csv(comments, file_path: str):
    """
    将评论数据保存到CSV文件
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

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
    aweme_id: str = Query(example="7304809083817774382", description="作品id/Video id"),
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
    - 获取TikTok视频的所有评论并导出为CSV文件
    - 导出的内容包含：评论人、评论内容、点赞量、评论时间
    - 使用流式处理，避免大量数据超时
    ### 参数:
    - aweme_id: 作品id
    - max_comments: 最大获取评论数，默认100，最多{{ MAX_COMMENTS }}
    - filename: 自定义文件名（不含扩展名），默认使用aweme_id
    ### 返回:
    - 返回CSV文件供下载

    # [English]
    ### Purpose:
    - Get all comments of a TikTok video and export them as a CSV file
    - Exported content includes: commenter, comment content, like count, comment time
    - Uses streaming processing to avoid timeout for large datasets
    ### Parameters:
    - aweme_id: Video id
    - max_comments: Maximum number of comments to fetch, default 100, max {{ MAX_COMMENTS }}
    - filename: Custom filename (without extension), default uses aweme_id
    ### Returns:
    - Return CSV file for download

    # [示例/Example]
    aweme_id: 7304809083817774382
    max_comments: 100
    """
    try:
        # 限制最大评论数
        if max_comments > MAX_COMMENTS:
            max_comments = MAX_COMMENTS

        if not filename:
            filename = f"tiktok_comments_{aweme_id}"

        download_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "download",
            "comments",
        )

        csv_filename = f"{filename}.csv"
        csv_file_path = os.path.join(download_path, csv_filename)

        # 使用流式处理获取和保存评论
        total_saved = await fetch_and_save_comments_stream(
            aweme_id, csv_file_path, max_comments
        )

        if total_saved == 0:
            return ErrorResponseModel(
                code=404,
                message="未找到评论/No comments found",
                router=request.url.path,
                params=dict(request.query_params),
            )

        return FileResponse(
            path=csv_file_path, filename=csv_filename, media_type="text/csv"
        )

    except Exception as e:
        print(f"Error in export_comments_to_csv: {e}")
        error_message = str(e)
        if (
            "连接" in error_message
            or "Connection" in error_message
            or "ConnectError" in error_message
        ):
            error_message = "无法连接到TikTok服务。TikTok可能需要网络代理/VPN才能访问，请检查您的网络连接或尝试使用代理。"
        elif "404" in error_message or "NotFound" in error_message:
            error_message = "无法找到该视频或评论，请检查视频ID是否正确。"
        return ErrorResponseModel(
            code=500,
            message=error_message,
            router=request.url.path,
            params=dict(request.query_params),
        )
