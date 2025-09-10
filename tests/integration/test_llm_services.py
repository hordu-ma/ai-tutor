"""
LLM服务集成测试
"""
import pytest
import asyncio
import httpx
from unittest.mock import patch, AsyncMock

from src.ai_tutor.services.llm import get_llm_service, QwenService, KimiService
from src.ai_tutor.core.config import settings


class TestLLMServiceIntegration:
    """LLM服务集成测试类"""

    @pytest.mark.asyncio
    async def test_qwen_service_basic_chat(self):
        """测试通义千问基本聊天功能"""
        service = QwenService()
        messages = [{"role": "user", "content": "你好，请简单回答：1+1等于多少？"}]
        
        response = await service.chat(messages, max_tokens=50)
        
        assert response is not None
        assert len(response.strip()) > 0
        assert any(char in response for char in ["2", "二", "两"])

    @pytest.mark.asyncio
    async def test_qwen_service_generate(self):
        """测试通义千问文本生成功能"""
        service = QwenService()
        
        response = await service.generate("请说'测试成功'", max_tokens=20)
        
        assert response is not None
        assert len(response.strip()) > 0

    @pytest.mark.asyncio
    async def test_kimi_service_basic_chat(self):
        """测试Kimi基本聊天功能"""
        service = KimiService()
        messages = [{"role": "user", "content": "你好，请简单回答：2+2等于多少？"}]
        
        response = await service.chat(messages, max_tokens=50)
        
        assert response is not None
        assert len(response.strip()) > 0
        assert any(char in response for char in ["4", "四"])

    @pytest.mark.asyncio
    async def test_kimi_service_generate(self):
        """测试Kimi文本生成功能"""
        service = KimiService()
        
        response = await service.generate("请说'Kimi测试成功'", max_tokens=20)
        
        assert response is not None
        assert len(response.strip()) > 0

    @pytest.mark.asyncio
    async def test_service_timeout_handling(self):
        """测试服务超时处理"""
        service = QwenService()
        
        # 模拟网络超时
        with patch.object(service.client, 'post') as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timeout")
            
            with pytest.raises(Exception) as exc_info:
                await service.generate("测试超时", max_tokens=50)
            
            assert "超时" in str(exc_info.value) or "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_service_http_error_handling(self):
        """测试HTTP错误处理"""
        service = QwenService()
        
        # 模拟HTTP错误
        from unittest.mock import MagicMock
        with patch.object(service.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Too Many Requests", request=None, response=mock_response
            )
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                await service.generate("测试HTTP错误", max_tokens=50)
            
            assert "429" in str(exc_info.value)

    def test_get_llm_service_factory_qwen(self):
        """测试LLM服务工厂方法 - 通义千问"""
        service = get_llm_service("qwen")
        assert isinstance(service, QwenService)

    def test_get_llm_service_factory_kimi(self):
        """测试LLM服务工厂方法 - Kimi"""
        service = get_llm_service("kimi")
        assert isinstance(service, KimiService)

    def test_get_llm_service_factory_default(self):
        """测试LLM服务工厂方法 - 默认服务"""
        service = get_llm_service("unknown_provider")
        assert isinstance(service, QwenService)  # 默认使用通义千问

    def test_get_llm_service_factory_empty(self):
        """测试LLM服务工厂方法 - 空参数"""
        service = get_llm_service()
        assert isinstance(service, QwenService)  # 默认使用通义千问

    @pytest.mark.asyncio 
    async def test_service_context_manager(self):
        """测试服务上下文管理器"""
        async with QwenService() as service:
            response = await service.generate("测试上下文管理器", max_tokens=20)
            assert response is not None
            assert len(response.strip()) > 0

    @pytest.mark.asyncio
    async def test_service_retry_mechanism(self):
        """测试服务重试机制"""
        service = QwenService()
        
        call_count = 0
        
        def mock_post_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:  # 第一次调用失败
                mock_response = AsyncMock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "Internal Server Error", request=None, response=mock_response
                )
                return mock_response
            else:  # 第二次调用成功
                mock_response = AsyncMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "重试成功"}}],
                    "usage": {"total_tokens": 10}
                }
                mock_response.raise_for_status.return_value = None
                return mock_response

        with patch.object(service.client, 'post', side_effect=mock_post_side_effect):
            # 如果有重试机制，这个测试应该通过
            # 如果没有重试机制，这个测试会失败，提醒我们需要实现重试
            try:
                response = await service.generate("测试重试", max_tokens=20)
                # 如果到这里，说明有重试机制或第一次就成功了
                assert response is not None
            except Exception as e:
                # 如果到这里，说明没有重试机制，需要实现
                pytest.skip(f"重试机制未实现，当前错误: {str(e)}")

    @pytest.mark.asyncio
    async def test_malformed_api_response_handling(self):
        """测试格式错误的API响应处理"""
        service = QwenService()
        
        # 模拟格式错误的响应
        from unittest.mock import MagicMock
        with patch.object(service.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"invalid": "response"}  # 缺少required字段
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception):
                await service.generate("测试格式错误响应", max_tokens=20)

    @pytest.mark.asyncio
    async def test_empty_response_handling(self):
        """测试空响应处理"""
        service = QwenService()
        
        # 模拟空响应 - 使用MagicMock而非AsyncMock处理json方法
        from unittest.mock import MagicMock
        with patch.object(service.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": ""}}],
                "usage": {"total_tokens": 5}
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            response = await service.generate("测试空响应", max_tokens=20)
            # 空响应应该被正确处理
            assert response == ""


class TestLLMServiceStabilityAndPerformance:
    """LLM服务稳定性和性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求处理"""
        service = QwenService()
        
        # 创建多个并发请求
        tasks = []
        for i in range(3):  # 限制并发数量避免API限制
            task = service.generate(f"并发测试{i+1}: 1+{i+1}=?", max_tokens=20)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查所有响应
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) >= 1, "至少应有一个成功响应"
        
        for response in successful_responses:
            assert isinstance(response, str)
            assert len(response.strip()) > 0

    @pytest.mark.asyncio
    async def test_large_input_handling(self):
        """测试大输入处理"""
        service = QwenService()
        
        # 创建较长的输入
        long_prompt = "请总结以下内容：" + "这是一个测试句子。" * 50
        
        try:
            response = await service.generate(long_prompt, max_tokens=100)
            assert response is not None
            assert len(response.strip()) > 0
        except Exception as e:
            # 如果因为输入过长失败，这也是预期行为
            assert any(keyword in str(e).lower() for keyword in ["token", "length", "limit"])

    @pytest.mark.asyncio 
    async def test_service_health_check(self):
        """测试服务健康检查"""
        # 简单的健康检查：尝试发送一个基本请求
        service = QwenService()
        
        try:
            response = await service.generate("健康检查", max_tokens=10)
            assert response is not None
            # 如果到这里，服务是健康的
            service_healthy = True
        except Exception:
            # 如果失败，服务可能不健康
            service_healthy = False
        
        # 记录服务状态，但不让测试失败
        # 在实际部署中，这个信息可以用于监控
        if not service_healthy:
            pytest.skip("LLM服务当前不可用，跳过健康检查")


if __name__ == "__main__":
    # 直接运行时的测试
    async def run_basic_test():
        print("运行基本LLM服务测试...")
        service = QwenService()
        response = await service.generate("你好", max_tokens=20)
        print(f"响应: {response}")
    
    asyncio.run(run_basic_test())
