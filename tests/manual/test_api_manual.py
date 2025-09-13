"""
ProgressService API 手动测试脚本
用于手动测试学习进度管理API端点的功能
"""

import requests
import json
import sys
from datetime import datetime
import time


class APITester:
    """API测试器"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_server_health(self):
        """测试服务器健康状态"""
        print("🏥 测试服务器健康状态...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("  ✅ 服务器运行正常")
                return True
            else:
                print(f"  ❌ 服务器健康检查失败: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("  ❌ 无法连接到服务器，请确保服务器正在运行")
            print("  💡 请运行: make dev 或 uv run uvicorn src.ai_tutor.main:app --reload")
            return False
        except Exception as e:
            print(f"  ❌ 健康检查出错: {e}")
            return False

    def test_api_docs(self):
        """测试API文档可访问性"""
        print("\n📖 测试API文档...")
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("  ✅ API文档可访问")
                print(f"  🌐 访问地址: {self.base_url}/docs")
                return True
            else:
                print(f"  ❌ API文档访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ API文档测试出错: {e}")
            return False

    def test_progress_endpoints(self):
        """测试进度管理端点"""
        print("\n📊 测试学习进度管理端点...")

        student_id = 1
        subject = "math"

        # 测试获取科目学习进度
        print("  📈 测试获取科目学习进度...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/students/{student_id}/progress/{subject}",
                params={"timeframe_days": 30}
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ 成功获取科目进度")
                print(f"    📋 科目: {data.get('subject', 'N/A')}")
                print(f"    📊 掌握率: {data.get('mastery_rate', 0):.3f}")
                print(f"    📝 总题数: {data.get('total_questions', 0)}")
                print(f"    ✅ 正确题数: {data.get('correct_questions', 0)}")
                print(f"    📉 薄弱知识点数量: {len(data.get('weak_knowledge_points', []))}")
                return True
            elif response.status_code == 500:
                print(f"    ⚠️ 服务器内部错误（可能是数据库未连接）: {response.status_code}")
                try:
                    error_detail = response.json().get('detail', '未知错误')
                    print(f"    📝 错误详情: {error_detail}")
                except:
                    print(f"    📝 错误详情: {response.text}")
                return False
            else:
                print(f"    ❌ 获取科目进度失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"    ❌ 测试科目进度出错: {e}")
            return False

    def test_trends_endpoint(self):
        """测试学习趋势端点"""
        print("\n📈 测试学习趋势端点...")

        student_id = 1
        subject = "math"

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/students/{student_id}/progress/{subject}/trends",
                params={"days": 7}
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ 成功获取学习趋势")
                print(f"    📊 趋势数据点数量: {len(data)}")

                if data:
                    first_trend = data[0]
                    print(f"    📅 首个数据点日期: {first_trend.get('date', 'N/A')}")
                    print(f"    📊 首个数据点准确率: {first_trend.get('accuracy_rate', 0):.3f}")
                else:
                    print("    📋 暂无趋势数据")
                return True
            elif response.status_code == 500:
                print(f"    ⚠️ 服务器内部错误: {response.status_code}")
                return False
            else:
                print(f"    ❌ 获取学习趋势失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"    ❌ 测试学习趋势出错: {e}")
            return False

    def test_weak_points_endpoint(self):
        """测试薄弱知识点端点"""
        print("\n🎯 测试薄弱知识点端点...")

        student_id = 1
        subject = "math"

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/students/{student_id}/weak-points/{subject}"
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ 成功获取薄弱知识点")
                print(f"    🎯 学生ID: {data.get('student_id', 'N/A')}")
                print(f"    📚 科目: {data.get('subject', 'N/A')}")

                recommendations = data.get('recommendations', [])
                print(f"    💡 建议数量: {len(recommendations)}")

                if recommendations:
                    first_rec = recommendations[0]
                    print(f"    📝 首个建议知识点: {first_rec.get('knowledge_point', 'N/A')}")
                    print(f"    📊 当前掌握率: {first_rec.get('current_mastery', 0):.3f}")
                    print(f"    🔥 优先级: {first_rec.get('priority', 'N/A')}")
                else:
                    print("    🎉 没有薄弱知识点（或数据不足）")
                return True
            elif response.status_code == 500:
                print(f"    ⚠️ 服务器内部错误: {response.status_code}")
                return False
            else:
                print(f"    ❌ 获取薄弱知识点失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"    ❌ 测试薄弱知识点出错: {e}")
            return False

    def test_learning_patterns_endpoint(self):
        """测试学习模式分析端点"""
        print("\n🔄 测试学习模式分析端点...")

        student_id = 1

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/students/{student_id}/learning-patterns",
                params={"days": 30}
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ 成功获取学习模式")
                print(f"    👤 学生ID: {data.get('student_id', 'N/A')}")
                print(f"    📅 分析周期: {data.get('analysis_period_days', 'N/A')}天")

                patterns = data.get('patterns', {})
                if patterns:
                    print(f"    📊 学习一致性: {patterns.get('learning_consistency', 0):.3f}")
                    print(f"    ⏰ 最佳学习时间: {patterns.get('best_learning_hour', 'N/A')}点")
                    print(f"    📚 总学习天数: {patterns.get('total_study_days', 0)}")
                    print(f"    📈 日均学习次数: {patterns.get('avg_daily_sessions', 0):.2f}")
                else:
                    print("    📋 暂无学习模式数据")
                return True
            elif response.status_code == 500:
                print(f"    ⚠️ 服务器内部错误: {response.status_code}")
                return False
            else:
                print(f"    ❌ 获取学习模式失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"    ❌ 测试学习模式出错: {e}")
            return False

    def test_update_knowledge_progress_endpoint(self):
        """测试知识点进度更新端点"""
        print("\n🔄 测试知识点进度更新端点...")

        student_id = 1
        knowledge_point_id = 1

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/students/{student_id}/knowledge-progress/{knowledge_point_id}",
                params={
                    "is_correct": True,
                    "confidence_score": 0.85
                }
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ 成功更新知识点进度")
                print(f"    ✅ 操作成功: {data.get('success', False)}")
                print(f"    📝 消息: {data.get('message', 'N/A')}")
                print(f"    👤 学生ID: {data.get('student_id', 'N/A')}")
                print(f"    🎯 知识点ID: {data.get('knowledge_point_id', 'N/A')}")
                return True
            elif response.status_code == 500:
                print(f"    ⚠️ 服务器内部错误: {response.status_code}")
                return False
            else:
                print(f"    ❌ 更新知识点进度失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"    ❌ 测试知识点进度更新出错: {e}")
            return False

    def test_parameter_validation(self):
        """测试参数验证"""
        print("\n🔧 测试参数验证...")

        # 测试无效的时间范围参数
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/students/1/progress/math",
                params={"timeframe_days": -1}
            )

            if response.status_code == 422:
                print("    ✅ 负数时间范围参数验证正确")
            else:
                print(f"    ⚠️ 负数时间范围参数验证异常: {response.status_code}")
        except Exception as e:
            print(f"    ❌ 参数验证测试出错: {e}")

        # 测试超出范围的时间参数
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/students/1/progress/math",
                params={"timeframe_days": 400}
            )

            if response.status_code == 422:
                print("    ✅ 超范围时间参数验证正确")
            else:
                print(f"    ⚠️ 超范围时间参数验证异常: {response.status_code}")
        except Exception as e:
            print(f"    ❌ 超范围参数验证测试出错: {e}")

        # 测试无效的置信度参数
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/students/1/knowledge-progress/1",
                params={
                    "is_correct": True,
                    "confidence_score": 1.5  # 超出范围
                }
            )

            if response.status_code == 422:
                print("    ✅ 置信度参数验证正确")
            else:
                print(f"    ⚠️ 置信度参数验证异常: {response.status_code}")
        except Exception as e:
            print(f"    ❌ 置信度参数验证测试出错: {e}")


def main():
    """主测试函数"""
    print("🚀 开始ProgressService API手动测试...\n")

    tester = APITester()

    # 基础连接测试
    if not tester.test_server_health():
        print("\n❌ 服务器连接失败，无法继续测试")
        return False

    # API文档测试
    tester.test_api_docs()

    # 功能测试
    tests = [
        tester.test_progress_endpoints,
        tester.test_trends_endpoint,
        tester.test_weak_points_endpoint,
        tester.test_learning_patterns_endpoint,
        tester.test_update_knowledge_progress_endpoint,
        tester.test_parameter_validation
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"    ❌ 测试异常: {e}")

    print("\n" + "="*60)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")

    if passed_tests == total_tests:
        print("🎉 所有测试通过！ProgressService API功能正常！")
    elif passed_tests > 0:
        print("⚠️ 部分测试通过，可能存在数据库连接或数据问题")
        print("💡 建议检查数据库连接和测试数据准备情况")
    else:
        print("❌ 所有测试失败，请检查服务器状态和实现")

    print("="*60)

    # 提供使用指导
    print("\n📖 使用指导:")
    print("1. 确保服务器正在运行: make dev")
    print("2. 如果看到500错误，可能是数据库未连接或无测试数据")
    print("3. API文档地址: http://localhost:8000/docs")
    print("4. 可以通过API文档进行交互式测试")

    return passed_tests > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
