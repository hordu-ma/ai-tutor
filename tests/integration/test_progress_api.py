"""
ProgressService API 集成测试
测试学习进度管理API的完整功能流程
"""

import pytest
import json
from datetime import datetime, timedelta
from httpx import AsyncClient
from unittest.mock import patch, Mock, AsyncMock

from src.ai_tutor.main import app
from src.ai_tutor.models.student import Student
from src.ai_tutor.models.homework import HomeworkSession, Question, SubjectEnum
from src.ai_tutor.models.knowledge import KnowledgeProgress, KnowledgePoint
from src.ai_tutor.services.student.progress_service import get_progress_service
from src.ai_tutor.schemas.student_schemas import SubjectProgress


class TestProgressAPI:
    """测试学习进度管理API"""

    @pytest.fixture
    def sample_student_data(self):
        """示例学生数据"""
        return {
            "id": 1,
            "name": "张三",
            "grade": "初二",
            "class_name": "2班"
        }

    @pytest.fixture
    def sample_homework_data(self):
        """示例作业数据"""
        return [
            {
                "id": 1,
                "student_id": 1,
                "subject": "math",
                "completed_at": datetime.now() - timedelta(days=1),
                "status": "completed"
            },
            {
                "id": 2,
                "student_id": 1,
                "subject": "math",
                "completed_at": datetime.now() - timedelta(days=3),
                "status": "completed"
            }
        ]

    @pytest.fixture
    def sample_questions_data(self):
        """示例题目数据"""
        return [
            {
                "id": 1,
                "homework_session_id": 1,
                "is_correct": True,
                "score": 95.0,
                "knowledge_points": ["一元一次方程"]
            },
            {
                "id": 2,
                "homework_session_id": 1,
                "is_correct": False,
                "score": 65.0,
                "knowledge_points": ["因式分解"]
            },
            {
                "id": 3,
                "homework_session_id": 2,
                "is_correct": True,
                "score": 88.0,
                "knowledge_points": ["一元一次方程"]
            }
        ]

    @pytest.mark.asyncio
    async def test_get_subject_progress_success(
        self,
        async_client,
        sample_homework_data,
        sample_questions_data,
        mock_progress_service
    ):
        """测试获取科目学习进度成功"""
        # 设置mock服务的返回值
        expected_progress = SubjectProgress(
            subject="math",
            mastery_rate=0.8,
            total_questions=25,
            correct_questions=20,
            recent_performance=0.85,
            weak_knowledge_points=["因式分解"]
        )
        mock_progress_service.calculate_subject_progress.return_value = expected_progress

        # 使用依赖覆盖
        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            # 发送请求
            response = await async_client.get(
                "/api/v1/students/999/progress/math",
                params={"timeframe_days": 30}
            )

            # 验证响应
            assert response.status_code == 200
            data = response.json()

            assert data["subject"] == "math"
            assert "mastery_rate" in data
            assert "total_questions" in data
            assert "correct_questions" in data
            assert "recent_performance" in data
            assert "weak_knowledge_points" in data

            # 验证数据类型和范围
            assert isinstance(data["mastery_rate"], float)
            assert 0.0 <= data["mastery_rate"] <= 1.0
            assert isinstance(data["total_questions"], int)
            assert data["total_questions"] >= 0
            assert isinstance(data["correct_questions"], int)
            assert data["correct_questions"] >= 0

        finally:
            # 清理依赖覆盖
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_subject_progress_no_data(self, async_client, mock_progress_service):
        """测试无学习数据时的科目进度获取"""
        # 设置无数据的返回值
        empty_progress = SubjectProgress(
            subject="math",
            mastery_rate=0.0,
            total_questions=0,
            correct_questions=0,
            recent_performance=0.0,
            weak_knowledge_points=[]
        )
        mock_progress_service.calculate_subject_progress.return_value = empty_progress

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get("/api/v1/students/1/progress/math")

            assert response.status_code == 200
            data = response.json()

            assert data["subject"] == "math"
            assert data["mastery_rate"] == 0.0
            assert data["total_questions"] == 0

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_subject_progress_invalid_student(self, async_client, mock_progress_service):
        """测试无效学生ID的处理"""
        # 模拟服务抛出异常
        mock_progress_service.calculate_subject_progress.side_effect = Exception("Student not found")

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get("/api/v1/students/99999/progress/math")

            # 应该返回500错误
            assert response.status_code == 500

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_subject_progress_invalid_params(self, async_client):
        """测试无效参数的处理"""
        # 测试无效的时间范围
        response = await async_client.get(
            "/api/v1/students/1/progress/math",
            params={"timeframe_days": -1}
        )
        assert response.status_code == 422  # 验证错误

        # 测试超出范围的时间范围
        response = await async_client.get(
            "/api/v1/students/1/progress/math",
            params={"timeframe_days": 400}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_learning_trends_success(self, async_client, mock_progress_service):
        """测试获取学习趋势成功"""
        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get(
                "/api/v1/students/1/progress/math/trends",
                params={"days": 7}
            )

            assert response.status_code == 200
            data = response.json()

            assert isinstance(data, list)
            assert len(data) == 2

            # 验证第一个趋势数据
            first_trend = data[0]
            assert "date" in first_trend
            assert "accuracy_rate" in first_trend
            assert "practice_count" in first_trend
            assert "average_score" in first_trend

            assert first_trend["accuracy_rate"] == 0.8
            assert first_trend["practice_count"] == 5
            assert first_trend["average_score"] == 85.0

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weak_knowledge_points_success(self, async_client, mock_progress_service):
        """测试获取薄弱知识点成功"""
        mock_progress_service.get_learning_recommendations.return_value = [
            {
                "knowledge_point": "因式分解",
                "current_mastery": 0.4,
                "priority": "high",
                "improvement_strategies": ["练习题1", "练习题2"]
            }
        ]

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get("/api/v1/students/1/weak-points/math")

            assert response.status_code == 200
            data = response.json()

            assert "student_id" in data
            assert "subject" in data
            assert "recommendations" in data
            assert data["student_id"] == 1
            assert data["subject"] == "math"
            assert len(data["recommendations"]) == 1

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_learning_patterns_success(self, async_client, mock_progress_service):
        """测试学习模式分析成功"""
        mock_progress_service.analyze_learning_patterns.return_value = {
            "learning_consistency": 0.8,
            "best_learning_hour": 14,
            "daily_activity_pattern": "afternoon_focused",
            "subject_preferences": {"math": 0.7, "physics": 0.5},
            "total_study_days": 20,
            "avg_daily_sessions": 2.5
        }

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get(
                "/api/v1/students/1/learning-patterns",
                params={"days": 30}
            )

            assert response.status_code == 200
            data = response.json()

            assert "student_id" in data
            assert "analysis_period_days" in data
            assert "patterns" in data

            patterns = data["patterns"]
            assert "learning_consistency" in patterns
            assert "best_learning_hour" in patterns
            assert "daily_activity_pattern" in patterns

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_knowledge_progress_success(self, async_client, mock_progress_service):
        """测试更新知识点进度成功"""
        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.post(
                "/api/v1/students/1/knowledge-progress/1",
                params={
                    "is_correct": True,
                    "confidence_score": 0.9
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "message" in data

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_knowledge_progress_invalid_params(self, async_client):
        """测试更新知识点进度参数验证"""
        # 缺少必需参数
        response = await async_client.post("/api/v1/students/1/knowledge-progress/1")
        assert response.status_code == 422

        # 无效的置信度分数
        response = await async_client.post(
            "/api/v1/students/1/knowledge-progress/1",
            params={
                "is_correct": True,
                "confidence_score": 1.5  # 超出范围
            }
        )
        assert response.status_code == 422


class TestProgressAPIErrorHandling:
    """测试API错误处理"""

    @pytest.mark.asyncio
    async def test_database_error_handling(self, async_client, mock_progress_service):
        """测试数据库错误处理"""
        # 模拟服务错误
        mock_progress_service.calculate_subject_progress.side_effect = Exception("数据库连接失败")

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get("/api/v1/students/1/progress/math")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_invalid_path_parameters(self, async_client):
        """测试路径参数验证"""
        # 无效的学生ID
        response = await async_client.get("/api/v1/students/abc/progress/math")
        assert response.status_code == 422

        # 无效的知识点ID
        response = await async_client.post(
            "/api/v1/students/1/knowledge-progress/abc",
            params={"is_correct": True}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_path_parameters(self, async_client):
        """测试缺少路径参数的情况"""
        # 缺少科目参数
        response = await async_client.get("/api/v1/students/1/progress/")
        assert response.status_code in [404, 405]  # 路由不匹配

        # 缺少学生ID
        response = await async_client.get("/api/v1/students//progress/math")
        assert response.status_code in [404, 422]


class TestProgressAPIPerformance:
    """测试API性能"""

    @pytest.mark.asyncio
    async def test_response_time_reasonable(self, async_client, mock_progress_service):
        """测试响应时间合理性"""
        import time

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            start_time = time.time()
            response = await async_client.get("/api/v1/students/1/progress/math")
            end_time = time.time()

            # 响应时间应该在合理范围内（少于2秒）
            response_time = end_time - start_time
            assert response_time < 2.0
            assert response.status_code == 200

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_large_dataset_handling(self, async_client, mock_progress_service):
        """测试大数据集处理能力"""
        # 模拟大量数据的返回值
        from datetime import datetime, timedelta
        base_date = datetime(2024, 1, 1)
        large_trends = [
            {
                "date": base_date + timedelta(days=i),
                "accuracy_rate": 0.8,
                "practice_count": 10,
                "average_score": 80.0,
                "study_time_minutes": 60
            }
            for i in range(100)  # 100天的数据
        ]
        mock_progress_service.get_learning_trends.return_value = large_trends

        app.dependency_overrides[get_progress_service] = lambda: mock_progress_service

        try:
            response = await async_client.get(
                "/api/v1/students/1/progress/math/trends",
                params={"days": 100}
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 100  # 应该能处理所有数据

        finally:
            app.dependency_overrides.clear()


class TestProgressAPIDocumentation:
    """测试API文档和规范性"""

    @pytest.mark.asyncio
    async def test_api_documentation_available(self, async_client):
        """测试API文档可访问性"""
        response = await async_client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_schema_includes_progress_endpoints(self, async_client):
        """测试OpenAPI schema包含进度管理端点"""
        response = await async_client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        # 检查关键端点是否存在
        progress_endpoints = [
            "/api/v1/students/{student_id}/progress/{subject}",
            "/api/v1/students/{student_id}/progress/{subject}/trends",
            "/api/v1/students/{student_id}/weak-points/{subject}",
            "/api/v1/students/{student_id}/learning-patterns",
            "/api/v1/students/{student_id}/knowledge-progress/{knowledge_point_id}"
        ]

        for endpoint in progress_endpoints:
            assert endpoint in paths, f"端点 {endpoint} 未在API文档中找到"
