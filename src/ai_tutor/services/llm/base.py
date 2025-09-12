"""
AI大模型服务基础模块
"""
import json
import re
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
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
    
    def safe_json_parse(self, text: str, fallback_parser: Optional[callable] = None) -> Dict[str, Any]:
        """安全的JSON解析，支持容错和降级策略"""
        if not text or not text.strip():
            self.log_warning("收到空文本，返回默认结构")
            return self._get_fallback_structure()
        
        original_text = text
        cleaned_text = text.strip()
        
        # 第一次尝试：直接解析
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            self.log_warning("JSON直接解析失败", error=str(e), text_preview=cleaned_text[:200])
        
        # 第二次尝试：清洗常见格式问题
        try:
            cleaned_text = self._clean_json_text(cleaned_text)
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            self.log_warning("JSON清洗后解析失败", error=str(e))
        
        # 第三次尝试：提取JSON部分
        try:
            extracted_json = self._extract_json_from_text(cleaned_text)
            if extracted_json:
                return json.loads(extracted_json)
        except json.JSONDecodeError as e:
            self.log_warning("JSON提取后解析失败", error=str(e))
        
        # 第四次尝试：修复常见JSON错误
        try:
            fixed_json = self._fix_common_json_errors(cleaned_text)
            return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            self.log_warning("JSON修复后解析失败", error=str(e))
        
        # 最后的降级策略
        if fallback_parser:
            try:
                result = fallback_parser(original_text)
                if isinstance(result, dict):
                    self.log_event("使用降级解析器成功")
                    return result
            except Exception as e:
                self.log_error("降级解析器失败", exception_msg=str(e))
        
        # 所有方法都失败，使用文本提取的最后手段
        self.log_error("所有JSON解析方法失败，使用紧急降级策略", original_text=original_text[:500])
        return self._emergency_text_extraction(original_text)
    
    def _clean_json_text(self, text: str) -> str:
        """清理JSON文本的常见格式问题"""
        # 移除代码块标记
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
        
        # 移除前后的引号和空格
        text = text.strip().strip('`"\'')
        
        # 处理尾随逗号
        text = re.sub(r',\s*([}\]])', r'\1', text)
        
        # 修复双引号问题
        text = re.sub(r'(["\'])([^"\']*)(["\'])', r'"\2"', text)
        
        return text
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """从文本中提取JSON部分"""
        # 尝试匹配最外层的JSON对象
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # 选择最长的匹配（可能是最完整的）
            return max(matches, key=len)
        
        # 尝试匹配JSON数组
        array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
        matches = re.findall(array_pattern, text, re.DOTALL)
        
        if matches:
            return max(matches, key=len)
        
        return None
    
    def _fix_common_json_errors(self, text: str) -> str:
        """修复常见的JSON错误"""
        # 修复缺失的引号
        text = re.sub(r'(\w+):', r'"\1":', text)  # 为key添加引号
        
        # 修复Python的True/False/None
        text = re.sub(r'\bTrue\b', 'true', text)
        text = re.sub(r'\bFalse\b', 'false', text)
        text = re.sub(r'\bNone\b', 'null', text)
        
        # 修复单引号为双引号
        text = re.sub(r"\'([^\']*)\'",'"\1"', text)
        
        # 移除多余的逗号
        text = re.sub(r',\s*([}\]])', r'\1', text)
        
        return text
    
    def _emergency_text_extraction(self, text: str) -> Dict[str, Any]:
        """紧急情况下的文本提取降级策略"""
        result = {
            "questions": [],
            "overall_score": 0,
            "overall_suggestions": "AI返回格式异常，无法正常解析批改结果。",
            "parsing_error": True,
            "raw_response": text[:1000]  # 保留前1000字符用于调试
        }
        
        # 尝试提取一些基本信息
        score_match = re.search(r'(?:总分|得分|score)[:\s]*([0-9.]+)', text, re.IGNORECASE)
        if score_match:
            try:
                result["overall_score"] = float(score_match.group(1))
            except ValueError:
                pass
        
        # 尝试提取建议
        suggestion_patterns = [
            r'(?:建议|suggestion)[:\s]*(.{1,200})',
            r'(?:总结|summary)[:\s]*(.{1,200})',
        ]
        
        for pattern in suggestion_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                suggestion = match.group(1).strip()
                if len(suggestion) > 10:  # 确保不是噪音
                    result["overall_suggestions"] = suggestion
                    break
        
        return result
    
    def _get_fallback_structure(self) -> Dict[str, Any]:
        """获取默认的回退结构"""
        return {
            "questions": [],
            "overall_score": 0,
            "total_score": 0,
            "accuracy_rate": 0.0,
            "overall_suggestions": "未能获取到有效的批改结果",
            "weak_knowledge_points": [],
            "study_recommendations": []
        }


class QwenService(LLMService):
    """通义千问AI服务"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.QWEN_API_KEY
        self.base_url = base_url or settings.QWEN_BASE_URL
        self.client = httpx.AsyncClient(timeout=60.0)  # 增加超时时间到60秒
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟（秒）
        
        if not self.api_key:
            raise ValueError("Qwen API key 未配置")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用通义千问聊天接口（支持重试）"""
        for attempt in range(self.max_retries):
            try:
                return await self._chat_single_attempt(messages, **kwargs)
            except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                if attempt < self.max_retries - 1:
                    self.log_event(
                        "API调用超时，准备重试",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        delay_seconds=self.retry_delay
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # 递增延迟
                    continue
                else:
                    # 最后一次重试也失败了
                    self.log_error("所有重试尝试都失败", attempts=self.max_retries)
                    raise e
            except Exception as e:
                # 非超时异常不重试，直接抛出
                raise e
        
        # 这里不应该到达，但为了安全起见
        raise Exception("所有重试尝试都失败")
    
    async def _chat_single_attempt(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """单次API调用尝试"""
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
            
        except httpx.TimeoutException:
            self.log_error("Qwen API请求超时", timeout_seconds=60.0)
            raise  # 让上层重试机制处理
        except httpx.ConnectTimeout:
            self.log_error("Qwen API连接超时")
            raise  # 让上层重试机制处理
        except httpx.ReadTimeout:
            self.log_error("Qwen API读取超时")
            raise  # 让上层重试机制处理
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            self.log_error("Qwen API HTTP错误", 
                          status_code=e.response.status_code, 
                          response=error_detail[:500])
            raise Exception(f"Qwen API调用失败 (HTTP {e.response.status_code}): {error_detail[:200]}")
        except Exception as e:
            error_msg = str(e) if str(e) else f"{type(e).__name__}: 未知错误"
            self.log_error("Qwen API调用异常", 
                          exception_type=type(e).__name__, 
                          exception_msg=error_msg)
            raise Exception(f"Qwen API调用异常: {error_msg}")
    
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
        self.client = httpx.AsyncClient(timeout=60.0)  # 增加超时时间到60秒
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟（秒）
        
        if not self.api_key:
            raise ValueError("Kimi API key 未配置")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用Kimi聊天接口（支持重试）"""
        for attempt in range(self.max_retries):
            try:
                return await self._chat_single_attempt(messages, **kwargs)
            except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                if attempt < self.max_retries - 1:
                    self.log_event(
                        "Kimi API调用超时，准备重试",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        delay_seconds=self.retry_delay
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    self.log_error("Kimi API所有重试尝试都失败", attempts=self.max_retries)
                    raise e
            except Exception as e:
                raise e
        
        raise Exception("Kimi API所有重试尝试都失败")
    
    async def _chat_single_attempt(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """单次Kimi API调用尝试"""
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
            
        except httpx.TimeoutException:
            self.log_error("Kimi API请求超时", timeout_seconds=60.0)
            raise  # 让上层重试机制处理
        except httpx.ConnectTimeout:
            self.log_error("Kimi API连接超时")
            raise  # 让上层重试机制处理
        except httpx.ReadTimeout:
            self.log_error("Kimi API读取超时")
            raise  # 让上层重试机制处理
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            self.log_error("Kimi API HTTP错误", 
                          status_code=e.response.status_code, 
                          response=error_detail[:500])
            raise Exception(f"Kimi API调用失败 (HTTP {e.response.status_code}): {error_detail[:200]}")
        except Exception as e:
            error_msg = str(e) if str(e) else f"{type(e).__name__}: 未知错误"
            self.log_error("Kimi API调用异常", 
                          exception_type=type(e).__name__, 
                          exception_msg=error_msg)
            raise Exception(f"Kimi API调用异常: {error_msg}")
    
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
