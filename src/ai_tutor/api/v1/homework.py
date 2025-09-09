"""
作业批改相关API端点
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO

from ...services.student import HomeworkService
from ...core.config import settings
from ...core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/grade", summary="作业批改")
async def grade_homework(
    file: UploadFile = File(...),
    subject: str = Form("math"),
    provider: str = Form("qwen"),
):
    """
    作业批改接口
    
    - **file**: 作业图片文件
    - **subject**: 科目 (math/english)
    - **provider**: AI服务提供商 (qwen/kimi)
    """
    
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        logger.warning("不支持的文件类型", content_type=file.content_type)
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}"
        )
    
    # 验证文件大小
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        logger.warning("文件过大", file_size=len(file_content))
        raise HTTPException(
            status_code=400,
            detail=f"文件过大。最大支持 {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # 加载图片
        image = Image.open(BytesIO(file_content))
        
        # 初始化作业批改服务
        homework_service = HomeworkService(provider=provider)
        
        # 执行批改
        result = await homework_service.grade_homework(
            image=image,
            subject=subject
        )
        
        logger.info(
            "作业批改完成",
            filename=file.filename,
            subject=subject,
            provider=provider,
            processing_time=result["processing_time"]
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "ocr_text": result["ocr_text"],
                    "correction": result["correction"],
                    "metadata": {
                        "filename": file.filename,
                        "subject": subject,
                        "provider": provider,
                        "processing_time": result["processing_time"],
                        "file_size": len(file_content)
                    }
                },
                "message": "作业批改完成"
            }
        )
        
    except Exception as e:
        logger.error("作业批改失败", filename=file.filename, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"作业批改失败: {str(e)}"
        )


@router.get("/subjects", summary="获取支持的科目列表")
async def get_supported_subjects():
    """获取系统支持的科目列表"""
    subjects = [
        {"code": "math", "name": "数学", "description": "数学作业批改"},
        {"code": "english", "name": "英语", "description": "英语作业批改"},
    ]
    
    return {
        "success": True,
        "data": subjects,
        "message": "获取科目列表成功"
    }


@router.get("/health", summary="作业批改服务健康检查")
async def homework_health():
    """检查作业批改服务健康状态"""
    try:
        # 测试OCR服务
        from ...services.ocr import get_ocr_service
        ocr_service = get_ocr_service()
        
        # 测试AI服务
        from ...services.llm import get_llm_service
        ai_service = get_llm_service("qwen")
        
        return {
            "status": "healthy",
            "services": {
                "ocr": "available",
                "ai_qwen": "available",
                "homework_service": "ready"
            }
        }
        
    except Exception as e:
        logger.error("作业批改服务健康检查失败", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
