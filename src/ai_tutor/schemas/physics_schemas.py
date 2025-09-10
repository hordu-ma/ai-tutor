"""
Physics-related schemas for the AI Tutor system.

This module defines Pydantic models and enums specific to physics questions,
knowledge points, and related data structures.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PhysicsCategory(str, Enum):
    """
    Enumeration of physics knowledge categories.
    """
    MECHANICS = "力学"
    ELECTROMAGNETICS = "电磁学"
    THERMODYNAMICS = "热学"
    OPTICS = "光学"
    ATOMIC_PHYSICS = "原子物理"
    WAVE_PHYSICS = "波动"


class PhysicsQuestionType(str, Enum):
    """
    Enumeration of physics question types.
    """
    MULTIPLE_CHOICE = "选择题"
    FILL_IN_BLANK = "填空题"
    CALCULATION = "计算题"
    PROOF = "证明题"
    EXPERIMENT = "实验题"
    DIAGRAM = "作图题"
    SHORT_ANSWER = "简答题"


class PhysicsKnowledgePoint(str, Enum):
    """
    Enumeration of specific physics knowledge points.
    Organized by category for easy reference.
    """
    # 力学
    NEWTON_LAWS = "牛顿运动定律"
    MOMENTUM_CONSERVATION = "动量守恒"
    ENERGY_CONSERVATION = "机械能守恒"
    CIRCULAR_MOTION = "圆周运动"
    OSCILLATION = "振动"

    # 电磁学
    ELECTRIC_FIELD = "电场"
    MAGNETIC_FIELD = "磁场"
    ELECTROMAGNETIC_INDUCTION = "电磁感应"
    ELECTRIC_CURRENT = "电流"
    CAPACITOR = "电容器"

    # 热学
    THERMODYNAMICS_FIRST_LAW = "热力学第一定律"
    IDEAL_GAS_LAW = "理想气体状态方程"
    HEAT_TRANSFER = "热传递"
    KINETIC_THEORY = "分子动理论"

    # 光学
    GEOMETRIC_OPTICS = "几何光学"
    WAVE_OPTICS = "物理光学"
    INTERFERENCE = "干涉"
    DIFFRACTION = "衍射"

    # 原子物理
    PHOTOELECTRIC_EFFECT = "光电效应"
    ATOMIC_STRUCTURE = "原子结构"
    NUCLEAR_PHYSICS = "核物理"

    # 波动
    MECHANICAL_WAVES = "机械波"
    ELECTROMAGNETIC_WAVES = "电磁波"
    WAVE_EQUATION = "波动方程"


class PhysicsQuestion(BaseModel):
    """
    Schema for a physics question.
    """
    text: str = Field(..., description="题目文本内容")
    question_type: PhysicsQuestionType = Field(..., description="题目类型")
    category: PhysicsCategory = Field(..., description="物理分类")
    knowledge_points: List[PhysicsKnowledgePoint] = Field(
        default_factory=list, description="涉及的知识点"
    )
    difficulty_level: Optional[int] = Field(
        None, ge=1, le=5, description="难度等级 (1-5)"
    )
    answer: Optional[str] = Field(None, description="参考答案")
    explanation: Optional[str] = Field(None, description="解题思路")


class PhysicsGradingResult(BaseModel):
    """
    Schema for physics question grading results.
    """
    question: PhysicsQuestion = Field(..., description="题目信息")
    student_answer: str = Field(..., description="学生答案")
    is_correct: bool = Field(..., description="是否正确")
    score: float = Field(..., ge=0, le=100, description="得分 (0-100)")
    feedback: str = Field(..., description="批改反馈")
    knowledge_gaps: List[PhysicsKnowledgePoint] = Field(
        default_factory=list, description="知识薄弱点"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="学习建议"
    )


class PhysicsHomeworkSession(BaseModel):
    """
    Schema for a physics homework grading session.
    """
    session_id: str = Field(..., description="批改会话ID")
    student_id: Optional[str] = Field(None, description="学生ID")
    questions: List[PhysicsGradingResult] = Field(
        default_factory=list, description="题目批改结果"
    )
    overall_score: float = Field(..., ge=0, le=100, description="总体得分")
    completion_time: Optional[float] = Field(
        None, description="完成时间（分钟）"
    )
    weak_areas: List[PhysicsCategory] = Field(
        default_factory=list, description="薄弱知识领域"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="学习建议"
    )


# Knowledge point mapping for easy lookup
PHYSICS_KNOWLEDGE_MAPPING = {
    PhysicsCategory.MECHANICS: [
        PhysicsKnowledgePoint.NEWTON_LAWS,
        PhysicsKnowledgePoint.MOMENTUM_CONSERVATION,
        PhysicsKnowledgePoint.ENERGY_CONSERVATION,
        PhysicsKnowledgePoint.CIRCULAR_MOTION,
        PhysicsKnowledgePoint.OSCILLATION,
    ],
    PhysicsCategory.ELECTROMAGNETICS: [
        PhysicsKnowledgePoint.ELECTRIC_FIELD,
        PhysicsKnowledgePoint.MAGNETIC_FIELD,
        PhysicsKnowledgePoint.ELECTROMAGNETIC_INDUCTION,
        PhysicsKnowledgePoint.ELECTRIC_CURRENT,
        PhysicsKnowledgePoint.CAPACITOR,
    ],
    PhysicsCategory.THERMODYNAMICS: [
        PhysicsKnowledgePoint.THERMODYNAMICS_FIRST_LAW,
        PhysicsKnowledgePoint.IDEAL_GAS_LAW,
        PhysicsKnowledgePoint.HEAT_TRANSFER,
        PhysicsKnowledgePoint.KINETIC_THEORY,
    ],
    PhysicsCategory.OPTICS: [
        PhysicsKnowledgePoint.GEOMETRIC_OPTICS,
        PhysicsKnowledgePoint.WAVE_OPTICS,
        PhysicsKnowledgePoint.INTERFERENCE,
        PhysicsKnowledgePoint.DIFFRACTION,
    ],
    PhysicsCategory.ATOMIC_PHYSICS: [
        PhysicsKnowledgePoint.PHOTOELECTRIC_EFFECT,
        PhysicsKnowledgePoint.ATOMIC_STRUCTURE,
        PhysicsKnowledgePoint.NUCLEAR_PHYSICS,
    ],
    PhysicsCategory.WAVE_PHYSICS: [
        PhysicsKnowledgePoint.MECHANICAL_WAVES,
        PhysicsKnowledgePoint.ELECTROMAGNETIC_WAVES,
        PhysicsKnowledgePoint.WAVE_EQUATION,
    ],
}
