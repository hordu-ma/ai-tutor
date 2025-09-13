"""
ProgressService 功能验证测试
用于验证学习进度管理服务的核心功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from ai_tutor.services.student.progress_service import ProgressService, ProgressAlgorithm
from ai_tutor.schemas.student_schemas import SubjectProgress
from datetime import datetime, timedelta


def test_progress_algorithm_basic():
    """测试进度算法基本功能"""
    print("🧮 测试进度计算算法...")

    # 测试掌握率计算
    mastery_rate = ProgressAlgorithm.calculate_mastery_rate(
        correct_answers=8,
        total_answers=10,
        recent_accuracy=0.9,
        time_decay_factor=1.0
    )

    expected = 0.86  # 0.9 * 0.6 + 0.8 * 0.4
    assert abs(mastery_rate - expected) < 0.01, f"掌握率计算错误: 期望 {expected}, 实际 {mastery_rate}"
    print(f"  ✅ 掌握率计算正确: {mastery_rate:.3f}")

    # 测试薄弱知识点识别
    knowledge_progresses = [
        {
            'knowledge_point_name': '一元一次方程',
            'mastery_level': 0.4,
            'total_attempts': 5
        },
        {
            'knowledge_point_name': '二次函数',
            'mastery_level': 0.8,
            'total_attempts': 6
        },
        {
            'knowledge_point_name': '因式分解',
            'mastery_level': 0.5,
            'total_attempts': 4
        }
    ]

    weak_points = ProgressAlgorithm.identify_weak_points(knowledge_progresses, threshold=0.6)
    expected_weak = ['一元一次方程', '因式分解']
    assert set(weak_points) == set(expected_weak), f"薄弱知识点识别错误: {weak_points}"
    print(f"  ✅ 薄弱知识点识别正确: {weak_points}")

    # 测试学习速度计算
    base_time = datetime(2024, 1, 1)
    progress_history = [
        (base_time, 0.3),
        (base_time + timedelta(days=7), 0.5),
        (base_time + timedelta(days=14), 0.7),
    ]

    velocity = ProgressAlgorithm.calculate_learning_velocity(progress_history, days_window=14)
    assert velocity > 0.02, f"学习速度应该为正: {velocity}"
    print(f"  ✅ 学习速度计算正确: {velocity:.4f}/天")

    # 测试掌握时间预测
    days = ProgressAlgorithm.predict_mastery_time(
        current_mastery=0.4,
        target_mastery=0.8,
        learning_velocity=0.02
    )
    expected_days = 20  # (0.8 - 0.4) / 0.02 = 20
    assert days == expected_days, f"掌握时间预测错误: 期望 {expected_days}, 实际 {days}"
    print(f"  ✅ 掌握时间预测正确: {days}天")


def test_progress_service_initialization():
    """测试进度服务初始化"""
    print("\n🏗️  测试ProgressService初始化...")

    service = ProgressService()
    assert service is not None, "ProgressService实例化失败"
    assert hasattr(service, 'algorithm'), "ProgressService缺少算法组件"
    assert isinstance(service.algorithm, ProgressAlgorithm), "算法组件类型错误"

    print("  ✅ ProgressService初始化成功")


def test_progress_service_helper_methods():
    """测试进度服务辅助方法"""
    print("\n🔧 测试ProgressService辅助方法...")

    service = ProgressService()

    # 测试练习时间估算
    from unittest.mock import Mock
    mock_progress = Mock()
    mock_progress.mastery_level = 0.4

    estimated_time = service._estimate_practice_time(mock_progress)
    expected_time = 30 * (1 + (1 - 0.4) * 2)  # 30 * 2.2 = 66
    assert estimated_time == expected_time, f"练习时间估算错误: 期望 {expected_time}, 实际 {estimated_time}"
    print(f"  ✅ 练习时间估算正确: {estimated_time}分钟")

    # 测试改进策略生成
    mock_knowledge_point = Mock()
    mock_knowledge_point.name = "一元一次方程"

    mock_progress_low = Mock()
    mock_progress_low.mastery_level = 0.2

    strategies = service._generate_improvement_strategies(
        mock_knowledge_point, mock_progress_low, {}
    )

    assert isinstance(strategies, list), "改进策略应该是列表"
    assert len(strategies) > 0, "应该生成改进策略"
    assert any("基础概念" in strategy for strategy in strategies), "应该包含基础概念相关建议"
    print(f"  ✅ 改进策略生成正确: {len(strategies)}条建议")

    # 测试掌握时间线估算
    mock_progress_medium = Mock()
    mock_progress_medium.mastery_level = 0.5

    timeline = service._estimate_mastery_timeline(mock_progress_medium)
    expected_timeline = int((0.75 - 0.5) / 0.05)  # 5天
    assert timeline == expected_timeline, f"时间线估算错误: 期望 {expected_timeline}, 实际 {timeline}"
    print(f"  ✅ 掌握时间线估算正确: {timeline}天")


def test_subject_progress_schema():
    """测试SubjectProgress数据模型"""
    print("\n📊 测试SubjectProgress数据模型...")

    # 创建有效的进度数据
    progress = SubjectProgress(
        subject="math",
        mastery_rate=0.85,
        total_questions=20,
        correct_questions=17,
        recent_performance=0.9,
        weak_knowledge_points=["一元一次方程", "因式分解"]
    )

    assert progress.subject == "math"
    assert progress.mastery_rate == 0.85
    assert progress.total_questions == 20
    assert progress.correct_questions == 17
    assert progress.recent_performance == 0.9
    assert len(progress.weak_knowledge_points) == 2

    print("  ✅ SubjectProgress模型验证通过")

    # 测试数据验证
    try:
        invalid_progress = SubjectProgress(
            subject="math",
            mastery_rate=1.5,  # 超出范围
            total_questions=-1,  # 负数
            correct_questions=25,  # 超过总数
            recent_performance=-0.1  # 负数
        )
        assert False, "应该触发验证错误"
    except Exception as e:
        print(f"  ✅ 数据验证正确触发: {type(e).__name__}")


def test_error_handling():
    """测试错误处理"""
    print("\n⚠️  测试错误处理...")

    # 测试算法边界情况
    mastery_rate = ProgressAlgorithm.calculate_mastery_rate(
        correct_answers=0,
        total_answers=0,
        recent_accuracy=0.0
    )
    assert mastery_rate == 0.0, "无数据时应返回0.0"
    print("  ✅ 无数据边界情况处理正确")

    # 测试学习速度计算边界情况
    velocity = ProgressAlgorithm.calculate_learning_velocity([], days_window=14)
    assert velocity == 0.0, "无历史数据时应返回0.0"
    print("  ✅ 无历史数据边界情况处理正确")

    # 测试掌握时间预测边界情况
    days = ProgressAlgorithm.predict_mastery_time(
        current_mastery=0.9,
        target_mastery=0.8,
        learning_velocity=0.02
    )
    assert days is None, "已掌握情况应返回None"
    print("  ✅ 已掌握边界情况处理正确")


def test_integration_workflow():
    """测试集成工作流"""
    print("\n🔄 测试集成工作流...")

    service = ProgressService()

    # 模拟完整的学习进度更新流程
    print("  📝 模拟学习进度计算流程...")

    # 1. 创建模拟数据
    student_id = 1
    subject = "math"

    # 2. 测试算法组合使用
    knowledge_data = [
        {'knowledge_point_name': '方程求解', 'mastery_level': 0.3, 'total_attempts': 5},
        {'knowledge_point_name': '函数图像', 'mastery_level': 0.8, 'total_attempts': 4},
    ]

    weak_points = service.algorithm.identify_weak_points(knowledge_data, threshold=0.6)
    assert len(weak_points) == 1, "应该识别出1个薄弱知识点"
    assert weak_points[0] == '方程求解', "应该识别出方程求解为薄弱点"

    # 3. 测试改进建议生成
    from unittest.mock import Mock
    mock_kp = Mock()
    mock_kp.name = weak_points[0]

    mock_progress = Mock()
    mock_progress.mastery_level = 0.3
    mock_progress.common_errors = {"calculation_error": 2}

    strategies = service._generate_improvement_strategies(mock_kp, mock_progress, {"calculation_error": 2})
    assert len(strategies) > 0, "应该生成改进策略"

    print("  ✅ 集成工作流测试通过")


def main():
    """运行所有验证测试"""
    print("🚀 开始ProgressService功能验证测试...\n")

    try:
        test_progress_algorithm_basic()
        test_progress_service_initialization()
        test_progress_service_helper_methods()
        test_subject_progress_schema()
        test_error_handling()
        test_integration_workflow()

        print("\n" + "="*50)
        print("🎉 所有测试通过！ProgressService功能验证成功！")
        print("="*50)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
