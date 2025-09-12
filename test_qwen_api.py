#!/usr/bin/env python3
"""
测试 Qwen API 连接
"""
import asyncio
import httpx
from src.ai_tutor.core.config import settings

async def test_qwen_api():
    """测试 Qwen API 连接"""
    
    # 基础配置检查
    print("=== 配置检查 ===")
    print(f"API Key 配置状态: {'已配置' if settings.QWEN_API_KEY else '未配置'}")
    print(f"API Key 长度: {len(settings.QWEN_API_KEY) if settings.QWEN_API_KEY else 0}")
    print(f"Base URL: {settings.QWEN_BASE_URL}")
    
    if not settings.QWEN_API_KEY:
        print("❌ QWEN_API_KEY 未配置")
        return
    
    # 测试网络连通性
    print("\n=== 网络连通性测试 ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://dashscope.aliyuncs.com")
            print(f"✅ 基础连通性: {response.status_code}")
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        return
    
    # 测试API调用
    print("\n=== API调用测试 ===")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            data = {
                "model": "qwen-plus",
                "messages": [{"role": "user", "content": "你好，请回复一个简单的测试消息"}],
                "temperature": 0.2,
                "max_tokens": 100
            }
            
            headers = {
                "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                "Content-Type": "application/json"
            }
            
            print("发送测试请求...")
            response = await client.post(
                f"{settings.QWEN_BASE_URL}/chat/completions",
                json=data,
                headers=headers
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ API调用成功")
                print(f"响应内容: {content}")
                print(f"Token使用: {result.get('usage', {})}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
    except httpx.TimeoutException:
        print("❌ 请求超时")
    except httpx.ConnectTimeout:
        print("❌ 连接超时")
    except httpx.ReadTimeout:  
        print("❌ 读取超时")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP错误: {e.response.status_code}")
        print(f"错误内容: {e.response.text}")
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_qwen_api())
