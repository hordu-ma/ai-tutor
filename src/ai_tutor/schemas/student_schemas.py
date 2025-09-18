"""
学生相关数据模型
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class GradeEnum(str, Enum):
    """年级枚举"""

    GRADE_7 = "初一"
    GRADE_8 = "初二"
    GRADE_9 = "初三"
    GRADE_10 = "高一"
    GRADE_11 = "高二"
    GRADE_12 = "高三"


class StudentBase(BaseModel):
    """学生基础信息模型"""

    name: str = Field(..., min_length=2, max_length=50)
    grade: GradeEnum
    class_name: Optional[str] = Field(None, max_length=20)
    student_id: Optional[str] = Field(None, max_length=30)
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    email: Optional[str] = None
    parent_phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    preferred_subjects: Optional[List[str]] = Field(default_factory=list)
    learning_style: Optional[str] = None


class StudentCreate(StudentBase):
    """创建学生请求模型"""

    pass


class StudentUpdate(BaseModel):
    """更新学生请求模型"""

    name: Optional[str] = Field(None, min_length=2, max_length=50)
    grade: Optional[GradeEnum] = None
    class_name: Optional[str] = Field(None, max_length=20)
    student_id: Optional[str] = Field(None, max_length=30)
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    email: Optional[str] = None
    parent_phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    preferred_subjects: Optional[List[str]] = None
    learning_style: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """学生响应模型"""

    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class StudentFilter(BaseModel):
    """学生查询过滤器"""

    name: Optional[str] = None
    grade: Optional[GradeEnum] = None
    class_name: Optional[str] = None
    is_active: Optional[bool] = None
    has_homework: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class PaginationParams(BaseModel):
    """分页参数"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class StudentListResponse(BaseModel):
    """学生列表响应"""

    students: List[StudentResponse] = Field(default_factory=list)
    total_count: int = Field(default=0, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)
    total_pages: int = Field(default=0, ge=0)
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)

    @staticmethod
    def create(students, total_count, pagination):
        import math

        total_pages = (
            math.ceil(total_count / pagination.page_size) if total_count > 0 else 0
        )
        return StudentListResponse(
            students=students,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1,
        )


# 简化的统计相关模型
class SubjectProgress(BaseModel):
    """科目学习进度"""

    subject: str
    mastery_rate: float = Field(ge=0.0, le=1.0)
    total_questions: int = Field(default=0, ge=0)
    correct_questions: int = Field(default=0, ge=0)
    recent_performance: float = Field(default=0.0, ge=0.0, le=1.0)
    weak_knowledge_points: List[str] = Field(default_factory=list)


class LearningTrend(BaseModel):
    """学习趋势数据"""

    date: datetime
    accuracy_rate: float = Field(ge=0.0, le=1.0)
    practice_count: int = Field(default=0, ge=0)
    average_score: float = Field(default=0.0, ge=0.0)
    study_time_minutes: int = Field(default=0, ge=0)


class StudentStats(BaseModel):
    """学生学习统计"""

    total_homework_sessions: int = Field(default=0, ge=0)
    total_questions_answered: int = Field(default=0, ge=0)
    overall_accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    active_days: int = Field(default=0, ge=0)
    subjects_studied: List[str] = Field(default_factory=list)
    subject_progress: List[SubjectProgress] = Field(default_factory=list)
    recent_trends: List[LearningTrend] = Field(default_factory=list)


class StudentActivity(BaseModel):
    """学生活动记录"""

    activity_type: str
    activity_date: datetime
    subject: Optional[str] = None
    description: str
    performance: Optional[float] = Field(None, ge=0.0, le=1.0)


class HomeworkSubmission(BaseModel):
    """作业提交记录"""

    id: int
    student_id: int
    subject: str
    submission_date: datetime
    total_questions: int = Field(default=0, ge=0)
    correct_answers: int = Field(default=0, ge=0)
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    total_score: float = Field(default=0.0, ge=0.0)
    max_score: float = Field(default=100.0, ge=0.0)
    grade_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    difficulty_level: int = Field(default=3, ge=1, le=5)
    ai_provider: Optional[str] = Field(None, max_length=50)
    ocr_text: Optional[str] = None
    processing_time: Optional[float] = Field(None, ge=0.0)
    feedback: Optional[str] = None
    weak_knowledge_points: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    error_types: List[str] = Field(default_factory=list)
    is_completed: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HomeworkHistoryResponse(BaseModel):
    """作业历史响应"""

    submissions: List[HomeworkSubmission] = Field(default_factory=list)
    total_count: int = Field(default=0, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)
    total_pages: int = Field(default=0, ge=0)
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)

    @staticmethod
    def create(submissions: List[HomeworkSubmission], total_count: int, pagination: PaginationParams) -> "HomeworkHistoryResponse":
        import math

        total_pages = math.ceil(total_count / pagination.page_size) if total_count > 0 else 0
        return HomeworkHistoryResponse(
            submissions=submissions,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1,
        )


class StudentDetailResponse(StudentResponse):
    """学生详细信息响应"""

    stats: StudentStats = Field(default_factory=StudentStats)
    recent_activities: List[StudentActivity] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
