"""
pytest全局配置文件
配置异步测试、数据库mock和通用fixtures
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock

from src.ai_tutor.main import app


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环供整个测试会话使用"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """异步HTTP客户端fixture"""
    from fastapi.testclient import TestClient
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    session.flush = Mock()
    return session


@pytest.fixture
def sample_student_data():
    """示例学生数据"""
    return {
        "id": 1,
        "name": "张三",
        "grade": "初二",
        "class_name": "2班",
        "student_id": "2023001",
        "created_at": datetime.now() - timedelta(days=30),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_homework_data():
    """示例作业数据"""
    return [
        {
            "id": 1,
            "student_id": 1,
            "subject": "math",
            "completed_at": datetime.now() - timedelta(days=1),
            "status": "completed",
            "total_questions": 10,
            "correct_answers": 8
        },
        {
            "id": 2,
            "student_id": 1,
            "subject": "math",
            "completed_at": datetime.now() - timedelta(days=3),
            "status": "completed",
            "total_questions": 15,
            "correct_answers": 12
        }
    ]


@pytest.fixture
def sample_questions_data():
    """示例题目数据"""
    return [
        {
            "id": 1,
            "homework_session_id": 1,
            "question_text": "解方程：2x + 3 = 7",
            "student_answer": "x = 2",
            "correct_answer": "x = 2",
            "is_correct": True,
            "knowledge_points": ["一元一次方程"]
        },
        {
            "id": 2,
            "homework_session_id": 1,
            "question_text": "分解因式：x² - 4",
            "student_answer": "(x+2)(x-2)",
            "correct_answer": "(x+2)(x-2)",
            "is_correct": True,
            "knowledge_points": ["因式分解"]
        },
        {
            "id": 3,
            "homework_session_id": 2,
            "question_text": "解方程：3x - 1 = 8",
            "student_answer": "x = 3",
            "correct_answer": "x = 3",
            "is_correct": True,
            "knowledge_points": ["一元一次方程"]
        }
    ]


@pytest.fixture
def mock_progress_service():
    """模拟学习进度服务"""
    service = AsyncMock()

    # 模拟calculate_subject_progress方法
    service.calculate_subject_progress.return_value = {
        "student_id": 1,
        "subject": "math",
        "overall_progress": 0.75,
        "mastery_rate": 0.8,
        "total_questions": 25,
        "correct_answers": 20,
        "knowledge_points": {
            "一元一次方程": {"mastery": 0.9, "attempts": 8, "correct": 7},
            "因式分解": {"mastery": 0.6, "attempts": 5, "correct": 3}
        },
        "weak_points": ["因式分解"],
        "recent_performance": 0.8,
        "timeframe_days": 30,
        "last_updated": datetime.now()
    }

    # 模拟get_learning_trends方法
    service.get_learning_trends.return_value = [
        {
            "date": datetime(2024, 1, 10),
            "accuracy_rate": 0.8,
            "practice_count": 5,
            "average_score": 85.0,
            "study_time_minutes": 60
        },
        {
            "date": datetime(2024, 1, 9),
            "accuracy_rate": 0.75,
            "practice_count": 8,
            "average_score": 78.0,
            "study_time_minutes": 45
        }
    ]

    # 模拟update_knowledge_progress方法
    service.update_knowledge_progress.return_value = {
        "success": True,
        "message": "知识点进度更新成功"
    }

    return service


@pytest.fixture
def mock_student_service():
    """模拟学生服务"""
    service = AsyncMock()

    service.create_student.return_value = {
        "id": 1,
        "name": "张三",
        "grade": "初二",
        "class_name": "2班",
        "student_id": "2023001"
    }

    service.get_student.return_value = {
        "id": 1,
        "name": "张三",
        "grade": "初二",
        "class_name": "2班",
        "student_id": "2023001",
        "created_at": datetime.now(),
        "homework_count": 5,
        "avg_score": 82.5
    }

    return service


@pytest.fixture
def mock_llm_service():
    """模拟LLM服务"""
    service = AsyncMock()

    service.chat.return_value = "这是模拟的AI回复"
    service.generate.return_value = {
        "knowledge_points": ["一元一次方程", "代数运算"],
        "difficulty": "中等",
        "confidence": 0.85
    }

    return service


@pytest.fixture
def mock_ocr_service():
    """模拟OCR服务"""
    service = AsyncMock()

    service.extract_text.return_value = "解方程：2x + 3 = 7\n学生答案：x = 2"

    return service


# pytest-asyncio配置
pytest_plugins = ('pytest_asyncio',)
