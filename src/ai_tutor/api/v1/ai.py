"""
AI服务相关API端点
"""
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.llm import get_llm_service
from ...core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[ChatMessage]
    provider: Optional[str] = "qwen"  # "qwen" 或 "kimi"
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000


class GenerateRequest(BaseModel):
    """文本生成请求模型"""
    prompt: str
    provider: Optional[str] = "qwen"
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000


@router.post("/chat", summary="AI聊天对话")
async def chat_with_ai(request: ChatRequest):
    """
    与AI进行聊天对话

    - **messages**: 消息列表
    - **provider**: AI服务提供商 (qwen/kimi)
    - **model**: 模型名称（可选）
    - **temperature**: 生成温度（0-1）
    - **max_tokens**: 最大生成token数
    """

    try:
        # 获取AI服务
        llm_service = get_llm_service(request.provider)

        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # 添加调试日志
        logger.info(
            "收到聊天请求",
            provider=request.provider,
            model=request.model,
            messages_count=len(messages),
            messages_detail=[{"role": msg["role"], "content": msg["content"][:100]} for msg in messages]
        )

        # 调用AI服务
        response = await llm_service.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        logger.info(
            "AI聊天完成",
            provider=request.provider,
            messages_count=len(messages),
            response_length=len(response)
        )

        return {
            "success": True,
            "data": {
                "response": response,
                "provider": request.provider,
                "model": request.model,
                "metadata": {
                    "messages_count": len(messages),
                    "response_length": len(response)
                }
            },
            "message": "AI对话成功"
        }

    except Exception as e:
        logger.error("AI聊天失败", provider=request.provider, error=str(e))
        raise HTTPException(status_code=500, detail=f"AI聊天失败: {str(e)}")


@router.post("/generate", summary="AI文本生成")
async def generate_text(request: GenerateRequest):
    """
    根据提示词生成文本

    - **prompt**: 提示词
    - **provider**: AI服务提供商 (qwen/kimi)
    - **model**: 模型名称（可选）
    - **temperature**: 生成温度（0-1）
    - **max_tokens**: 最大生成token数
    """

    try:
        # 获取AI服务
        llm_service = get_llm_service(request.provider)

        # 生成文本
        response = await llm_service.generate(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        logger.info(
            "AI文本生成完成",
            provider=request.provider,
            prompt_length=len(request.prompt),
            response_length=len(response)
        )

        return {
            "success": True,
            "data": {
                "text": response,
                "provider": request.provider,
                "model": request.model,
                "metadata": {
                    "prompt_length": len(request.prompt),
                    "response_length": len(response)
                }
            },
            "message": "文本生成成功"
        }

    except Exception as e:
        logger.error("AI文本生成失败", provider=request.provider, error=str(e))
        raise HTTPException(status_code=500, detail=f"AI文本生成失败: {str(e)}")


@router.get("/health", summary="AI服务健康检查")
async def ai_health():
    """检查AI服务健康状态"""

    health_status = {
        "qwen": {"status": "unknown", "error": None},
        "kimi": {"status": "unknown", "error": None}
    }

    # 检查Qwen服务
    try:
        qwen_service = get_llm_service("qwen")
        # 发送简单测试消息
        test_response = await qwen_service.generate("hello", max_tokens=10)
        health_status["qwen"] = {"status": "healthy", "error": None}
    except Exception as e:
        health_status["qwen"] = {"status": "unhealthy", "error": str(e)}

    # 检查Kimi服务
    try:
        kimi_service = get_llm_service("kimi")
        # 发送简单测试消息
        test_response = await kimi_service.generate("hello", max_tokens=10)
        health_status["kimi"] = {"status": "healthy", "error": None}
    except Exception as e:
        health_status["kimi"] = {"status": "unhealthy", "error": str(e)}

    # 判断整体健康状态
    overall_healthy = any(service["status"] == "healthy" for service in health_status.values())

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "services": health_status
    }
