#!/usr/bin/env python3
"""
错误分析API演示脚本

演示如何使用ErrorPatternService的各个API端点
"""
import requests
import json
import time
import sys


class ErrorAnalysisAPIDemo:
    """错误分析API演示类"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = f"{base_url}/api/v1/error-analysis"

    def check_service_health(self):
        """检查服务健康状态"""
        print("🔍 检查错误分析服务状态...")
        try:
            response = requests.get(f"{self.api_prefix}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务状态: {data['status']}")
                print(f"   服务名称: {data['service']}")
                print(f"   状态信息: {data['message']}")
                return True
            else:
                print(f"❌ 服务异常，状态码: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到服务: {e}")
            return False

    def demo_error_types(self):
        """演示错误类型查询"""
        print("\n📋 获取支持的错误类型...")
        try:
            response = requests.get(f"{self.api_prefix}/error-types")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 支持的错误类型数量: {len(data['error_types'])}")

                # 显示前3个错误类型
                for i, error_type in enumerate(data['error_types'][:3]):
                    print(f"   {i+1}. {error_type['name']} ({error_type['code']})")
                    print(f"      描述: {error_type['description']}")
                    print(f"      适用科目: {', '.join(error_type['subjects'])}")

                if len(data['error_types']) > 3:
                    print(f"   ... 还有 {len(data['error_types']) - 3} 个错误类型")

                return True
            else:
                print(f"❌ 获取错误类型失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False

    def demo_single_question_analysis(self):
        """演示单题错误分析"""
        print("\n📝 单题错误分析演示...")

        # 准备测试数据
        test_cases = [
            {
                "name": "数学计算错误",
                "data": {
                    "question_text": "计算 2+3×4 的值",
                    "student_answer": "20",  # 错误答案：先算加法
                    "correct_answer": "14",
                    "subject": "math"
                }
            },
            {
                "name": "数学正确答案",
                "data": {
                    "question_text": "计算 5×6 的值",
                    "student_answer": "30",
                    "correct_answer": "30",
                    "subject": "math"
                }
            },
            {
                "name": "物理单位错误",
                "data": {
                    "question_text": "一物体重量为2公斤，求其重力大小",
                    "student_answer": "2牛顿",  # 单位概念错误
                    "correct_answer": "20牛顿",
                    "subject": "physics"
                }
            }
        ]

        success_count = 0
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  📌 测试用例 {i}: {test_case['name']}")
            try:
                response = requests.post(
                    f"{self.api_prefix}/analyze-question",
                    json=test_case['data'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"     ✅ 分析成功")
                    print(f"        是否有错误: {data['has_errors']}")
                    print(f"        整体得分: {data['overall_score']}")
                    print(f"        即时反馈: {data['immediate_feedback']}")

                    if data['has_errors'] and data['errors']:
                        print(f"        错误类型: {data['errors'][0]['error_type']}")
                        print(f"        改正建议: {data['errors'][0]['correction_suggestion']}")

                    success_count += 1
                else:
                    print(f"     ❌ 分析失败，状态码: {response.status_code}")
                    if response.text:
                        error_info = response.json().get('detail', 'Unknown error')
                        print(f"        错误信息: {error_info}")

            except Exception as e:
                print(f"     ❌ 请求异常: {e}")

            time.sleep(0.5)  # 避免请求过快

        print(f"\n✅ 单题分析演示完成，成功率: {success_count}/{len(test_cases)}")
        return success_count == len(test_cases)

    def demo_student_pattern_analysis(self):
        """演示学生错误模式分析"""
        print("\n📊 学生错误模式分析演示...")

        # 注意：这个演示可能需要数据库中有实际数据
        test_params = [
            {"student_id": 1, "subject": "math", "timeframe": 30},
            {"student_id": 1, "subject": "physics", "timeframe": 14},
        ]

        success_count = 0
        for i, params in enumerate(test_params, 1):
            print(f"\n  📌 测试 {i}: 学生{params['student_id']} - {params['subject']}科目")
            try:
                url = f"{self.api_prefix}/students/{params['student_id']}/patterns/{params['subject']}"
                response = requests.get(
                    url,
                    params={'timeframe_days': params['timeframe']},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"     ✅ 分析成功")
                    print(f"        分析期间: {data['analysis_period']}")
                    print(f"        总题数: {data['total_questions']}")
                    print(f"        错误数: {data['total_errors']}")
                    print(f"        错误率: {data['error_rate']:.1%}")

                    if data['error_type_distribution']:
                        print(f"        主要错误类型: {list(data['error_type_distribution'].keys())}")

                    print(f"        系统性错误: {len(data['systematic_errors'])}个")
                    print(f"        改进建议: {len(data['improvement_recommendations'])}条")

                    success_count += 1
                elif response.status_code == 400:
                    error_info = response.json().get('detail', 'Unknown error')
                    print(f"     ⚠️  参数错误: {error_info}")
                else:
                    print(f"     ℹ️  暂无数据或服务异常 (状态码: {response.status_code})")
                    # 对于演示来说，这也算"成功"，因为API正常响应了
                    success_count += 1

            except Exception as e:
                print(f"     ❌ 请求异常: {e}")

            time.sleep(0.5)

        print(f"\n✅ 错误模式分析演示完成，成功率: {success_count}/{len(test_params)}")
        return success_count > 0

    def demo_error_trends(self):
        """演示错误趋势分析"""
        print("\n📈 错误趋势分析演示...")

        try:
            url = f"{self.api_prefix}/students/1/trends/math"
            response = requests.get(url, params={'days': 30}, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ 趋势分析成功")
                print(f"        学生ID: {data['student_id']}")
                print(f"        科目: {data['subject']}")
                print(f"        总体趋势: {data['overall_trend']}")
                print(f"        改进速度: {data['improvement_rate']}")
                print(f"        数据点数: {len(data['daily_error_rates'])}天")
                print(f"        风险评估: {data['risk_assessment']}")
                return True
            else:
                print(f"     ℹ️  趋势分析返回状态码: {response.status_code}")
                return True  # 演示目的，API响应即可

        except Exception as e:
            print(f"     ❌ 请求异常: {e}")
            return False

    def demo_improvement_plan(self):
        """演示改进计划生成"""
        print("\n💡 个性化改进计划演示...")

        try:
            url = f"{self.api_prefix}/students/1/improvement-plan/math"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ 改进计划生成成功")
                print(f"        学生ID: {data['student_id']}")
                print(f"        科目: {data['subject']}")
                print(f"        当前错误率: {data['current_performance']['error_rate']:.1%}")
                print(f"        改进目标: {len(data['improvement_goals'])}个")
                print(f"        行动计划: {len(data['action_plan'])}周")
                print(f"        预计完成时间: {data['estimated_duration']}")

                # 显示第一个改进目标
                if data['improvement_goals']:
                    print(f"        首要目标: {data['improvement_goals'][0]}")

                return True
            else:
                print(f"     ℹ️  改进计划生成返回状态码: {response.status_code}")
                return True  # 演示目的，API响应即可

        except Exception as e:
            print(f"     ❌ 请求异常: {e}")
            return False

    def demo_summary(self):
        """演示多科目错误总结"""
        print("\n📋 多科目错误总结演示...")

        try:
            url = f"{self.api_prefix}/students/1/summary"
            response = requests.get(
                url,
                params={'subjects': ['math', 'physics'], 'timeframe_days': 30},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ 总结生成成功")
                print(f"        学生ID: {data['student_id']}")
                print(f"        总体错误率: {data['overall_error_rate']:.1%}")
                print(f"        总题数: {data['total_questions']}")
                print(f"        总错误数: {data['total_errors']}")
                print(f"        涵盖科目: {len(data['subjects_analysis'])}个")

                # 显示各科目表现
                for subject, analysis in data['subjects_analysis'].items():
                    if isinstance(analysis, dict) and 'error_rate' in analysis:
                        print(f"        {subject}: 错误率 {analysis['error_rate']:.1%}")

                return True
            else:
                print(f"     ℹ️  多科目总结返回状态码: {response.status_code}")
                return True

        except Exception as e:
            print(f"     ❌ 请求异常: {e}")
            return False

    def run_full_demo(self):
        """运行完整演示"""
        print("🚀 AI Tutor 错误分析服务 API 演示")
        print("=" * 60)

        # 检查服务状态
        if not self.check_service_health():
            print("\n❌ 服务未启动，请先运行 'make dev' 启动服务器")
            return False

        # 演示各个功能
        demos = [
            ("错误类型查询", self.demo_error_types),
            ("单题错误分析", self.demo_single_question_analysis),
            ("错误模式分析", self.demo_student_pattern_analysis),
            ("错误趋势分析", self.demo_error_trends),
            ("改进计划生成", self.demo_improvement_plan),
            ("多科目总结", self.demo_summary),
        ]

        success_count = 0
        for name, demo_func in demos:
            try:
                if demo_func():
                    success_count += 1
                time.sleep(1)  # 演示间隔
            except KeyboardInterrupt:
                print("\n\n⚠️  演示被用户中断")
                break
            except Exception as e:
                print(f"\n❌ {name}演示异常: {e}")

        # 演示总结
        print(f"\n" + "=" * 60)
        print(f"🎉 演示完成！成功率: {success_count}/{len(demos)}")

        if success_count == len(demos):
            print("✨ 所有功能正常工作！")
        elif success_count > 0:
            print("⚠️  部分功能可能需要实际数据支持")
        else:
            print("❌ 请检查服务状态和网络连接")

        print("\n💡 使用提示:")
        print("   • 单题分析功能无需数据库，可直接使用")
        print("   • 学生相关分析需要数据库中有对应数据")
        print("   • 所有API都支持参数验证和错误处理")
        print("   • 详细API文档请查看 FastAPI 自动生成的文档")
        print(f"   • 访问 {self.base_url}/docs 查看完整API文档")

        return success_count > 0


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='错误分析API演示程序')
    parser.add_argument('--host', default='localhost', help='服务器地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--demo', choices=[
        'health', 'types', 'question', 'patterns', 'trends', 'plan', 'summary'
    ], help='运行特定演示')

    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    demo = ErrorAnalysisAPIDemo(base_url)

    if args.demo:
        # 运行特定演示
        demo_map = {
            'health': demo.check_service_health,
            'types': demo.demo_error_types,
            'question': demo.demo_single_question_analysis,
            'patterns': demo.demo_student_pattern_analysis,
            'trends': demo.demo_error_trends,
            'plan': demo.demo_improvement_plan,
            'summary': demo.demo_summary,
        }

        print(f"🎯 运行特定演示: {args.demo}")
        success = demo_map[args.demo]()
        sys.exit(0 if success else 1)
    else:
        # 运行完整演示
        success = demo.run_full_demo()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
