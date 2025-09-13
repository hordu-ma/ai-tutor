#!/usr/bin/env python3
"""
API 密钥测试脚本

用于测试和验证 AI Tutor 项目中配置的各种 API 密钥是否有效。
"""

import asyncio
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ApiKeyTester:
    """API 密钥测试器"""

    def __init__(self):
        self.qwen_api_key = os.getenv('QWEN_API_KEY', '').strip()
        self.qwen_base_url = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

        self.kimi_api_key = os.getenv('KIMI_API_KEY', '').strip()
        self.kimi_base_url = os.getenv('KIMI_BASE_URL', 'https://api.moonshot.cn/v1')

    def check_env_file(self):
        """检查环境变量文件"""
        print("🔍 检查环境配置...")
        print("=" * 50)

        env_file = Path('.env')
        if env_file.exists():
            print("✅ .env 文件存在")

            # 读取文件内容（不显示密钥）
            with open(env_file, 'r') as f:
                content = f.read()

            has_qwen = 'QWEN_API_KEY' in content
            has_kimi = 'KIMI_API_KEY' in content

            print(f"{'✅' if has_qwen else '❌'} QWEN_API_KEY 配置项存在")
            print(f"{'✅' if has_kimi else '❌'} KIMI_API_KEY 配置项存在")

        else:
            print("❌ .env 文件不存在")

        print()

    def check_api_key_format(self):
        """检查 API 密钥格式"""
        print("🔑 检查 API 密钥格式...")
        print("=" * 50)

        # 检查 QWEN API 密钥
        if self.qwen_api_key:
            qwen_len = len(self.qwen_api_key)
            qwen_prefix = self.qwen_api_key[:10] + "..." if qwen_len > 10 else self.qwen_api_key
            print(f"✅ QWEN API 密钥已配置 (长度: {qwen_len}, 前缀: {qwen_prefix})")

            if not self.qwen_api_key.startswith('sk-'):
                print("⚠️  QWEN API 密钥格式可能不正确 (通常以 'sk-' 开头)")
        else:
            print("❌ QWEN API 密钥未配置或为空")

        # 检查 KIMI API 密钥
        if self.kimi_api_key:
            kimi_len = len(self.kimi_api_key)
            kimi_prefix = self.kimi_api_key[:10] + "..." if kimi_len > 10 else self.kimi_api_key
            print(f"✅ KIMI API 密钥已配置 (长度: {kimi_len}, 前缀: {kimi_prefix})")

            if not self.kimi_api_key.startswith('sk-'):
                print("⚠️  KIMI API 密钥格式可能不正确 (通常以 'sk-' 开头)")
        else:
            print("❌ KIMI API 密钥未配置或为空")

        print()

    async def test_qwen_api(self):
        """测试 QWEN API 连接"""
        print("🤖 测试 QWEN API...")
        print("=" * 50)

        if not self.qwen_api_key:
            print("❌ QWEN API 密钥未配置，跳过测试")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 测试简单的 chat completion
                response = await client.post(
                    f"{self.qwen_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.qwen_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "qwen-turbo",
                        "messages": [
                            {"role": "user", "content": "Hello"}
                        ],
                        "max_tokens": 10
                    }
                )

                print(f"   状态码: {response.status_code}")

                if response.status_code == 200:
                    print("✅ QWEN API 连接成功！")
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        reply = result['choices'][0]['message']['content']
                        print(f"   API 响应: {reply[:50]}...")
                    return True

                elif response.status_code == 401:
                    print("❌ QWEN API 认证失败 (密钥无效或过期)")
                    try:
                        error_detail = response.json()
                        print(f"   错误详情: {error_detail}")
                    except:
                        print(f"   响应内容: {response.text}")
                    return False

                elif response.status_code == 429:
                    print("⚠️  QWEN API 请求限流 (额度不足或请求过于频繁)")
                    return False

                else:
                    print(f"❌ QWEN API 请求失败 (状态码: {response.status_code})")
                    print(f"   响应内容: {response.text}")
                    return False

        except httpx.ConnectTimeout:
            print("❌ QWEN API 连接超时")
            print("   请检查网络连接或防火墙设置")
            return False

        except Exception as e:
            print(f"❌ QWEN API 测试异常: {str(e)}")
            return False

    async def test_kimi_api(self):
        """测试 KIMI API 连接"""
        print("\n🌙 测试 KIMI API...")
        print("=" * 50)

        if not self.kimi_api_key:
            print("❌ KIMI API 密钥未配置，跳过测试")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 测试简单的 chat completion
                response = await client.post(
                    f"{self.kimi_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.kimi_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {"role": "user", "content": "Hello"}
                        ],
                        "max_tokens": 10
                    }
                )

                print(f"   状态码: {response.status_code}")

                if response.status_code == 200:
                    print("✅ KIMI API 连接成功！")
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        reply = result['choices'][0]['message']['content']
                        print(f"   API 响应: {reply[:50]}...")
                    return True

                elif response.status_code == 401:
                    print("❌ KIMI API 认证失败 (密钥无效或过期)")
                    try:
                        error_detail = response.json()
                        print(f"   错误详情: {error_detail}")
                    except:
                        print(f"   响应内容: {response.text}")
                    return False

                elif response.status_code == 429:
                    print("⚠️  KIMI API 请求限流 (额度不足或请求过于频繁)")
                    return False

                else:
                    print(f"❌ KIMI API 请求失败 (状态码: {response.status_code})")
                    print(f"   响应内容: {response.text}")
                    return False

        except httpx.ConnectTimeout:
            print("❌ KIMI API 连接超时")
            print("   请检查网络连接或防火墙设置")
            return False

        except Exception as e:
            print(f"❌ KIMI API 测试异常: {str(e)}")
            return False

    async def test_backend_integration(self):
        """测试后端集成"""
        print("\n🔗 测试后端 API 集成...")
        print("=" * 50)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 测试后端 AI 服务健康检查
                response = await client.get("http://127.0.0.1:8000/api/v1/homework/health")

                if response.status_code == 200:
                    result = response.json()
                    print("✅ 后端服务连接成功")

                    services = result.get('services', {})
                    print(f"   OCR 服务: {services.get('ocr', 'unknown')}")
                    print(f"   AI 服务: {services.get('ai_qwen', 'unknown')}")
                    print(f"   批改服务: {services.get('homework_service', 'unknown')}")

                    return True
                else:
                    print(f"❌ 后端服务异常 (状态码: {response.status_code})")
                    return False

        except httpx.ConnectError:
            print("❌ 无法连接后端服务")
            print("   请确认后端服务在 http://127.0.0.1:8000 运行")
            return False
        except Exception as e:
            print(f"❌ 后端服务测试异常: {str(e)}")
            return False

    def print_recommendations(self, qwen_ok: bool, kimi_ok: bool, backend_ok: bool):
        """打印建议"""
        print("\n💡 建议和解决方案:")
        print("=" * 50)

        if not qwen_ok and not kimi_ok:
            print("🔴 所有 AI API 都无法正常工作")
            print("   1. 检查 API 密钥是否正确配置")
            print("   2. 确认密钥格式正确 (通常以 'sk-' 开头)")
            print("   3. 验证 API 密钥是否有效且有足够额度")
            print("   4. 检查网络连接和防火墙设置")

        elif not qwen_ok:
            print("🟡 QWEN API 无法正常工作")
            print("   1. 检查 QWEN_API_KEY 配置")
            print("   2. 登录阿里云 DashScope 控制台验证密钥")
            print("   3. 确认账户余额充足")

        elif not kimi_ok:
            print("🟡 KIMI API 无法正常工作")
            print("   1. 检查 KIMI_API_KEY 配置")
            print("   2. 登录月之暗面控制台验证密钥")
            print("   3. 确认账户余额充足")

        else:
            print("🟢 所有 AI API 都正常工作！")

        if backend_ok:
            print("✅ 后端服务集成正常")
        else:
            print("❌ 后端服务需要检查")
            print("   1. 确认后端服务正在运行 (make dev)")
            print("   2. 检查服务日志中的错误信息")

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 AI Tutor API 密钥测试工具")
        print("=" * 60)
        print()

        # 基础检查
        self.check_env_file()
        self.check_api_key_format()

        # API 连接测试
        qwen_ok = await self.test_qwen_api()
        kimi_ok = await self.test_kimi_api()
        backend_ok = await self.test_backend_integration()

        # 结果汇总
        print(f"\n📊 测试结果汇总:")
        print("=" * 50)
        total_tests = 3
        passed_tests = sum([qwen_ok, kimi_ok, backend_ok])

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {total_tests - passed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        # 打印建议
        self.print_recommendations(qwen_ok, kimi_ok, backend_ok)

        return passed_tests >= 2  # 至少有 2 个测试通过才算成功


async def main():
    """主函数"""
    tester = ApiKeyTester()
    success = await tester.run_all_tests()

    if success:
        print(f"\n🎉 API 配置基本正常，可以进行作业批改测试！")
        print("   运行: uv run python test_homework_api.py")
    else:
        print(f"\n⚠️  请根据上述建议修复 API 配置问题")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试执行出错: {e}")
