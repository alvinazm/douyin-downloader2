"""
Instagram 博主最新视频解析 API

POST /api/instagram/creator_latest
Body: { "url": "https://www.instagram.com/<user>/reels/", "n": 2, "list_limit": 20 }

实现思路见 crawlers/instagram/creator_latest.py
文档参考：/Users/azm/MyProject/ins-dl/docs/ins-fetch-latest.md
"""
import traceback

from fastapi import APIRouter, Body, Request

from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
from crawlers.instagram.creator_latest import get_creator_latest_reels_async
from crawlers.utils.logger import logger

router = APIRouter()


@router.post(
    "/creator_latest",
    response_model=ResponseModel,
    tags=["Instagram-API"],
    summary="获取 Instagram 博主最近 N 条视频元数据",
)
async def instagram_creator_latest(
    request: Request,
    url: str = Body(..., embed=True, description="作者 /reels/ 链接"),
    n: int = Body(default=2, embed=True, ge=1, le=20, description="返回几条"),
    list_limit: int = Body(
        default=20, embed=True, ge=1, le=50, description="列表抓取上限（用于排序）"
    ),
):
    """
    输入作者 reels 链接，按发布时间倒序返回最近 N 条视频元数据。

    每条返回：
    - shortcode: Instagram 短码
    - url: 完整 reel URL（可用于下载）
    - title / description
    - uploader / uploader_id
    - timestamp (Unix 秒)
    - upload_date (YYYYMMDD)
    - formatted_publish_time (YYYY-MM-DD HH:MM:SS UTC+8)
    - like_count / comment_count / view_count
    - thumbnail
    """
    logger.info(f"[Instagram-API] 抓取作者最近视频: url={url}, n={n}")
    try:
        result = await get_creator_latest_reels_async(url, n=n, list_limit=list_limit)
        items = result.get("items") or []
        warning = result.get("warning")
        logger.info(
            f"[Instagram-API] 抓取成功: username={result.get('username')}, items={len(items)}"
        )
        return ResponseModel(
            code=200,
            router=request.url.path,
            data={
                "username": result.get("username"),
                "items": items,
                "warning": warning,
            },
        )
    except Exception as e:
        logger.error(
            f"[Instagram-API] 抓取作者最近视频失败: url={url}, err={e}"
        )
        logger.error(traceback.format_exc())
        raise _to_http_500(e, request)


def _to_http_500(e: Exception, request: Request):
    from fastapi import HTTPException

    return HTTPException(
        status_code=500,
        detail=ErrorResponseModel(
            code=500,
            message=str(e),
            router=request.url.path,
            params=dict(request.query_params),
        ).dict(),
    )
