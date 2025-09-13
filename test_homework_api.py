#!/usr/bin/env python3
"""
作业批改 API 功能测试脚本

测试 AI Tutor 的作业批改核心功能，验证前后端对接是否正常工作。
"""

import asyncio
import httpx
import json
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class HomeworkApiTester:
    """作业批改 API 测试器"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def create_test_image(self) -> bytes:
        """创建一个测试用的数学题图片"""
        # 创建一个简单的白色背景图片
        width, height = 800, 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # 尝试使用系统字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # 绘制数学题目
        title = "数学作业"
        draw.text((50, 50), title, fill='black', font=font)

        questions = [
            "1. 计算: 25 + 37 = ?",
            "   学生答案: 62",
            "",
            "2. 解方程: 2x + 5 = 15",
            "   学生答案: x = 5",
            "",
            "3. 计算面积: 长方形长8cm，宽6cm",
            "   学生答案: 48 平方厘米"
        ]

        y_position = 120
        for question in questions:
            if question.strip():  # 不是空行
                draw.text((50, y_position), question, fill='black', font=small_font)
            y_position += 40

        # 转换为字节数据
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        return img_bytes.getvalue()

    async def test_homework_grading(self):
        """测试作业批改功能"""
        print("🧮 测试作业批改功能...")

        # 创建测试图片
        test_image_data = self.create_test_image()

        # 准备上传文件
        files = {
            'file': ('test_homework.jpg', test_image_data, 'image/jpeg')
        }

        data = {
            'subject': 'math',
            'provider': 'qwen'
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/homework/grade",
                files=files,
                data=data
            )

            success = response.status_code == 200
            result = response.json() if success else response.text

            print(f"{'✅' if success else '❌'} 作业批改API")
            print(f"   状态码: {response.status_code}")

            if success:
                print(f"   响应格式: {'有success字段' if 'success' in result else '直接数据'}")

                # 检查响应数据结构
                if 'data' in result:
                    data = result['data']
                    print(f"   OCR文本长度: {len(data.get('ocr_text', ''))}")
                    print(f"   批改结果: {'存在' if 'correction' in data else '缺失'}")
                    print(f"   元数据: {'存在' if 'metadata' in data else '缺失'}")

                    if 'metadata' in data:
                        metadata = data['metadata']
                        print(f"   处理时间: {metadata.get('processing_time', 'N/A')}s")
                        print(f"   解析题目数: {metadata.get('questions_parsed', 'N/A')}")

                print(f"   完整响应预览:")
                print(f"   {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            else:
                print(f"   错误详情: {result}")

            return success

        except Exception as e:
            print(f"❌ 作业批改API测试失败")
            print(f"   错误: {str(e)}")
            return False

    async def test_homework_subjects(self):
        """测试获取支持科目列表"""
        print("\n📚 测试科目列表API...")

        try:
            response = await self.client.get(f"{self.base_url}/api/v1/homework/subjects")
            success = response.status_code == 200
            result = response.json() if success else response.text

            print(f"{'✅' if success else '❌'} 科目列表API")
            print(f"   状态码: {response.status_code}")

            if success:
                subjects = result.get('data', [])
                print(f"   支持科目数: {len(subjects)}")
                for subject in subjects:
                    print(f"   - {subject.get('name')} ({subject.get('code')})")
            else:
                print(f"   错误: {result}")

            return success

        except Exception as e:
            print(f"❌ 科目列表API测试失败: {str(e)}")
            return False

    async def test_homework_health(self):
        """测试作业批改服务健康状态"""
        print("\n💚 测试作业批改服务健康状态...")

        try:
            response = await self.client.get(f"{self.base_url}/api/v1/homework/health")
            success = response.status_code == 200
            result = response.json() if success else response.text

            print(f"{'✅' if success else '❌'} 作业批改健康检查")
            print(f"   状态码: {response.status_code}")

            if success:
                services = result.get('services', {})
                print(f"   OCR服务: {services.get('ocr', 'unknown')}")
                print(f"   AI服务: {services.get('ai_qwen', 'unknown')}")
                print(f"   批改服务: {services.get('homework_service', 'unknown')}")
            else:
                print(f"   错误: {result}")

            return success

        except Exception as e:
            print(f"❌ 健康检查失败: {str(e)}")
            return False

    async def test_frontend_compatibility(self):
        """测试前端兼容性 - 检查响应格式"""
        print("\n🔗 测试前端兼容性...")

        # 模拟前端调用方式
        test_image_data = self.create_test_image()

        files = {
            'file': ('homework.jpg', test_image_data, 'image/jpeg')
        }

        data = {
            'subject': 'math',
            'provider': 'qwen'
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/homework/grade",
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()

                # 检查前端期望的数据结构
                checks = {
                    "有success字段": 'success' in result,
                    "有data字段": 'data' in result,
                    "有message字段": 'message' in result
                }

                if 'data' in result:
                    data_checks = {
                        "有ocr_text": 'ocr_text' in result['data'],
                        "有correction": 'correction' in result['data'],
                        "有metadata": 'metadata' in result['data']
                    }
                    checks.update(data_checks)

                print("   响应格式检查:")
                for check_name, passed in checks.items():
                    print(f"   {'✅' if passed else '❌'} {check_name}")

                # 评估前端适配需求
                if all([checks.get("有success字段"), checks.get("有data字段")]):
                    print("   🎉 响应格式与前端API服务层兼容！")
                else:
                    print("   ⚠️  需要前端适配层处理响应格式")

                return True
            else:
                print(f"   ❌ 请求失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ 兼容性测试失败: {str(e)}")
            return False

    async def run_all_tests(self):
        """运行所有作业批改相关测试"""
        print("🚀 AI Tutor 作业批改功能测试")
        print("=" * 50)

        results = []

        # 基础功能测试
        results.append(await self.test_homework_subjects())
        results.append(await self.test_homework_health())

        # 核心功能测试
        results.append(await self.test_homework_grading())

        # 前端兼容性测试
        results.append(await self.test_frontend_compatibility())

        # 测试结果汇总
        print("\n📊 测试结果汇总:")
        print("=" * 50)

        passed = sum(results)
        total = len(results)

        print(f"总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {total - passed} ❌")
        print(f"成功率: {(passed/total*100):.1f}%")

        if passed == total:
            print("\n🎉 作业批改功能完全正常！前后端对接成功！")
            print("💡 建议:")
            print("   - 可以在前端测试作业上传和批改流程")
            print("   - 验证数据可视化功能")
            print("   - 测试不同科目的批改效果")
        elif passed >= total * 0.75:
            print(f"\n✅ 核心功能基本正常，{total - passed}个问题需要解决")
        else:
            print(f"\n⚠️  存在较多问题，需要检查后端配置")


async def main():
    """主函数"""
    print("正在连接后端服务...")

    async with HomeworkApiTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试执行出错: {e}")
