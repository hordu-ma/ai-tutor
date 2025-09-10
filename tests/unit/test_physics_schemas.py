"""
Unit tests for physics schemas.

Tests the physics-related Pydantic models and enums to ensure they work correctly.
"""

import pytest
from pydantic import ValidationError

from ai_tutor.schemas.physics_schemas import (
    PhysicsCategory,
    PhysicsQuestionType,
    PhysicsKnowledgePoint,
    PhysicsQuestion,
    PhysicsGradingResult,
    PhysicsHomeworkSession,
    PHYSICS_KNOWLEDGE_MAPPING,
)


def test_physics_category_enum():
    """Test PhysicsCategory enum values."""
    assert PhysicsCategory.MECHANICS == "力学"
    assert PhysicsCategory.ELECTROMAGNETICS == "电磁学"
    assert PhysicsCategory.THERMODYNAMICS == "热学"
    assert PhysicsCategory.OPTICS == "光学"
    assert PhysicsCategory.ATOMIC_PHYSICS == "原子物理"
    assert PhysicsCategory.WAVE_PHYSICS == "波动"


def test_physics_question_type_enum():
    """Test PhysicsQuestionType enum values."""
    assert PhysicsQuestionType.MULTIPLE_CHOICE == "选择题"
    assert PhysicsQuestionType.FILL_IN_BLANK == "填空题"
    assert PhysicsQuestionType.CALCULATION == "计算题"
    assert PhysicsQuestionType.PROOF == "证明题"
    assert PhysicsQuestionType.EXPERIMENT == "实验题"
    assert PhysicsQuestionType.DIAGRAM == "作图题"
    assert PhysicsQuestionType.SHORT_ANSWER == "简答题"


def test_physics_knowledge_point_enum():
    """Test PhysicsKnowledgePoint enum values."""
    assert PhysicsKnowledgePoint.NEWTON_LAWS == "牛顿运动定律"
    assert PhysicsKnowledgePoint.ELECTRIC_FIELD == "电场"
    assert PhysicsKnowledgePoint.IDEAL_GAS_LAW == "理想气体状态方程"
    assert PhysicsKnowledgePoint.GEOMETRIC_OPTICS == "几何光学"


def test_physics_question_model():
    """Test PhysicsQuestion Pydantic model."""
    question_data = {
        "text": "一个物体在水平面上做匀速直线运动，求摩擦力大小。",
        "question_type": PhysicsQuestionType.CALCULATION,
        "category": PhysicsCategory.MECHANICS,
        "knowledge_points": [PhysicsKnowledgePoint.NEWTON_LAWS],
        "difficulty_level": 3,
        "answer": "摩擦力等于重力乘以摩擦系数",
        "explanation": "根据牛顿第一定律，匀速直线运动时合力为零"
    }

    question = PhysicsQuestion(**question_data)
    assert question.text == question_data["text"]
    assert question.question_type == PhysicsQuestionType.CALCULATION
    assert question.category == PhysicsCategory.MECHANICS
    assert question.difficulty_level == 3
    assert len(question.knowledge_points) == 1


def test_physics_question_model_validation():
    """Test PhysicsQuestion model validation."""
    # Test invalid difficulty level
    with pytest.raises(ValidationError):
        PhysicsQuestion(
            text="测试题目",
            question_type=PhysicsQuestionType.MULTIPLE_CHOICE,
            category=PhysicsCategory.MECHANICS,
            difficulty_level=6  # Invalid: should be 1-5
        )

    # Test missing required fields
    with pytest.raises(ValidationError):
        PhysicsQuestion(
            text="测试题目"
            # Missing question_type and category
        )


def test_physics_grading_result_model():
    """Test PhysicsGradingResult Pydantic model."""
    question = PhysicsQuestion(
        text="测试题目",
        question_type=PhysicsQuestionType.CALCULATION,
        category=PhysicsCategory.MECHANICS,
        knowledge_points=[PhysicsKnowledgePoint.NEWTON_LAWS]
    )

    grading_data = {
        "question": question,
        "student_answer": "学生答案",
        "is_correct": True,
        "score": 85.5,
        "feedback": "答案正确，思路清晰",
        "knowledge_gaps": [],
        "suggestions": ["继续保持"]
    }

    grading_result = PhysicsGradingResult(**grading_data)
    assert grading_result.is_correct is True
    assert grading_result.score == 85.5
    assert grading_result.feedback == "答案正确，思路清晰"


def test_physics_grading_result_validation():
    """Test PhysicsGradingResult model validation."""
    question = PhysicsQuestion(
        text="测试题目",
        question_type=PhysicsQuestionType.CALCULATION,
        category=PhysicsCategory.MECHANICS
    )

    # Test invalid score
    with pytest.raises(ValidationError):
        PhysicsGradingResult(
            question=question,
            student_answer="答案",
            is_correct=True,
            score=150,  # Invalid: should be 0-100
            feedback="反馈"
        )


def test_physics_homework_session_model():
    """Test PhysicsHomeworkSession Pydantic model."""
    question = PhysicsQuestion(
        text="测试题目",
        question_type=PhysicsQuestionType.CALCULATION,
        category=PhysicsCategory.MECHANICS
    )

    grading_result = PhysicsGradingResult(
        question=question,
        student_answer="学生答案",
        is_correct=True,
        score=90.0,
        feedback="很好"
    )

    session_data = {
        "session_id": "session_123",
        "student_id": "student_456",
        "questions": [grading_result],
        "overall_score": 90.0,
        "completion_time": 45.5,
        "weak_areas": [],
        "recommendations": ["继续努力"]
    }

    session = PhysicsHomeworkSession(**session_data)
    assert session.session_id == "session_123"
    assert session.overall_score == 90.0
    assert len(session.questions) == 1


def test_physics_knowledge_mapping():
    """Test the PHYSICS_KNOWLEDGE_MAPPING structure."""
    # Test that all categories have knowledge points
    for category in PhysicsCategory:
        assert category in PHYSICS_KNOWLEDGE_MAPPING
        assert len(PHYSICS_KNOWLEDGE_MAPPING[category]) > 0

    # Test specific mappings
    mechanics_points = PHYSICS_KNOWLEDGE_MAPPING[PhysicsCategory.MECHANICS]
    assert PhysicsKnowledgePoint.NEWTON_LAWS in mechanics_points
    assert PhysicsKnowledgePoint.MOMENTUM_CONSERVATION in mechanics_points

    electromagnetics_points = PHYSICS_KNOWLEDGE_MAPPING[PhysicsCategory.ELECTROMAGNETICS]
    assert PhysicsKnowledgePoint.ELECTRIC_FIELD in electromagnetics_points
    assert PhysicsKnowledgePoint.MAGNETIC_FIELD in electromagnetics_points


def test_physics_question_minimal():
    """Test PhysicsQuestion with minimal required fields."""
    question = PhysicsQuestion(
        text="简单题目",
        question_type=PhysicsQuestionType.MULTIPLE_CHOICE,
        category=PhysicsCategory.OPTICS
    )

    assert question.text == "简单题目"
    assert question.knowledge_points == []  # Should default to empty list
    assert question.difficulty_level is None  # Should be optional
    assert question.answer is None  # Should be optional
    assert question.explanation is None  # Should be optional
