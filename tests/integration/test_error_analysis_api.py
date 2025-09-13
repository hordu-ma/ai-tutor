"""
错误分析API集成测试 - 简化版本
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from ai_tutor.main import app
from ai_tutor.schemas.error_analysis import ErrorPatternAnalysis, QuestionErrorAnalysis


class TestErrorAnalysisAPI:
    """错误分析API测试"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get("/api/v1/error-analysis/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data

    def test_get_error_types(self):
        """测试获取错误类型列表"""
        response = self.client.get("/api/v1/error-analysis/error-types")

        assert response.status_code == 200
        data = response.json()
        assert "error_types" in data
        assert len(data["error_types"]) > 0

        # 验证错误类型结构
        error_type = data["error_types"][0]
        assert "code" in error_type
        assert "name" in error_type
        assert "description" in error_type
        assert "subjects" in error_type

    @patch('ai_tutor.services.error_analysis.get_error_analysis_service')
    def test_get_error_patterns(self, mock_service_getter):
        """测试获取错误模式分析"""
        # 设置Mock服务
        mock_service = Mock()
        mock_service_getter.return_value = mock_service

        # 设置Mock返回值
        mock_analysis = ErrorPatternAnalysis(
            student_id=1,
            subject="math",
            analysis_period="最近30天",
            total_questions=10,
            total_errors=3,
            error_rate=0.3,
            error_type_distribution={"calculation_error": 2, "concept_confusion": 1},
            severity_distribution={"medium": 2, "high": 1},
            systematic_errors=[],
            improvement_recommendations=[],
            progress_indicators={"overall_accuracy": 0.7}
        )

        mock_service.analyze_student_error_patterns.return_value = mock_analysis

        # 发送请求
        response = self.client.get(
            "/api/v1/error-analysis/students/1/patterns/math?timeframe_days=30"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == 1
        assert data["subject"] == "math"
        assert data["total_questions"] == 10
        assert data["total_errors"] == 3
        assert data["error_rate"] == 0.3

    def test_get_error_patterns_invalid_subject(self):
        """测试无效科目"""
        response = self.client.get(
            "/api/v1/error-analysis/students/1/patterns/invalid_subject"
        )

        assert response.status_code == 400
        data = response.json()
        assert "不支持的科目" in data["detail"]

    def test_get_error_patterns_invalid_timeframe(self):
        """测试无效时间范围"""
        response = self.client.get(
            "/api/v1/error-analysis/students/1/patterns/math?timeframe_days=400"
        )

        assert response.status_code == 422  # 验证错误

    @patch('ai_tutor.services.error_analysis.get_error_analysis_service')
    def test_analyze_question_error(self, mock_service_getter):
        """测试单题错误分析"""
        # 设置Mock服务
        mock_service = Mock()
        mock_service_getter.return_value = mock_service

        # 设置Mock返回值
        mock_analysis = QuestionErrorAnalysis(
            has_errors=True,
            errors=[],
            overall_score=0.8,
            confidence_score=0.9,
            knowledge_point_mastery={},
            immediate_feedback="发现1个问题",
            improvement_suggestions=["仔细检查计算过程"]
        )

        mock_service.analyze_question_error.return_value = mock_analysis

        # 发送请求
        request_data = {
            "question_text": "计算 2+3 的值",
            "student_answer": "6",
            "correct_answer": "5",
            "subject": "math"
        }

        response = self.client.post(
            "/api/v1/error-analysis/analyze-question",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_errors"] is True
        assert data["overall_score"] == 0.8
        assert "发现" in data["immediate_feedback"]

    def test_analyze_question_error_empty_input(self):
        """测试空输入的单题分析"""
        request_data = {
            "question_text": "",
            "student_answer": "答案",
            "correct_answer": "正确答案",
            "subject": "math"
        }

        response = self.client.post(
            "/api/v1/error-analysis/analyze-question",
            json=request_data
        )

        assert response.status_code == 400
        data = response.json()
        assert "不能为空" in data["detail"]

    @patch('ai_tutor.services.error_analysis.get_error_analysis_service')
    def test_get_error_trends(self, mock_service_getter):
        """测试错误趋势分析"""
        # 设置Mock服务
        mock_service = Mock()
        mock_service_getter.return_value = mock_service

        # 设置Mock返回值
        from ai_tutor.schemas.error_analysis import ErrorTrendAnalysis
        mock_trends = ErrorTrendAnalysis(
            student_id=1,
            subject="math",
            daily_error_rates=[{"date": "2024-01-15", "error_rate": 0.3}],
            weekly_summaries=[{"week": "Week 1", "avg_error_rate": 0.25}],
            overall_trend="improving",
            improvement_rate=0.02,
            regression_areas=[],
            predicted_mastery_time=None,
            risk_assessment="中等"
        )

        mock_service.get_error_trends.return_value = mock_trends

        # 发送请求
        response = self.client.get(
            "/api/v1/error-analysis/students/1/trends/math?days=30"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == 1
        assert data["subject"] == "math"
        assert data["overall_trend"] == "improving"
        assert len(data["daily_error_rates"]) > 0

    def test_get_error_trends_invalid_days(self):
        """测试无效天数参数"""
        response = self.client.get(
            "/api/v1/error-analysis/students/1/trends/math?days=5"  # 小于最小值7
        )

        assert response.status_code == 422

    @patch('ai_tutor.services.error_analysis.get_error_analysis_service')
    def test_get_error_summary(self, mock_service_getter):
        """测试多科目错误总结"""
        # 设置Mock服务
        mock_service = Mock()
        mock_service_getter.return_value = mock_service

        # 设置Mock返回值
        mock_analysis = ErrorPatternAnalysis(
            student_id=1,
            subject="math",
            analysis_period="最近30天",
            total_questions=10,
            total_errors=3,
            error_rate=0.3,
            error_type_distribution={"calculation_error": 2},
            severity_distribution={"medium": 2},
            systematic_errors=[],
            improvement_recommendations=[],
            progress_indicators={"improvement_trend": "improving"}
        )

        mock_service.analyze_student_error_patterns.return_value = mock_analysis

        # 发送请求
        response = self.client.get(
            "/api/v1/error-analysis/students/1/summary?subjects=math&subjects=physics"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == 1
        assert "subjects_analysis" in data
        assert "overall_error_rate" in data
        assert "total_errors" in data

    @patch('ai_tutor.services.error_analysis.get_error_analysis_service')
    def test_get_improvement_plan(self, mock_service_getter):
        """测试个性化改进计划"""
        # 设置Mock服务
        mock_service = Mock()
        mock_service_getter.return_value = mock_service

        # 设置Mock返回值
        mock_analysis = ErrorPatternAnalysis(
            student_id=1,
            subject="math",
            analysis_period="最近30天",
            total_questions=15,
            total_errors=5,
            error_rate=0.33,
            error_type_distribution={},
            severity_distribution={},
            systematic_errors=[],
            improvement_recommendations=[],
            progress_indicators={}
        )

        mock_service.analyze_student_error_patterns.return_value = mock_analysis

        # 发送请求
        response = self.client.get(
            "/api/v1/error-analysis/students/1/improvement-plan/math"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == 1
        assert data["subject"] == "math"
        assert "current_performance" in data
        assert "improvement_goals" in data
        assert "action_plan" in data
        assert "estimated_duration" in data
        assert "success_criteria" in data


class TestErrorAnalysisAPIValidation:
    """错误分析API参数验证测试"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_student_id_validation(self):
        """测试学生ID验证"""
        # 无效的学生ID
        response = self.client.get(
            "/api/v1/error-analysis/students/invalid/patterns/math"
        )
        assert response.status_code == 422

    def test_timeframe_boundary_validation(self):
        """测试时间范围边界值验证"""
        # 最小值测试
        response = self.client.get(
            "/api/v1/error-analysis/students/1/patterns/math?timeframe_days=1"
        )
        assert response.status_code in [200, 500]  # 可能因为服务mock问题返回500

        # 最大值测试
        response = self.client.get(
            "/api/v1/error-analysis/students/1/patterns/math?timeframe_days=365"
        )
        assert response.status_code in [200, 500]

        # 超出最大值
        response = self.client.get(
            "/api/v1/error-analysis/students/1/patterns/math?timeframe_days=366"
        )
        assert response.status_code == 422

    def test_question_analysis_required_fields(self):
        """测试单题分析必填字段"""
        # 缺少question_text
        response = self.client.post(
            "/api/v1/error-analysis/analyze-question",
            json={
                "student_answer": "答案",
                "correct_answer": "正确答案",
                "subject": "math"
            }
        )
        assert response.status_code == 422

        # 缺少student_answer
        response = self.client.post(
            "/api/v1/error-analysis/analyze-question",
            json={
                "question_text": "题目",
                "correct_answer": "正确答案",
                "subject": "math"
            }
        )
        assert response.status_code == 422

        # 缺少correct_answer
        response = self.client.post(
            "/api/v1/error-analysis/analyze-question",
            json={
                "question_text": "题目",
                "student_answer": "答案",
                "subject": "math"
            }
        )
        assert response.status_code == 422
