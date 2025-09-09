"""
OCR服务基础模块
"""
from abc import ABC, abstractmethod
import asyncio
from io import BytesIO
from typing import Optional
import pytesseract
from PIL import Image

from ...core.logger import LoggerMixin
from ...core.config import settings


class OCRService(ABC, LoggerMixin):
    """OCR服务抽象基类"""
    
    @abstractmethod
    async def extract_text(self, image: Image.Image) -> str:
        """从图片中提取文本"""
        pass
    
    async def preprocess_image(self, image: Image.Image) -> Image.Image:
        """图片预处理"""
        # 转换为RGB格式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 如果图片太大，适当缩放
        max_size = (2048, 2048)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            self.log_event("图片已缩放", original_size=image.size, new_size=image.size)
        
        return image


class TesseractOCR(OCRService):
    """基于Tesseract的OCR服务"""
    
    def __init__(self):
        self.lang = 'chi_sim+eng'  # 支持中文简体和英文
    
    async def extract_text(self, image: Image.Image) -> str:
        """使用Tesseract提取文本"""
        try:
            # 预处理图片
            processed_image = await self.preprocess_image(image)
            
            # 在线程池中运行Tesseract（避免阻塞）
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_string(processed_image, lang=self.lang)
            )
            
            # 清理提取的文本
            text = text.strip()
            self.log_event("OCR文本提取完成", text_length=len(text))
            
            return text
            
        except Exception as e:
            self.log_error("OCR文本提取失败", error_msg=str(e))
            raise


# OCR服务工厂函数
def get_ocr_service() -> OCRService:
    """获取OCR服务实例"""
    engine = settings.OCR_ENGINE.lower()
    
    if engine == "tesseract":
        return TesseractOCR()
    else:
        # 默认使用Tesseract
        return TesseractOCR()
