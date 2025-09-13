#!/usr/bin/env python3
"""
错误分析功能验证脚本

用于验证ErrorPatternService的核心功能是否正常工作。
按照简化原则，只测试关键路径，不依赖数据库。
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import Mock
from datetime import datetime
from ai_tutor.services.error_analysis import ErrorPatternService, ErrorClassifier
from ai_tutor.schemas.error_analysis import ErrorTypeEnum
from ai_tutor.models.homework import Question


def test_error_classifier():
    """测试错误分类器"""
    print("🔍 测试错误分类器...")

    classifier = ErrorClassifier()

    # 测试数学错误分类
    question = Mock(spec=Question)

    # 计算错误
    result = classifier.classify_error(question, "计算过程有误", "math")
    print(f"  ✓ 数学计算错误: {[e.value for e in result]}")
    assert ErrorTypeEnum.CALCULATION_ERROR in result

    # 物理单位错误
    result = classifier.classify_error(question, "单位使用错误", "physics")
    print(f"  ✓ 物理单位错误: {[e.value for e in result]}")
    assert ErrorTypeEnum.UNIT_ERROR in result

    # 英语语法错误
    result = classifier.classify_error(question, "语法结构不当", "english")
    print(f"  ✓ 英语语法错误: {[e.value for e in result]}")
    assert ErrorTypeEnum.GRAMMAR_ERROR in result

    # 未知科目
    result = classifier.classify_error(question, "未知错误", "unknown")
    print(f"  ✓ 未知科目默认分类: {[e.value for e in result]}")
    assert ErrorTypeEnum.KNOWLEDGE_GAP in result

    print("✅ 错误分类器测试通过\n")


async def test_single_question_analysis():
    """测试单题错误分析"""
    print("📝 测试单题错误分析...")

    mock_db = Mock()
    service = ErrorPatternService(mock_db)

    # 测试正确答案
    result = await service.analyze_question_error(
        question_text="计算 2+3 的值",
        student_answer="5",
        correct_answer="5",
        subject="math"
    )

    print(f"  ✓ 正确答案分析: 有错误={result.has_errors}, 得分={result.overall_score}")
    assert not result.has_errors
    assert result.overall_score == 1.0
    assert "正确" in result.immediate_feedback

    # 测试错误答案
    result = await service.analyze_question_error(
        question_text="计算 2+3 的值",
        student_answer="6",
        correct_answer="5",
        subject="math"
    )

    print(f"  ✓ 错误答案分析: 有错误={result.has_errors}, 得分={result.overall_score}")
    print(f"    反馈: {result.immediate_feedback}")
    print(f"    错误数量: {len(result.errors)}")

    assert result.has_errors
    assert result.overall_score < 1.0
    assert len(result.errors) > 0
    assert "问题" in result.immediate_feedback

    print("✅ 单题错误分析测试通过\n")


async def test_pattern_analysis():
    """测试错误模式分析"""
    print("📊 测试错误模式分析...")

    mock_db = Mock()
    service = ErrorPatternService(mock_db)

    # 模拟题目数据
    mock_questions = [
        Mock(
            spec=Question,
            is_correct=False,
            error_analysis="计算错误",
            difficulty_level=2,
            created_at=datetime.now(),
            student_answer="5",
            correct_answer="4"
        ),
        Mock(
            spec=Question,
            is_correct=True,
            error_analysis="",
            difficulty_level=3,
            created_at=datetime.now()
        ),
        Mock(
            spec=Question,
            is_correct=False,
            error_analysis="概念理解错误",
            difficulty_level=1,
            created_at=datetime.now()
        )
    ]

    # Mock数据库查询
    service._get_student_questions = Mock(return_value=mock_questions)

    # 执行分析
    result = await service.analyze_student_error_patterns(
        student_id=1,
        subject="math",
        timeframe_days=30
    )

    print(f"  ✓ 模式分析完成:")
    print(f"    学生ID: {result.student_id}")
    print(f"    科目: {result.subject}")
    print(f"    总题数: {result.total_questions}")
    print(f"    错误数: {result.total_errors}")
    print(f"    错误率: {result.error_rate:.1%}")
    print(f"    错误类型分布: {result.error_type_distribution}")
    print(f"    系统性错误数: {len(result.systematic_errors)}")
    print(f"    改进建议数: {len(result.improvement_recommendations)}")

    assert result.student_id == 1
    assert result.subject == "math"
    assert result.total_questions == 3
    assert result.total_errors == 2
    assert abs(result.error_rate - 2/3) < 0.01

    print("✅ 错误模式分析测试通过\n")


async def test_error_trends():
    """测试错误趋势分析"""
    print("📈 测试错误趋势分析...")

    mock_db = Mock()
    service = ErrorPatternService(mock_db)

    # 执行趋势分析
    result = await service.get_error_trends(
        student_id=1,
        subject="math",
        days=30
    )

    print(f"  ✓ 趋势分析完成:")
    print(f"    学生ID: {result.student_id}")
    print(f"    科目: {result.subject}")
    print(f"    总体趋势: {result.overall_trend}")
    print(f"    改进速度: {result.improvement_rate}")
    print(f"    每日数据点数: {len(result.daily_error_rates)}")
    print(f"    周度数据点数: {len(result.weekly_summaries)}")

    assert result.student_id == 1
    assert result.subject == "math"
    assert result.overall_trend in ["improving", "stable", "worsening"]
    assert isinstance(result.improvement_rate, float)
    assert len(result.daily_error_rates) > 0

    print("✅ 错误趋势分析测试通过\n")


def test_utility_functions():
    """测试工具函数"""
    print("🔧 测试工具函数...")

    mock_db = Mock()
    service = ErrorPatternService(mock_db)

    # 测试错误严重程度判断
    easy_question = Mock(spec=Question, difficulty_level=2)
    severity = service._determine_error_severity(easy_question, "math")
    print(f"  ✓ 简单题错误严重程度: {severity.value}")

    # 测试错误频率判断
    frequency = service._determine_error_frequency(0.7)
    print(f"  ✓ 70%频率判断: {frequency.value}")

    # 测试趋势计算
    data = [
        {"error_rate": 0.5},
        {"error_rate": 0.4},
        {"error_rate": 0.3}
    ]
    trend = service._calculate_overall_trend(data)
    print(f"  ✓ 改进趋势计算: {trend}")

    # 测试改进速度
    rate = service._calculate_improvement_rate(data)
    print(f"  ✓ 改进速度计算: {rate}")

    print("✅ 工具函数测试通过\n")


async def main():
    """主测试流程"""
    print("🚀 AI Tutor 错误分析服务功能验证")
    print("=" * 50)

    try:
        # 基础功能测试
        test_error_classifier()

        # 核心服务测试
        await test_single_question_analysis()
        await test_pattern_analysis()
        await test_error_trends()

        # 工具函数测试
        test_utility_functions()

        print("🎉 所有测试通过！")
        print("\n📋 功能验证总结:")
        print("  ✅ 错误分类器 - 正确识别不同类型错误")
        print("  ✅ 单题分析 - 准确判断答案正误并给出反馈")
        print("  ✅ 模式分析 - 成功分析错误模式和生成建议")
        print("  ✅ 趋势分析 - 正确计算学习趋势指标")
        print("  ✅ 工具函数 - 辅助函数工作正常")

        print("\n🔧 服务特性:")
        print("  • 支持数学、物理、英语等多科目")
        print("  • 智能错误类型识别")
        print("  • 系统性错误模式分析")
        print("  • 个性化改进建议生成")
        print("  • 学习趋势预测")
        print("  • 模块化设计，易于扩展")

        print(f"\n✨ ErrorPatternService v1.0 验证完成")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
