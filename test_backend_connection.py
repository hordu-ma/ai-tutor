#!/usr/bin/env python3
"""
后端服务连接测试脚本

用于测试AI Tutor后端服务的各项功能和API端点是否正常工作。
"""

import asyncio
import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional


class BackendTester:
    """后端服务测试器"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_result(self, test_name: str, success: bool, details: Optional[Dict] = None):
        """记录测试结果"""
        self.test_results[test_name] = {
            "success": success,
            "details": details or {}
        }
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {json.dumps(details, ensure_ascii=False, indent=2)}")

    async def test_health_check(self):
        """测试健康检查端点"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
            self.log_result("健康检查 (/health)", success, details)
            return success
        except Exception as e:
            self.log_result("健康检查 (/health)", False, {"error": str(e)})
            return False

    async def test_api_v1_health(self):
        """测试API v1健康检查"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")
            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
            self.log_result("API v1 健康检查 (/api/v1/health)", success, details)
            return success
        except Exception as e:
            self.log_result("API v1 健康检查 (/api/v1/health)", False, {"error": str(e)})
            return False

    async def test_homework_subjects(self):
        """测试获取支持的科目列表"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/homework/subjects")
            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
            self.log_result("获取科目列表 (/api/v1/homework/subjects)", success, details)
            return success
        except Exception as e:
            self.log_result("获取科目列表 (/api/v1/homework/subjects)", False, {"error": str(e)})
            return False

    async def test_homework_health(self):
        """测试作业批改服务健康检查"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/homework/health")
            success = response.status_code in [200, 503]  # 503也是正常响应（服务不可用但端点存在）
            details = {
                "status_code": response.status_code,
                "response": response.json() if response.status_code in [200, 503] else response.text
            }
            self.log_result("作业批改服务健康检查 (/api/v1/homework/health)", success, details)
            return success
        except Exception as e:
            self.log_result("作业批改服务健康检查 (/api/v1/homework/health)", False, {"error": str(e)})
            return False

    async def test_students_list(self):
        """测试获取学生列表"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/students")
            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
            self.log_result("获取学生列表 (/api/v1/students)", success, details)
            return success
        except Exception as e:
            self.log_result("获取学生列表 (/api/v1/students)", False, {"error": str(e)})
            return False

    async def test_cors_headers(self):
        """测试CORS头部设置"""
        try:
            response = await self.client.options(
                f"{self.base_url}/api/v1/health",
                headers={
                    "Origin": "http://localhost:6173",
                    "Access-Control-Request-Method": "GET"
                }
            )
            cors_headers = {
                key: value for key, value in response.headers.items()
                if key.lower().startswith('access-control')
            }
            success = "access-control-allow-origin" in response.headers
            details = {
                "status_code": response.status_code,
                "cors_headers": cors_headers
            }
            self.log_result("CORS 头部检查", success, details)
            return success
        except Exception as e:
            self.log_result("CORS 头部检查", False, {"error": str(e)})
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始后端服务连接测试...\n")

        # 基础连接测试
        print("📡 基础连接测试:")
        await self.test_health_check()
        await self.test_api_v1_health()
        print()

        # API端点测试
        print("🔌 API 端点测试:")
        await self.test_homework_subjects()
        await self.test_homework_health()
        await self.test_students_list()
        print()

        # 网络配置测试
        print("🌐 网络配置测试:")
        await self.test_cors_headers()
        print()

        # 测试结果汇总
        self.print_summary()

    def print_summary(self):
        """打印测试结果汇总"""
        print("📊 测试结果汇总:")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {test_name}")
                    if "error" in result["details"]:
                        print(f"    错误: {result['details']['error']}")

        print("\n💡 建议:")
        if failed_tests == total_tests:
            print("  - 后端服务可能未启动，请检查服务状态")
            print("  - 确认后端服务运行在 http://127.0.0.1:8000")
            print("  - 检查防火墙和网络连接")
        elif failed_tests > 0:
            print("  - 部分API端点可能需要额外的依赖或配置")
            print("  - 检查.env文件中的配置项")
            print("  - 查看后端服务日志获取更多信息")
        else:
            print("  - 🎉 所有测试通过！前后端可以正常对接")


async def main():
    """主函数"""
    async with BackendTester() as tester:
        await tester.run_all_tests()


def check_backend_startup():
    """检查后端启动的先决条件"""
    print("🔍 检查后端启动条件...\n")

    # 检查.env文件
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env 文件存在")
    else:
        print("❌ .env 文件不存在")
        print("   建议: cp .env.example .env")

    # 检查uv环境
    try:
        import subprocess
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv 已安装: {result.stdout.strip()}")
        else:
            print("❌ uv 未正确安装")
    except FileNotFoundError:
        print("❌ uv 未找到")

    # 检查依赖文件
    pyproject_file = Path("pyproject.toml")
    if pyproject_file.exists():
        print("✅ pyproject.toml 存在")
    else:
        print("❌ pyproject.toml 不存在")

    print("\n启动后端服务的命令:")
    print("  uv run python -m src.ai_tutor.main")
    print("或")
    print("  uv run uvicorn src.ai_tutor.main:app --host 0.0.0.0 --port 8000 --reload")
    print()


if __name__ == "__main__":
    print("AI Tutor 后端连接测试工具")
    print("=" * 40)
    print()

    # 先检查启动条件
    check_backend_startup()

    # 运行连接测试
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试执行出错: {e}")
