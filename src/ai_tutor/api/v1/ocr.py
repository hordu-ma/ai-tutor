"""
OCR相关API端点
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO

from ...services.ocr import get_ocr_service
from ...core.config import settings
from ...core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/extract", summary="OCR文本提取")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    从上传的图片中提取文本
    
    - **file**: 图片文件（支持JPEG、PNG、JPG、WEBP格式）
    
    返回提取的文本内容
    """
    
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        logger.warning("不支持的文件类型", content_type=file.content_type)
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。支持的类型: {settings.ALLOWED_IMAGE_TYPES}"
        )
    
    # 验证文件大小
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        logger.warning("文件过大", file_size=len(file_content), max_size=settings.MAX_FILE_SIZE)
        raise HTTPException(
            status_code=400,
            detail=f"文件过大。最大支持 {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # 加载图片
        image = Image.open(BytesIO(file_content))
        
        # 获取OCR服务
        ocr_service = get_ocr_service()
        
        # 提取文本
        extracted_text = await ocr_service.extract_text(image)
        
        logger.info(
            "OCR提取完成",
            filename=file.filename,
            file_size=len(file_content),
            text_length=len(extracted_text)
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "text": extracted_text,
                    "metadata": {
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "file_size": len(file_content),
                        "text_length": len(extracted_text),
                        "ocr_engine": settings.OCR_ENGINE
                    }
                },
                "message": "文本提取成功"
            }
        )
        
    except Exception as e:
        logger.error("OCR处理失败", filename=file.filename, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"OCR处理失败: {str(e)}"
        )


@router.get("/health", summary="OCR服务健康检查")
async def ocr_health():
    """OCR服务健康检查"""
    try:
        ocr_service = get_ocr_service()
        return {
            "status": "healthy",
            "ocr_engine": settings.OCR_ENGINE,
            "service_class": ocr_service.__class__.__name__
        }
    except Exception as e:
        logger.error("OCR服务不健康", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e)
            }
        )
