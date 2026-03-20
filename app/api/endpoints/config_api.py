from fastapi import APIRouter
from app.config import MAX_COMMENTS, API_VERSION, API_ENVIRONMENT, MAX_TAKE_URLS

router = APIRouter()


@router.get("/config")
async def get_config():
    """
    获取前端配置
    """
    return {
        "code": 200,
        "router": "",
        "data": {
            "maxComments": MAX_COMMENTS,
            "maxTakeUrls": MAX_TAKE_URLS,
            "apiVersion": API_VERSION,
            "environment": API_ENVIRONMENT,
        },
    }
