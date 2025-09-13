"""
错误分析服务测试 - 简化版本
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from ai_tutor.services.error_analysis import ErrorPatternService, ErrorClassifier
from ai_tutor.schemas.error_analysis import (
    ErrorTypeEnum,
    SeverityLevel,
    ErrorFrequency
)
from ai_tutor.models.homework import Question, HomeworkSession


class TestErrorClassifier:
    """错误分类器测试"""

    def setup_method(self):
        self.classifier = ErrorClassifier()

    def test_classify_math_error_calculation(self):
        """测试数学计算错误分类"""
        question = Mock(spec=Question)
        error_text = "计算过程中出现错误"

        result = self.classifier.classify_error(question, error_text, "math")

        assert ErrorTypeEnum.CALCULATION_ERROR in result

    def test_classify_physics_error_unit(self):
        """测试物理单位错误分类"""
        question = Mock(spec=Question)
        error_text = "单位使用错误"

        result = self.classifier.classify_error(question, error_text, "physics")

        assert ErrorTypeEnum.UNIT_ERROR in result

    def test_classify_english_error_grammar(self):
        """测试英语语法错误分类"""
        question = Mock(spec=Question)
        error_text = "语法结构错误"

        result = self.classifier.classify_error(question, error_text, "english")

        assert ErrorTypeEnum.GRAMMAR_ERROR in result

    def test_default_classification(self):
        """测试默认分类"""
        question = Mock(spec=Question)
        error_text = "未知错误"

        result = self.classifier.classify_error(question, error_text, "unknown")

        assert ErrorTypeEnum.KNOWLEDGE_GAP in result


class TestErrorPatternService:
    """错误模式分析服务测试"""

    def setup_method(self):
        self.mock_db = Mock()
        self.service = ErrorPatternService(self.mock_db)

    @pytest.mark.asyncio
    async def test_analyze_empty_questions(self):
        """测试无题目数据的分析"""
        # Mock数据库查询返回空列表
        with patch.object(self.service, '_get_student_questions', return_value=[]):
            result = await self.service.analyze_student_error_patterns(
                student_id=1,
                subject="math",
                timeframe_days=30
            )

        assert result.student_id == 1
        assert result.subject == "math"
        assert result.total_questions == 0
        assert result.total_errors == 0
        assert result.error_rate == 0.0

    @pytest.mark.asyncio
    async def test_analyze_with_questions(self):
        """测试有题目数据的分析"""
        # 创建模拟题目数据
        mock_questions = [
            Mock(
                spec=Question,
                is_correct=False,
                error_analysis="计算错误",
                difficulty_level=2,
                created_at=datetime.now()
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
                error_analysis="公式使用错误",
                difficulty_level=2,
                created_at=datetime.now()
            )
        ]

        with patch.object(self.service, '_get_student_questions', return_value=mock_questions):
            result = await self.service.analyze_student_error_patterns(
                student_id=1,
                subject="math",
                timeframe_days=30
            )

        assert result.total_questions == 3
        assert result.total_errors == 2
        assert result.error_rate == 0.667  # 2/3 约等于 0.667
        assert len(result.error_type_distribution) > 0

    @pytest.mark.asyncio
    async def test_analyze_question_error_correct(self):
        """测试正确答案的单题分析"""
        result = await self.service.analyze_question_error(
            question_text="1+1等于几？",
            student_answer="2",
            correct_answer="2",
            subject="math"
        )

        assert not result.has_errors
        assert result.overall_score == 1.0
        assert result.immediate_feedback == "答案正确！"
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_analyze_question_error_incorrect(self):
        """测试错误答案的单题分析"""
        result = await self.service.analyze_question_error(
            question_text="1+1等于几？",
            student_answer="3",
            correct_answer="2",
            subject="math"
        )

        assert result.has_errors
        assert result.overall_score < 1.0
        assert len(result.errors) > 0
        assert "问题" in result.immediate_feedback

    @pytest.mark.asyncio
    async def test_get_error_trends(self):
        """测试错误趋势分析"""
        result = await self.service.get_error_trends(
            student_id=1,
            subject="math",
            days=30
        )

        assert result.student_id == 1
        assert result.subject == "math"
        assert len(result.daily_error_rates) > 0
        assert result.overall_trend in ["improving", "stable", "worsening"]
        assert isinstance(result.improvement_rate, float)

    def test_determine_error_severity(self):
        """测试错误严重程度判断"""
        # 简单题目错误 - 高严重程度
        easy_question = Mock(spec=Question, difficulty_level=2)
        severity = self.service._determine_error_severity(easy_question, "math")
        assert severity == SeverityLevel.HIGH

        # 困难题目错误 - 低严重程度
        hard_question = Mock(spec=Question, difficulty_level=4)
        severity = self.service._determine_error_severity(hard_question, "math")
        assert severity == SeverityLevel.LOW

        # 中等题目错误 - 中等严重程度
        medium_question = Mock(spec=Question, difficulty_level=3)
        severity = self.service._determine_error_severity(medium_question, "math")
        assert severity == SeverityLevel.MEDIUM

    def test_determine_error_frequency(self):
        """测试错误频率判断"""
        assert self.service._determine_error_frequency(0.05) == ErrorFrequency.RARE
        assert self.service._determine_error_frequency(0.2) == ErrorFrequency.OCCASIONAL
        assert self.service._determine_error_frequency(0.45) == ErrorFrequency.FREQUENT
        assert self.service._determine_error_frequency(0.7) == ErrorFrequency.SYSTEMATIC

    def test_calculate_overall_trend(self):
        """测试总体趋势计算"""
        # 改进趋势
        improving_data = [
            {"error_rate": 0.5}, {"error_rate": 0.4},
            {"error_rate": 0.3}, {"error_rate": 0.2}
        ]
        trend = self.service._calculate_overall_trend(improving_data)
        assert trend == "improving"

        # 恶化趋势
        worsening_data = [
            {"error_rate": 0.2}, {"error_rate": 0.3},
            {"error_rate": 0.4}, {"error_rate": 0.5}
        ]
        trend = self.service._calculate_overall_trend(worsening_data)
        assert trend == "worsening"

        # 稳定趋势
        stable_data = [
            {"error_rate": 0.3}, {"error_rate": 0.3},
            {"error_rate": 0.3}, {"error_rate": 0.3}
        ]
        trend = self.service._calculate_overall_trend(stable_data)
        assert trend == "stable"

    def test_calculate_improvement_rate(self):
        """测试改进速度计算"""
        data = [
            {"error_rate": 0.5},
            {"error_rate": 0.4},
            {"error_rate": 0.3}
        ]
        rate = self.service._calculate_improvement_rate(data)
        # (0.5 - 0.3) / 3 = 0.0667 约等于 0.0667
        assert 0.06 <= rate <= 0.07

    def test_generate_action_items_for_error(self):
        """测试错误类型对应的行动项生成"""
        actions = self.service._get_action_items_for_error(
            ErrorTypeEnum.CALCULATION_ERROR,
            "math"
        )
        assert len(actions) > 0
        assert any("运算" in action for action in actions)

        actions = self.service._get_action_items_for_error(
            ErrorTypeEnum.CONCEPT_CONFUSION,
            "math"
        )
        assert len(actions) > 0
        assert any("概念" in action for action in actions)

    def test_calculate_question_score(self):
        """测试题目得分计算"""
        question = Mock(spec=Question)

        # 无错误 - 满分
        score = self.service._calculate_question_score(question, [])
        assert score == 1.0

        # 有高严重程度错误 - 扣分较多
        high_error = Mock()
        high_error.severity = SeverityLevel.HIGH
        score = self.service._calculate_question_score(question, [high_error])
        assert score == 0.7  # 1.0 - 0.3

        # 有低严重程度错误 - 扣分较少
        low_error = Mock()
        low_error.severity = SeverityLevel.LOW
        score = self.service._calculate_question_score(question, [low_error])
        assert score == 0.9  # 1.0 - 0.1


class TestErrorAnalysisIntegration:
    """错误分析集成测试"""

    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self):
        """测试完整分析流程"""
        mock_db = Mock()
        service = ErrorPatternService(mock_db)

        # 模拟数据库查询
        mock_questions = [
            Mock(
                spec=Question,
                is_correct=False,
                error_analysis="计算错误，步骤不完整",
                difficulty_level=2,
                created_at=datetime.now(),
                student_answer="5",
                correct_answer="4"
            )
        ]

        with patch.object(service, '_get_student_questions', return_value=mock_questions):
            # 执行分析
            result = await service.analyze_student_error_patterns(
                student_id=1,
                subject="math",
                timeframe_days=7
            )

            # 验证结果
            assert result.student_id == 1
            assert result.subject == "math"
            assert result.total_questions == 1
            assert result.total_errors == 1
            assert result.error_rate == 1.0

            # 验证错误类型分布
            assert len(result.error_type_distribution) > 0

            # 验证系统性错误识别
            # 单个错误不算系统性，应该为空
            assert len(result.systematic_errors) == 0

            # 验证改进建议
            assert isinstance(result.improvement_recommendations, list)
