"""
ProgressAlgorithm 核心算法验证测试
独立测试学习进度计算算法，不依赖其他模块
"""

import sys
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
from statistics import mean, stdev


class ProgressAlgorithm:
    """进度计算核心算法"""

    # 权重配置
    RECENT_WEIGHT = 0.6      # 近期表现权重
    HISTORICAL_WEIGHT = 0.4   # 历史表现权重
    CONFIDENCE_THRESHOLD = 0.75  # 掌握程度阈值
    MIN_ATTEMPTS_FOR_CONFIDENCE = 3  # 最小练习次数要求

    @classmethod
    def calculate_mastery_rate(
        cls,
        correct_answers: int,
        total_answers: int,
        recent_accuracy: float,
        time_decay_factor: float = 0.95
    ) -> float:
        """
        计算知识点掌握率
        """
        if total_answers == 0:
            return 0.0

        # 历史准确率
        historical_accuracy = correct_answers / total_answers

        # 综合计算：近期表现 + 历史表现
        mastery_rate = (
            recent_accuracy * cls.RECENT_WEIGHT +
            historical_accuracy * cls.HISTORICAL_WEIGHT
        ) * time_decay_factor

        return min(1.0, max(0.0, mastery_rate))

    @classmethod
    def identify_weak_points(
        cls,
        knowledge_progresses: List[Dict],
        threshold: float = 0.6
    ) -> List[str]:
        """
        识别薄弱知识点
        """
        weak_points = []

        for progress in knowledge_progresses:
            mastery_level = progress.get('mastery_level', 0.0)
            total_attempts = progress.get('total_attempts', 0)
            knowledge_point_name = progress.get('knowledge_point_name', '')

            # 判断条件：掌握率低于阈值 且 有足够的练习次数
            if (mastery_level < threshold and
                total_attempts >= cls.MIN_ATTEMPTS_FOR_CONFIDENCE):
                weak_points.append(knowledge_point_name)

        return weak_points

    @classmethod
    def calculate_learning_velocity(
        cls,
        progress_history: List[Tuple[datetime, float]],
        days_window: int = 14
    ) -> float:
        """
        计算学习速度（进步速率）
        """
        if len(progress_history) < 2:
            return 0.0

        # 按时间排序
        sorted_history = sorted(progress_history, key=lambda x: x[0])

        # 取最近的数据点
        cutoff_time = datetime.now() - timedelta(days=days_window)
        recent_history = [
            (time, rate) for time, rate in sorted_history
            if time >= cutoff_time
        ]

        if len(recent_history) < 2:
            recent_history = sorted_history[-2:]  # 至少取最后两个点

        # 计算线性回归斜率
        n = len(recent_history)
        x_values = [(h[0] - recent_history[0][0]).days for h in recent_history]
        y_values = [h[1] for h in recent_history]

        if len(set(x_values)) == 1:  # 避免除零错误
            return 0.0

        # 简单线性回归
        x_mean = mean(x_values)
        y_mean = mean(y_values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    @classmethod
    def predict_mastery_time(
        cls,
        current_mastery: float,
        target_mastery: float,
        learning_velocity: float
    ) -> int:
        """
        预测达到目标掌握率需要的天数
        """
        if learning_velocity <= 0 or current_mastery >= target_mastery:
            return None

        days_needed = (target_mastery - current_mastery) / learning_velocity
        return max(1, int(days_needed))


def test_calculate_mastery_rate():
    """测试掌握率计算"""
    print("🧮 测试掌握率计算...")

    # 基础测试
    mastery_rate = ProgressAlgorithm.calculate_mastery_rate(
        correct_answers=8,
        total_answers=10,
        recent_accuracy=0.9,
        time_decay_factor=1.0
    )

    expected = 0.86  # 0.9 * 0.6 + 0.8 * 0.4
    assert abs(mastery_rate - expected) < 0.01, f"掌握率计算错误: 期望 {expected}, 实际 {mastery_rate}"
    print(f"  ✅ 基础掌握率计算正确: {mastery_rate:.3f}")

    # 带衰减测试
    mastery_rate_decay = ProgressAlgorithm.calculate_mastery_rate(
        correct_answers=7,
        total_answers=10,
        recent_accuracy=0.8,
        time_decay_factor=0.9
    )

    expected_decay = 0.684  # (0.8 * 0.6 + 0.7 * 0.4) * 0.9
    assert abs(mastery_rate_decay - expected_decay) < 0.01
    print(f"  ✅ 衰减掌握率计算正确: {mastery_rate_decay:.3f}")

    # 无数据测试
    mastery_rate_zero = ProgressAlgorithm.calculate_mastery_rate(
        correct_answers=0,
        total_answers=0,
        recent_accuracy=0.0
    )
    assert mastery_rate_zero == 0.0
    print(f"  ✅ 无数据情况处理正确: {mastery_rate_zero}")


def test_identify_weak_points():
    """测试薄弱知识点识别"""
    print("\n🎯 测试薄弱知识点识别...")

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
        },
        {
            'knowledge_point_name': '平面几何',
            'mastery_level': 0.3,
            'total_attempts': 2  # 练习次数不足
        }
    ]

    weak_points = ProgressAlgorithm.identify_weak_points(knowledge_progresses, threshold=0.6)

    expected_weak = ['一元一次方程', '因式分解']
    assert set(weak_points) == set(expected_weak), f"薄弱知识点识别错误: {weak_points}"
    print(f"  ✅ 薄弱知识点识别正确: {weak_points}")


def test_calculate_learning_velocity():
    """测试学习速度计算"""
    print("\n📈 测试学习速度计算...")

    base_time = datetime(2024, 1, 1)
    progress_history = [
        (base_time, 0.3),
        (base_time + timedelta(days=7), 0.5),
        (base_time + timedelta(days=14), 0.7),
    ]

    velocity = ProgressAlgorithm.calculate_learning_velocity(progress_history, days_window=14)
    assert velocity > 0.02, f"学习速度应该为正且合理: {velocity}"
    assert velocity < 0.04, f"学习速度不应过高: {velocity}"
    print(f"  ✅ 学习速度计算正确: {velocity:.4f}/天")

    # 无数据测试
    velocity_empty = ProgressAlgorithm.calculate_learning_velocity([], days_window=14)
    assert velocity_empty == 0.0
    print(f"  ✅ 无数据情况处理正确: {velocity_empty}")

    # 单点数据测试
    velocity_single = ProgressAlgorithm.calculate_learning_velocity([(base_time, 0.5)], days_window=14)
    assert velocity_single == 0.0
    print(f"  ✅ 单点数据情况处理正确: {velocity_single}")


def test_predict_mastery_time():
    """测试掌握时间预测"""
    print("\n⏰ 测试掌握时间预测...")

    # 正常预测
    days = ProgressAlgorithm.predict_mastery_time(
        current_mastery=0.4,
        target_mastery=0.8,
        learning_velocity=0.02
    )
    expected_days = 20  # (0.8 - 0.4) / 0.02 = 20
    assert days == expected_days, f"掌握时间预测错误: 期望 {expected_days}, 实际 {days}"
    print(f"  ✅ 正常掌握时间预测正确: {days}天")

    # 已掌握情况
    days_mastered = ProgressAlgorithm.predict_mastery_time(
        current_mastery=0.9,
        target_mastery=0.8,
        learning_velocity=0.02
    )
    assert days_mastered is None, "已掌握情况应返回None"
    print(f"  ✅ 已掌握情况处理正确: {days_mastered}")

    # 无进步情况
    days_no_progress = ProgressAlgorithm.predict_mastery_time(
        current_mastery=0.4,
        target_mastery=0.8,
        learning_velocity=0.0
    )
    assert days_no_progress is None, "无进步情况应返回None"
    print(f"  ✅ 无进步情况处理正确: {days_no_progress}")


def test_algorithm_integration():
    """测试算法集成使用"""
    print("\n🔄 测试算法集成使用...")

    # 模拟学生学习过程
    student_data = {
        'correct_answers': 15,
        'total_answers': 20,
        'recent_accuracy': 0.85,
        'knowledge_points': [
            {'knowledge_point_name': '方程求解', 'mastery_level': 0.4, 'total_attempts': 6},
            {'knowledge_point_name': '函数图像', 'mastery_level': 0.9, 'total_attempts': 5},
            {'knowledge_point_name': '几何证明', 'mastery_level': 0.55, 'total_attempts': 4},
        ]
    }

    # 1. 计算整体掌握率
    overall_mastery = ProgressAlgorithm.calculate_mastery_rate(
        correct_answers=student_data['correct_answers'],
        total_answers=student_data['total_answers'],
        recent_accuracy=student_data['recent_accuracy']
    )
    print(f"  📊 整体掌握率: {overall_mastery:.3f}")

    # 2. 识别薄弱知识点
    weak_points = ProgressAlgorithm.identify_weak_points(student_data['knowledge_points'])
    print(f"  🎯 薄弱知识点: {weak_points}")

    # 3. 计算学习速度
    base_time = datetime.now() - timedelta(days=21)
    progress_history = [
        (base_time, 0.5),
        (base_time + timedelta(days=7), 0.65),
        (base_time + timedelta(days=14), 0.75),
        (base_time + timedelta(days=21), overall_mastery),
    ]

    velocity = ProgressAlgorithm.calculate_learning_velocity(progress_history)
    print(f"  📈 学习速度: {velocity:.4f}/天")

    # 4. 预测薄弱点掌握时间
    if weak_points and velocity > 0:
        # 找到最薄弱的知识点
        weakest_point = min(student_data['knowledge_points'],
                          key=lambda x: x['mastery_level'])

        mastery_days = ProgressAlgorithm.predict_mastery_time(
            current_mastery=weakest_point['mastery_level'],
            target_mastery=0.75,
            learning_velocity=velocity
        )
        print(f"  ⏰ '{weakest_point['knowledge_point_name']}'预计掌握时间: {mastery_days}天")

    print("  ✅ 算法集成测试通过")


def main():
    """运行所有算法测试"""
    print("🚀 开始ProgressAlgorithm核心算法验证测试...\n")

    try:
        test_calculate_mastery_rate()
        test_identify_weak_points()
        test_calculate_learning_velocity()
        test_predict_mastery_time()
        test_algorithm_integration()

        print("\n" + "="*60)
        print("🎉 所有测试通过！ProgressAlgorithm核心算法验证成功！")
        print("="*60)

        # 输出算法配置信息
        print(f"\n📊 算法配置:")
        print(f"  - 近期权重: {ProgressAlgorithm.RECENT_WEIGHT}")
        print(f"  - 历史权重: {ProgressAlgorithm.HISTORICAL_WEIGHT}")
        print(f"  - 掌握阈值: {ProgressAlgorithm.CONFIDENCE_THRESHOLD}")
        print(f"  - 最小练习次数: {ProgressAlgorithm.MIN_ATTEMPTS_FOR_CONFIDENCE}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
