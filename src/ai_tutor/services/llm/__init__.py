"""
AI大模型服务模块
"""
from .base import LLMService, QwenService, KimiService, get_llm_service

__all__ = ["LLMService", "QwenService", "KimiService", "get_llm_service"]
