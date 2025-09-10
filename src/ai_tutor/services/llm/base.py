"""
AI大模型服务基础模块
"""
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx

from ...core.logger import LoggerMixin
from ...core.config import settings


class LLMService(ABC, LoggerMixin):
    """AI大模型服务抽象基类"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送消息并获取回复"""
        pass
    
    @abstractmethod  
    async def generate(self, prompt: str, **kwargs) -> str:
        """根据提示词生成文本"""
        pass


class QwenService(LLMService):
    """通义千问AI服务"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.QWEN_API_KEY
        self.base_url = base_url or settings.QWEN_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            raise ValueError("Qwen API key 未配置")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用通义千问聊天接口"""
        try:
            # 准备请求数据
            data = {
                "model": kwargs.get("model", "qwen-plus"),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            self.log_event(
                "发送Qwen API请求",
                model=data["model"],
                messages_count=len(messages),
                temperature=data["temperature"]
            )
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 提取回复内容
            content = result["choices"][0]["message"]["content"]
            
            self.log_event(
                "Qwen API响应成功",
                response_length=len(content),
                usage=result.get("usage", {})
            )
            
            return content.strip()
            
        except httpx.HTTPStatusError as e:
            self.log_error("Qwen API HTTP错误", status_code=e.response.status_code, response=e.response.text)
            raise Exception(f"Qwen API调用失败: {e.response.status_code}")
        except Exception as e:
            self.log_error("Qwen API调用异常", exception_msg=str(e))
            raise Exception(f"Qwen API调用异常: {str(e)}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


class KimiService(LLMService):
    """Kimi AI服务"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.KIMI_API_KEY
        self.base_url = base_url or settings.KIMI_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            raise ValueError("Kimi API key 未配置")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用Kimi聊天接口"""
        try:
            # 准备请求数据
            data = {
                "model": kwargs.get("model", "moonshot-v1-8k"),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            self.log_event(
                "发送Kimi API请求",
                model=data["model"],
                messages_count=len(messages),
                temperature=data["temperature"]
            )
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 提取回复内容
            content = result["choices"][0]["message"]["content"]
            
            self.log_event(
                "Kimi API响应成功",
                response_length=len(content),
                usage=result.get("usage", {})
            )
            
            return content.strip()
            
        except httpx.HTTPStatusError as e:
            self.log_error("Kimi API HTTP错误", status_code=e.response.status_code, response=e.response.text)
            raise Exception(f"Kimi API调用失败: {e.response.status_code}")
        except Exception as e:
            self.log_error("Kimi API调用异常", exception_msg=str(e))
            raise Exception(f"Kimi API调用异常: {str(e)}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


def get_llm_service(provider: str = "qwen") -> LLMService:
    """获取AI服务实例"""
    if provider.lower() == "qwen":
        return QwenService()
    elif provider.lower() == "kimi":
        return KimiService()
    else:
        # 默认使用通义千问
        return QwenService()
