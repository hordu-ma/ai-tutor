"""
ProgressService 单元测试
测试学习进度管理服务的核心功能
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.ai_tutor.services.student.progress_service import ProgressService, ProgressAlgorithm
from src.ai_tutor.schemas.student_schemas import SubjectProgress, LearningTrend
from src.ai_tutor.models.student import Student
from src.ai_tutor.models.homework import HomeworkSession, Question, SubjectEnum
from src.ai_tutor.models.knowledge import KnowledgeProgress, KnowledgePoint


class TestProgressAlgorithm:
    """测试进度计算核心算法"""

    def test_calculate_mastery_rate_basic(self):
        """测试基础掌握率计算"""
        mastery_rate = ProgressAlgorithm.calculate_mastery_rate(
            correct_answers=8,
            total_answers=10,
            recent_accuracy=0.9,
            time_decay_factor=1.0
        )

        # 历史准确率 0.8，近期准确率 0.9
        # 期望值 = 0.9 * 0.6 + 0.8 * 0.4 = 0.86
        expected = 0.86
        assert abs(mastery_rate - expected) < 0.01

    def test_calculate_mastery_rate_no_data(self):
        """测试无数据时的掌握率计算"""
        mastery_rate = ProgressAlgorithm.calculate_mastery_rate(
            correct_answers=0,
            total_answers=0,
            recent_accuracy=0.0
        )
        assert mastery_rate == 0.0

    def test_calculate_mastery_rate_with_decay(self):
        """测试带时间衰减的掌握率计算"""
        mastery_rate = ProgressAlgorithm.calculate_mastery_rate(
            correct_answers=7,
            total_answers=10,
            recent_accuracy=0.8,
            time_decay_factor=0.9
        )

        # (0.8 * 0.6 + 0.7 * 0.4) * 0.9 = 0.76 * 0.9 = 0.684
        expected = 0.684
        assert abs(mastery_rate - expected) < 0.01

    def test_identify_weak_points(self):
        """测试薄弱知识点识别"""
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

        weak_points = ProgressAlgorithm.identify_weak_points(
            knowledge_progresses, threshold=0.6
        )

        # 应该只识别出足够练习次数且掌握率低的知识点
        assert '一元一次方程' in weak_points
        assert '因式分解' in weak_points
        assert '二次函数' not in weak_points  # 掌握率高
        assert '平面几何' not in weak_points  # 练习次数不足

    def test_calculate_learning_velocity_basic(self):
        """测试学习速度计算"""
        base_time = datetime(2024, 1, 1)
        progress_history = [
            (base_time, 0.3),
            (base_time + timedelta(days=7), 0.5),
            (base_time + timedelta(days=14), 0.7),
        ]

        velocity = ProgressAlgorithm.calculate_learning_velocity(
            progress_history, days_window=14
        )

        # 14天内从0.3提升到0.7，速度约为 0.4/14 ≈ 0.029
        assert 0.02 < velocity < 0.04

    def test_calculate_learning_velocity_insufficient_data(self):
        """测试数据不足时的学习速度计算"""
        progress_history = [(datetime.now(), 0.5)]

        velocity = ProgressAlgorithm.calculate_learning_velocity(
            progress_history, days_window=14
        )

        assert velocity == 0.0

    def test_predict_mastery_time(self):
        """测试掌握时间预测"""
        days = ProgressAlgorithm.predict_mastery_time(
            current_mastery=0.4,
            target_mastery=0.8,
            learning_velocity=0.02  # 每天提升2%
        )

        # (0.8 - 0.4) / 0.02 = 20天
        assert days == 20

    def test_predict_mastery_time_already_mastered(self):
        """测试已掌握情况的时间预测"""
        days = ProgressAlgorithm.predict_mastery_time(
            current_mastery=0.9,
            target_mastery=0.8,
            learning_velocity=0.02
        )

        assert days is None

    def test_predict_mastery_time_no_progress(self):
        """测试无进步情况的时间预测"""
        days = ProgressAlgorithm.predict_mastery_time(
            current_mastery=0.4,
            target_mastery=0.8,
            learning_velocity=0.0
        )

        assert days is None


class TestProgressService:
    """测试进度服务"""

    @pytest.fixture
    def progress_service(self):
        """创建进度服务实例"""
        return ProgressService()

    @pytest.fixture
    def mock_db_session(self):
        """模拟数据库会话"""
        mock_session = Mock()
        return mock_session

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_calculate_subject_progress_basic(self, mock_get_db, progress_service):
        """测试科目进度计算基础功能"""
        # 模拟数据库会话
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟作业会话数据
        mock_homework_session = Mock()
        mock_homework_session.id = 1
        mock_homework_session.completed_at = datetime.now()

        mock_session.query.return_value.filter.return_value.all.return_value = [mock_homework_session]

        # 模拟题目数据
        mock_questions = [
            Mock(is_correct=True, score=90),
            Mock(is_correct=False, score=60),
            Mock(is_correct=True, score=85),
        ]

        # 为不同的query调用返回不同结果
        def mock_query_side_effect(model):
            if model == Question:
                query_mock = Mock()
                query_mock.filter.return_value.all.return_value = mock_questions
                return query_mock
            return mock_session.query.return_value

        mock_session.query.side_effect = mock_query_side_effect

        # 模拟薄弱知识点查询
        with patch.object(progress_service, '_get_weak_knowledge_points') as mock_weak_points:
            mock_weak_points.return_value = ['一元一次方程']

            # 执行测试
            result = await progress_service.calculate_subject_progress(
                student_id=1,
                subject="math",
                timeframe_days=30
            )

            # 验证结果
            assert isinstance(result, SubjectProgress)
            assert result.subject == "math"
            assert result.total_questions == 3
            assert result.correct_questions == 2
            assert result.mastery_rate > 0
            assert '一元一次方程' in result.weak_knowledge_points

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_calculate_subject_progress_no_data(self, mock_get_db, progress_service):
        """测试无数据时的科目进度计算"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟无作业数据
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch.object(progress_service, '_get_weak_knowledge_points') as mock_weak_points:
            mock_weak_points.return_value = []

            result = await progress_service.calculate_subject_progress(
                student_id=1,
                subject="math",
                timeframe_days=30
            )

            assert result.mastery_rate == 0.0
            assert result.total_questions == 0
            assert result.correct_questions == 0
            assert len(result.weak_knowledge_points) == 0

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_get_learning_trends(self, mock_get_db, progress_service):
        """测试学习趋势获取"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟按日统计数据
        mock_daily_stats = [
            Mock(date=datetime(2024, 1, 1).date(), total_questions=5, correct_questions=4, avg_score=80.0),
            Mock(date=datetime(2024, 1, 2).date(), total_questions=8, correct_questions=6, avg_score=75.0),
            Mock(date=datetime(2024, 1, 3).date(), total_questions=6, correct_questions=5, avg_score=85.0),
        ]

        mock_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_daily_stats

        result = await progress_service.get_learning_trends(
            student_id=1,
            subject="math",
            days=3
        )

        assert len(result) == 3
        assert all(isinstance(trend, LearningTrend) for trend in result)

        # 验证第一天数据
        first_trend = result[0]
        assert first_trend.accuracy_rate == 0.8  # 4/5
        assert first_trend.practice_count == 5
        assert first_trend.average_score == 80.0

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_update_knowledge_progress_new_record(self, mock_get_db, progress_service):
        """测试创建新的知识点进度记录"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟查询不到现有记录
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch.object(progress_service, '_calculate_recent_accuracy') as mock_recent:
            mock_recent.return_value = 0.8

            await progress_service.update_knowledge_progress(
                student_id=1,
                knowledge_point_id=2,
                is_correct=True,
                confidence_score=0.9
            )

            # 验证创建了新记录
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_update_knowledge_progress_existing_record(self, mock_get_db, progress_service):
        """测试更新现有知识点进度记录"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟现有记录
        mock_progress = Mock()
        mock_progress.total_attempts = 5
        mock_progress.correct_attempts = 3
        mock_progress.mastery_level = 0.6
        mock_progress.mastery_achieved_at = None

        mock_session.query.return_value.filter.return_value.first.return_value = mock_progress

        with patch.object(progress_service, '_calculate_recent_accuracy') as mock_recent:
            mock_recent.return_value = 0.8

            await progress_service.update_knowledge_progress(
                student_id=1,
                knowledge_point_id=2,
                is_correct=True,
                confidence_score=0.9
            )

            # 验证更新了统计数据
            assert mock_progress.total_attempts == 6
            assert mock_progress.correct_attempts == 4
            assert mock_progress.accuracy_rate == 4/6
            assert mock_progress.confidence_score == 0.9
            mock_session.commit.assert_called_once()

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_get_learning_recommendations(self, mock_get_db, progress_service):
        """测试获取学习建议"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟薄弱知识点数据
        mock_progress = Mock()
        mock_progress.mastery_level = 0.3
        mock_progress.common_errors = {"calculation_error": 3}
        mock_progress.recommended_exercises = ["练习题1", "练习题2"]

        mock_knowledge_point = Mock()
        mock_knowledge_point.name = "一元一次方程"
        mock_knowledge_point.id = 1

        mock_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            (mock_progress, mock_knowledge_point)
        ]

        with patch.object(progress_service, '_estimate_practice_time') as mock_time, \
             patch.object(progress_service, '_generate_improvement_strategies') as mock_strategies, \
             patch.object(progress_service, '_estimate_mastery_timeline') as mock_timeline:

            mock_time.return_value = 45
            mock_strategies.return_value = ["建议从基础概念开始复习"]
            mock_timeline.return_value = 15

            result = await progress_service.get_learning_recommendations(
                student_id=1,
                subject="math",
                limit=5
            )

            assert len(result) == 1
            recommendation = result[0]
            assert recommendation["knowledge_point"] == "一元一次方程"
            assert recommendation["current_mastery"] == 0.3
            assert recommendation["priority"] == "high"  # mastery < 0.4
            assert recommendation["suggested_practice_time"] == 45
            assert recommendation["estimated_mastery_days"] == 15

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_analyze_learning_patterns(self, mock_get_db, progress_service):
        """测试学习模式分析"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟小时活动数据
        mock_hourly_activity = [
            Mock(hour=9, count=5),
            Mock(hour=14, count=8),
            Mock(hour=20, count=3),
        ]

        # 模拟每日活动数据
        mock_daily_activity = [
            Mock(date=datetime(2024, 1, 1).date(), sessions=2, total_score=150),
            Mock(date=datetime(2024, 1, 2).date(), sessions=3, total_score=200),
            Mock(date=datetime(2024, 1, 3).date(), sessions=2, total_score=180),
        ]

        # 模拟科目表现数据
        mock_subject_performance = [
            Mock(subject="math", question_count=20, accuracy=0.8, avg_score=85.0),
            Mock(subject="physics", question_count=15, accuracy=0.7, avg_score=75.0),
        ]

        # 简化mock设置，直接设置三次查询的返回值
        query_returns = [mock_hourly_activity, mock_daily_activity, mock_subject_performance]
        query_index = 0

        def mock_query_side_effect(*args, **kwargs):
            nonlocal query_index
            query_mock = Mock()

            # 设置查询链的返回值
            final_query = Mock()
            final_query.all.return_value = query_returns[query_index]

            query_mock.filter.return_value.group_by.return_value = final_query
            query_mock.join.return_value.filter.return_value.group_by.return_value = final_query

            query_index += 1
            return query_mock

        mock_session.query.side_effect = mock_query_side_effect

        result = await progress_service.analyze_learning_patterns(
            student_id=1,
            days=30
        )

        # 验证结果结构
        assert "learning_consistency" in result
        assert "best_learning_hour" in result
        assert "daily_activity_pattern" in result
        assert "subject_preferences" in result
        assert "avg_daily_sessions" in result
        assert "total_study_days" in result

        # 验证最佳学习时间（最高活动时间）
        assert result["best_learning_hour"] == 14

        # 验证学习一致性计算（标准差的倒数）
        assert 0 <= result["learning_consistency"] <= 1

        # 验证科目偏好（列表格式）
        preferences = result["subject_preferences"]
        assert len(preferences) == 2

        # 找到数学和物理的偏好数据
        math_pref = next((p for p in preferences if p["subject"] == "math"), None)
        physics_pref = next((p for p in preferences if p["subject"] == "physics"), None)

        assert math_pref is not None
        assert physics_pref is not None
        assert math_pref["performance"] == 0.8
        assert physics_pref["performance"] == 0.7
    def test_estimate_practice_time(self, progress_service):
        """测试练习时间估算"""
        mock_progress = Mock()
        mock_progress.mastery_level = 0.4  # 掌握程度40%

        estimated_time = progress_service._estimate_practice_time(mock_progress)

        # 基础时间30分钟 + 掌握度差距影响
        # 30 * (1 + (1-0.4) * 2) = 30 * 2.2 = 66分钟
        assert estimated_time == 66

    def test_generate_improvement_strategies(self, progress_service):
        """测试改进策略生成"""
        mock_knowledge_point = Mock()
        mock_knowledge_point.name = "一元一次方程"

        # 测试低掌握度情况
        mock_progress_low = Mock()
        mock_progress_low.mastery_level = 0.2

        strategies = progress_service._generate_improvement_strategies(
            mock_knowledge_point, mock_progress_low, {}
        )

        assert "建议从基础概念开始复习" in strategies
        assert "寻求老师或同学的帮助" in strategies

        # 测试中等掌握度情况
        mock_progress_medium = Mock()
        mock_progress_medium.mastery_level = 0.5

        strategies = progress_service._generate_improvement_strategies(
            mock_knowledge_point, mock_progress_medium, {"calculation_error": 3}
        )

        assert "增加相关练习题的数量" in strategies
        assert "注意计算细节，使用验算方法" in strategies

    def test_estimate_mastery_timeline(self, progress_service):
        """测试掌握时间线估算"""
        mock_progress = Mock()
        mock_progress.mastery_level = 0.5

        days = progress_service._estimate_mastery_timeline(mock_progress)

        # (0.75 - 0.5) / 0.05 = 5天
        assert days == 5

        # 测试已掌握情况
        mock_progress.mastery_level = 0.8
        days = progress_service._estimate_mastery_timeline(mock_progress)
        assert days is None


class TestProgressServiceIntegration:
    """集成测试"""

    @pytest.fixture
    def progress_service(self):
        return ProgressService()

    @patch('src.ai_tutor.services.student.progress_service.get_db')
    @pytest.mark.asyncio
    async def test_complete_progress_workflow(self, mock_get_db, progress_service):
        """测试完整的进度管理工作流"""
        mock_session = Mock()
        mock_get_db.return_value.__next__ = Mock(return_value=mock_session)

        # 模拟学生完成一次练习的完整流程
        student_id = 1
        subject = "math"
        knowledge_point_id = 1

        # 1. 更新知识点进度
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch.object(progress_service, '_calculate_recent_accuracy') as mock_recent:
            mock_recent.return_value = 0.8

            await progress_service.update_knowledge_progress(
                student_id=student_id,
                knowledge_point_id=knowledge_point_id,
                is_correct=True,
                confidence_score=0.9
            )

        # 2. 计算科目进度
        mock_homework_session = Mock(id=1, completed_at=datetime.now())
        mock_questions = [Mock(is_correct=True, score=90)]

        # 3. 模拟对象定义（需要在mock_query_side_effect中使用）
        mock_progress = Mock(mastery_level=0.4, common_errors={}, recommended_exercises=[])
        mock_knowledge_point = Mock(id=knowledge_point_id)
        mock_knowledge_point.name = "测试知识点"

        def mock_query_side_effect(*models):
            if len(models) == 1:
                model = models[0]
                if model == Question:
                    query_mock = Mock()
                    query_mock.filter.return_value.all.return_value = mock_questions
                    return query_mock
                else:
                    query_mock = Mock()
                    query_mock.filter.return_value.all.return_value = [mock_homework_session]
                    return query_mock
            else:
                # Multiple models query (e.g., KnowledgeProgress, KnowledgePoint)
                query_mock = Mock()
                query_mock.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
                    (mock_progress, mock_knowledge_point)
                ]
                return query_mock

        mock_session.query.side_effect = mock_query_side_effect

        with patch.object(progress_service, '_get_weak_knowledge_points') as mock_weak:
            mock_weak.return_value = []

            progress = await progress_service.calculate_subject_progress(
                student_id=student_id,
                subject=subject,
                timeframe_days=30
            )

            assert progress.subject == subject
            assert progress.mastery_rate > 0

        # 3. 获取学习建议

        with patch.object(progress_service, '_estimate_practice_time') as mock_time, \
             patch.object(progress_service, '_generate_improvement_strategies') as mock_strategies, \
             patch.object(progress_service, '_estimate_mastery_timeline') as mock_timeline:

            mock_time.return_value = 30
            mock_strategies.return_value = ["练习建议"]
            mock_timeline.return_value = 10

            recommendations = await progress_service.get_learning_recommendations(
                student_id=student_id,
                subject=subject,
                limit=5
            )

            assert len(recommendations) > 0
            assert recommendations[0]["knowledge_point"] == "测试知识点"
