"""
API v1版本路由配置
"""
from fastapi import APIRouter

# 创建主路由
router = APIRouter()

# 健康检查端点
@router.get("/health")
async def health_check():
    """API健康检查"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "message": "AI Tutor API is running"
    }

# 导入并注册路由模块
from .ocr import router as ocr_router
from .ai import router as ai_router
from .homework import router as homework_router
# from .student import router as student_router

# 注册路由
router.include_router(ocr_router, prefix="/ocr", tags=["OCR"])
router.include_router(ai_router, prefix="/ai", tags=["AI服务"])
router.include_router(homework_router, prefix="/homework", tags=["作业批改"])
# router.include_router(student_router, prefix="/student", tags=["学生"])
