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
    url: str = Body(default=None, embed=True, description="单个作者 /reels/ 链接（向后兼容）"),
    urls: list = Body(
        default=None, embed=True, description="多个作者 /reels/ 链接列表（推荐）"
    ),
    n: int = Body(default=2, embed=True, ge=1, le=20, description="每个作者返回几条"),
    list_limit: int = Body(
        default=20, embed=True, ge=1, le=50, description="列表抓取上限（用于排序）"
    ),
):
    """
    输入作者 reels 链接（支持单个 url 或 urls 列表），按发布时间倒序返回
    每个作者最近 N 条视频元数据。

    单数 url 用法：
        POST {url: "https://www.instagram.com/<user>/reels/", n: 2}
        返回: { username, items, warning }

    复数 urls 用法（推荐）：
        POST {urls: ["...reels/", "...reels/", ...], n: 2}
        返回: { results: [{ username, items, warning }, ...] }

    字段说明同单数用法。
    """
    # 归一化入参：urls 优先，回退到 url 包装成单元素列表
    if urls:
        url_list = [u.strip() for u in urls if u and u.strip()]
    elif url:
        url_list = [url.strip()]
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail={
                "code": 422,
                "message": "url 或 urls 必须传一个",
                "router": request.url.path,
                "params": dict(request.query_params),
            },
        )

    if not url_list:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail={
                "code": 422,
                "message": "url 或 urls 不能为空",
                "router": request.url.path,
                "params": dict(request.query_params),
            },
        )

    logger.info(f"[Instagram-API] 抓取 {len(url_list)} 个作者: n={n}")

    # 并发抓取多个作者（Playwright + yt-dlp 阻塞，放到线程池）
    import asyncio
    tasks = [get_creator_latest_reels_async(u, n=n, list_limit=list_limit) for u in url_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 统一异常处理：单个失败不影响其他
    out_results = []
    for u, r in zip(url_list, results):
        if isinstance(r, Exception):
            logger.error(f"[Instagram-API] 抓取失败: url={u}, err={r}")
            out_results.append(
                {
                    "url": u,
                    "username": None,
                    "items": [],
                    "warning": f"抓取失败: {r}",
                }
            )
        else:
            items = r.get("items") or []
            out_results.append(
                {
                    "url": u,
                    "username": r.get("username"),
                    "items": items,
                    "warning": r.get("warning"),
                }
            )

    # 单数 url 模式：返回旧的 schema（向后兼容）
    if not urls and url:
        first = out_results[0]
        return ResponseModel(
            code=200,
            router=request.url.path,
            data={
                "username": first["username"],
                "items": first["items"],
                "warning": first["warning"],
            },
        )

    # urls 模式：返回 results 列表
    return ResponseModel(
        code=200,
        router=request.url.path,
        data={"results": out_results},
    )


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
