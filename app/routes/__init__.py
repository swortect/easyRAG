from fastapi import APIRouter
from .web import router as web_router
from .ws import router as ws_router
from .api import router as api_router

# 定义一个总路由
router = APIRouter()

# 包含所有子路由
router.include_router(web_router, prefix="")
router.include_router(ws_router, prefix="")
router.include_router(api_router, prefix="/api")