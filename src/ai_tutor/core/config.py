"""
应用核心配置模块
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置配置类"""
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:pass@localhost/ai_tutor"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI模型配置
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    KIMI_API_KEY: str = ""
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    
    # OCR配置
    OCR_ENGINE: str = "tesseract"  # tesseract 或 paddleocr
    
    # 应用配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    
    # 跨域配置
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局设置实例
settings = Settings()
