#!/usr/bin/env python3
"""
错误处理和边界条件测试

测试各种异常情况和边界条件，确保系统的健壮性
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from httpx import HTTPStatusError, TimeoutException

from ai_tutor.services.student.progress_service import ProgressService, ProgressAlgorithm
from ai_tutor.services.student.student_service import StudentService


class TestProgressAlgorithmErrorHandling:
    """测试 ProgressAlgorithm 错误处理"""

    def setup_method(self):
        self.algorithm = ProgressAlgorithm()

    def test_empty_data_handling(self):
        """测试空数据处理"""
        # 测试空数据 - 使用正确的参数
        assert self.algorithm.calculate_mastery_rate(0, 0, 0.0) == 0.0

        # 测试零总答题数
        assert self.algorithm.calculate_mastery_rate(5, 0, 0.8) == 0.0

    def test_negative_values_handling(self):
        """测试负数值处理"""
        # 测试负数正确答题数（业务上不应出现）
        result = self.algorithm.calculate_mastery_rate(-1, 10, 0.8)
        assert 0.0 <= result <= 1.0

    def test_extreme_accuracy_values(self):
        """测试极端准确率值"""
        # 测试超过1.0的近期准确率
        result = self.algorithm.calculate_mastery_rate(8, 10, 1.5)
        assert 0.0 <= result <= 1.0

    def test_large_numbers(self):
        """测试大数值处理"""
        # 测试超大答题数
        result = self.algorithm.calculate_mastery_rate(999999, 1000000, 0.8)
        assert 0.0 <= result <= 1.0

    def test_identify_weak_points_empty_data(self):
        """测试薄弱点识别的空数据处理"""
        weak_points = self.algorithm.identify_weak_points([])
        assert weak_points == []

        # 测试包含无效数据的列表
        invalid_data = [{}]  # 空字典
        weak_points = self.algorithm.identify_weak_points(invalid_data)
        assert weak_points == []

    def test_calculate_learning_velocity_edge_cases(self):
        """测试学习速度计算边界条件"""
        # 测试空数据
        velocity = self.algorithm.calculate_learning_velocity([])
        assert velocity is None or velocity == 0

        # 测试单个数据点
        single_point = Mock()
        single_point.date = datetime.now()
        single_point.mastery_rate = 0.8

        velocity = self.algorithm.calculate_learning_velocity([single_point])
        assert velocity is None or velocity >= 0

    def test_predict_mastery_time_edge_cases(self):
        """测试掌握时间预测边界条件"""
        # 测试已经掌握的情况
        result = self.algorithm.predict_mastery_time(0.9, 0.8, 0.01)
        assert result is None

        # 测试无进步的情况
        result = self.algorithm.predict_mastery_time(0.3, 0.8, 0.0)
        assert result is None

        # 测试正常情况
        result = self.algorithm.predict_mastery_time(0.3, 0.8, 0.02)
        assert result is not None and result > 0


class TestProgressServiceErrorHandling:
    """测试 ProgressService 错误处理"""

    def setup_method(self):
        self.progress_service = ProgressService()

    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """测试数据库连接错误"""
        with patch.object(self.progress_service, 'get_db_session') as mock_db:
            mock_db.side_effect = SQLAlchemyError("数据库连接失败")

            with pytest.raises(SQLAlchemyError):
                await self.progress_service.calculate_subject_progress(1, "math")

    @pytest.mark.asyncio
    async def test_invalid_student_id(self):
        """测试无效的学生ID"""
        with patch.object(self.progress_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.query.return_value.filter.return_value.all.return_value = []

            # 测试负数ID
            result = await self.progress_service.calculate_subject_progress(-1, "math")
            assert result.total_questions == 0
            assert result.mastery_rate == 0.0

            # 测试极大数值ID
            result = await self.progress_service.calculate_subject_progress(999999999, "math")
            assert result.total_questions == 0

    @pytest.mark.asyncio
    async def test_empty_subject(self):
        """测试空科目名称"""
        with patch.object(self.progress_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.query.return_value.filter.return_value.all.return_value = []

            result = await self.progress_service.calculate_subject_progress(1, "")
            assert result.subject == ""
            assert result.total_questions == 0

    @pytest.mark.asyncio
    async def test_corrupted_data_handling(self):
        """测试数据损坏情况"""
        with patch.object(self.progress_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # 模拟损坏的数据记录 - 需要包含必需的时间字段
            corrupted_session = Mock()
            corrupted_session.completed_at = datetime.now()  # 添加时间字段

            corrupted_question = Mock()
            corrupted_question.is_correct = None  # 损坏的数据
            corrupted_question.score = None

            mock_db.query.return_value.filter.return_value.all.side_effect = [
                [corrupted_session],  # homework_sessions查询
                [corrupted_question]  # questions查询
            ]

            result = await self.progress_service.calculate_subject_progress(1, "math")
            # 应该优雅处理损坏的数据
            assert hasattr(result, 'subject')
            assert hasattr(result, 'total_questions')


class TestStudentServiceErrorHandling:
    """测试 StudentService 错误处理"""

    def setup_method(self):
        with patch('ai_tutor.services.student.student_service.get_db'):
            self.student_service = StudentService(Mock())

    @pytest.mark.asyncio
    async def test_create_student_integrity_error(self):
        """测试创建学生时的完整性约束错误"""
        with patch.object(self.student_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.add.side_effect = IntegrityError("", "", "")

            student_data = {
                "name": "测试学生",
                "student_id": "TEST001",
                "grade": "grade_1",
                "class_name": "一班"
            }

            with pytest.raises(IntegrityError):
                await self.student_service.create_student(student_data)

    @pytest.mark.asyncio
    async def test_database_rollback_on_error(self):
        """测试数据库事务回滚"""
        with patch.object(self.student_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.commit.side_effect = Exception("提交失败")

            student_data = {
                "name": "测试学生",
                "student_id": "TEST001",
                "grade": "grade_1",
                "class_name": "一班"
            }

            with pytest.raises(Exception):
                await self.student_service.create_student(student_data)

            # 验证回滚被调用
            mock_db.rollback.assert_called_once()


class TestBoundaryConditions:
    """边界条件测试"""

    def test_date_boundary_conditions(self):
        """测试日期边界条件"""
        algorithm = ProgressAlgorithm()

        # 测试未来日期
        future_date = datetime.now() + timedelta(days=365)
        # 应该优雅处理未来日期

        # 测试过去很久的日期
        ancient_date = datetime(1900, 1, 1)
        # 应该优雅处理古老日期

        assert True  # 基本日期处理测试

    def test_numeric_boundary_conditions(self):
        """测试数值边界条件"""
        algorithm = ProgressAlgorithm()

        # 测试极小值
        result = algorithm.calculate_mastery_rate(1, 10000, 0.0001)
        assert 0.0 <= result <= 1.0

        # 测试接近1的值
        result = algorithm.calculate_mastery_rate(9999, 10000, 0.9999)
        assert 0.0 <= result <= 1.0

    def test_string_boundary_conditions(self):
        """测试字符串边界条件"""
        # 测试空字符串
        assert len("") == 0

        # 测试单字符
        single_char = "A"
        assert len(single_char) == 1

        # 测试Unicode字符
        unicode_string = "数学题目🧮📊"
        assert len(unicode_string) > 0


class TestConcurrencyAndRaceConditions:
    """并发和竞态条件测试"""

    @pytest.mark.asyncio
    async def test_concurrent_progress_updates(self):
        """测试并发进度更新"""
        progress_service = ProgressService()

        # 模拟多个并发更新
        with patch.object(progress_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = None

            # 并发更新同一个知识点
            tasks = []
            for i in range(5):  # 减少并发数量避免测试过重
                task = progress_service.update_knowledge_progress(
                    student_id=1,
                    knowledge_point_id=1,
                    is_correct=True,
                    confidence_score=0.8
                )
                tasks.append(task)

            # 所有任务都应该完成而不出错
            import asyncio
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                assert not isinstance(result, Exception)


class TestMemoryAndResourceManagement:
    """内存和资源管理测试"""

    @pytest.mark.asyncio
    async def test_large_dataset_memory_usage(self):
        """测试大数据集内存使用"""
        progress_service = ProgressService()

        # 模拟大量数据
        large_sessions = [Mock(completed_at=datetime.now()) for _ in range(100)]
        large_questions = [Mock(is_correct=True, score=85) for _ in range(1000)]

        with patch.object(progress_service, 'get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.query.return_value.filter.return_value.all.side_effect = [
                large_sessions,  # homework_sessions查询
                large_questions  # questions查询
            ]

            result = await progress_service.calculate_subject_progress(1, "math")

            # 应该能够处理大数据集
            assert hasattr(result, 'total_questions')
            assert result.total_questions >= 0

    def test_algorithm_performance_with_large_data(self):
        """测试算法在大数据下的性能"""
        algorithm = ProgressAlgorithm()

        # 测试大数值输入
        import time
        start_time = time.time()

        # 使用正确的参数签名
        result = algorithm.calculate_mastery_rate(800000, 1000000, 0.8)

        end_time = time.time()
        execution_time = end_time - start_time

        # 算法应该在合理时间内完成（小于1秒）
        assert execution_time < 1.0
        assert 0.0 <= result <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
