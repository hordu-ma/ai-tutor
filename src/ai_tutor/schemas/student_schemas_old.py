"""
学生相关的Pydantic schemas定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict


class GradeEnum(str, Enum):
    """年级枚举"""
    GRADE_7 = "初一"
    GRADE_8 = "初二"
    GRADE_9 = "初三"
    GRADE_10 = "高一"
    GRADE_11 = "高二"
    GRADE_12 = "高三"


class LearningStyleEnum(str, Enum):
    """学习风格枚举"""
    VISUAL = "视觉型"
    AUDITORY = "听觉型"
    KINESTHETIC = "动觉型"
    MIXED = "混合型"


class StudentBase(BaseModel):
    """学生基础信息模型"""
    name: str = Field(..., min_length=2, max_length=50, description="学生姓名")
    grade: GradeEnum = Field(..., description="年级")
    class_name: Optional[str] = Field(None, max_length=20, description="班级")
    student_id: Optional[str] = Field(None, max_length=30, description="学号")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="联系电话")
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', description="邮箱")
    parent_phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="家长电话")
    preferred_subjects: Optional[List[str]] = Field(default_factory=list, description="偏好科目列表")
    learning_style: Optional[LearningStyleEnum] = Field(None, description="学习风格")
    
    @validator('preferred_subjects')
    def validate_preferred_subjects(cls, v):
        """验证偏好科目"""
        if v:
            valid_subjects = ['math', 'physics', 'english', 'chemistry', 'biology', 'chinese']
            invalid_subjects = [s for s in v if s not in valid_subjects]
            if invalid_subjects:
                raise ValueError(f"无效的科目: {invalid_subjects}")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """验证学生姓名"""
        if not v or not v.strip():
            raise ValueError("学生姓名不能为空")
        # 检查是否包含中文或英文字符
        if not any('\u4e00' <= c <= '\u9fff' for c in v) and not any(c.isalpha() for c in v):
            raise ValueError("学生姓名必须包含中文或英文字符")
        return v.strip()
    
    model_config = ConfigDict(
        use_enum_values=True
    )
        json_schema_extra= {
            "example": {
                "name": "张小明",
                "grade": "初二",
                "class_name": "初二(3)班",
                "student_id": "2023001",
                "phone": "13812345678",
                "email": "zhangxiaoming@example.com",
                "parent_phone": "13987654321",
                "preferred_subjects": ["math", "physics"],
                "learning_style": "视觉型"
            }
        }


class StudentCreate(StudentBase):
    """创建学生请求模型"""
    pass


class StudentUpdate(BaseModel):
    """更新学生请求模型（所有字段都可选）"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="学生姓名")
    grade: Optional[GradeEnum] = Field(None, description="年级")
    class_name: Optional[str] = Field(None, max_length=20, description="班级")
    student_id: Optional[str] = Field(None, max_length=30, description="学号")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="联系电话")
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', description="邮箱")
    parent_phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="家长电话")
    preferred_subjects: Optional[List[str]] = Field(None, description="偏好科目列表")
    learning_style: Optional[LearningStyleEnum] = Field(None, description="学习风格")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
    @validator('name')
    def validate_name(cls, v):
        """验证学生姓名"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("学生姓名不能为空")
            if not any('\u4e00' <= c <= '\u9fff' for c in v) and not any(c.isalpha() for c in v):
                raise ValueError("学生姓名必须包含中文或英文字符")
            return v.strip()
        return v
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "name": "张小明",
                "grade": "初三",
                "class_name": "初三(1)班",
                "phone": "13812345679"
            }
        }
    )


class StudentResponse(StudentBase):
    """学生响应模型（包含系统字段）"""
    id: int = Field(..., description="学生ID")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(
        from_attributes=True,  # 允许从SQLAlchemy模型创建
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "张小明",
                "grade": "初二",
                "class_name": "初二(3)班",
                "student_id": "2023001",
                "phone": "13812345678",
                "email": "zhangxiaoming@example.com",
                "parent_phone": "13987654321",
                "preferred_subjects": ["math", "physics"],
                "learning_style": "视觉型",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    )


class SubjectProgress(BaseModel):
    """单个科目学习进度"""
    subject: str = Field(..., description="科目名称")
    mastery_rate: float = Field(..., ge=0.0, le=1.0, description="掌握率 (0-1)")
    total_questions: int = Field(default=0, ge=0, description="总题目数")
    correct_questions: int = Field(default=0, ge=0, description="正确题目数")
    recent_performance: float = Field(default=0.0, ge=0.0, le=1.0, description="最近表现")
    weak_knowledge_points: List[str] = Field(default_factory=list, description="薄弱知识点")
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "subject": "math",
                "mastery_rate": 0.75,
                "total_questions": 100,
                "correct_questions": 75,
                "recent_performance": 0.80,
                "weak_knowledge_points": ["一元二次方程", "函数图像"]
            }
        }


class LearningTrend(BaseModel):
    """学习趋势数据"""
    date: datetime = Field(..., description="日期")
    accuracy_rate: float = Field(..., ge=0.0, le=1.0, description="正确率")
    questions_count: int = Field(default=0, ge=0, description="题目数量")
    study_time_minutes: int = Field(default=0, ge=0, description="学习时长（分钟）")
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "date": "2024-01-01T12:00:00",
                "accuracy_rate": 0.80,
                "questions_count": 20,
                "study_time_minutes": 60
            }
        }


class StudentStats(BaseModel):
    """学生学习统计概览"""
    total_homework_sessions: int = Field(default=0, ge=0, description="总作业次数")
    total_questions_answered: int = Field(default=0, ge=0, description="总回答题目数")
    overall_accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="总体正确率")
    active_days: int = Field(default=0, ge=0, description="活跃天数")
    subjects_studied: List[str] = Field(default_factory=list, description="已学习科目")
    subject_progress: List[SubjectProgress] = Field(default_factory=list, description="各科目进度")
    recent_trends: List[LearningTrend] = Field(default_factory=list, description="最近学习趋势")
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "total_homework_sessions": 50,
                "total_questions_answered": 500,
                "overall_accuracy_rate": 0.78,
                "active_days": 30,
                "subjects_studied": ["math", "physics", "english"],
                "subject_progress": [
                    {
                        "subject": "math",
                        "mastery_rate": 0.75,
                        "total_questions": 200,
                        "correct_questions": 150,
                        "recent_performance": 0.80,
                        "weak_knowledge_points": ["一元二次方程"]
                    }
                ]
            }
        }


class StudentFilter(BaseModel):
    """学生查询过滤器"""
    name: Optional[str] = Field(None, description="姓名模糊搜索")
    grade: Optional[GradeEnum] = Field(None, description="年级筛选")
    class_name: Optional[str] = Field(None, description="班级筛选")
    is_active: Optional[bool] = Field(None, description="是否激活")
    has_homework: Optional[bool] = Field(None, description="是否有作业记录")
    min_accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="最低正确率")
    created_after: Optional[datetime] = Field(None, description="创建时间晚于")
    created_before: Optional[datetime] = Field(None, description="创建时间早于")
    
    model_config = ConfigDict(
        use_enum_values = True
        json_schema_extra= {
            "example": {
                "name": "张",
                "grade": "初二",
                "class_name": "初二(3)班",
                "is_active": True,
                "has_homework": True,
                "min_accuracy_rate": 0.6
            }
        }


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小")
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size


class StudentListResponse(BaseModel):
    """学生列表响应（支持分页）"""
    students: List[StudentResponse] = Field(default_factory=list, description="学生列表")
    total_count: int = Field(default=0, ge=0, description="总数量")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, description="每页大小")
    total_pages: int = Field(default=0, ge=0, description="总页数")
    has_next: bool = Field(default=False, description="是否有下一页")
    has_prev: bool = Field(default=False, description="是否有上一页")
    
    @staticmethod
    def create(
        students: List[StudentResponse], 
        total_count: int, 
        pagination: PaginationParams
    ) -> "StudentListResponse":
        """创建分页响应"""
        import math
        total_pages = math.ceil(total_count / pagination.page_size) if total_count > 0 else 0
        
        return StudentListResponse(
            students=students,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "students": [
                    {
                        "id": 1,
                        "name": "张小明",
                        "grade": "初二",
                        "class_name": "初二(3)班",
                        "is_active": True,
                        "created_at": "2024-01-01T12:00:00",
                        "updated_at": "2024-01-01T12:00:00"
                    }
                ],
                "total_count": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }


class StudentActivity(BaseModel):
    """学生最近活动记录"""
    activity_type: str = Field(..., description="活动类型")
    activity_date: datetime = Field(..., description="活动时间")
    subject: Optional[str] = Field(None, description="相关科目")
    description: str = Field(..., description="活动描述")
    performance: Optional[float] = Field(None, ge=0.0, le=1.0, description="表现评分")
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "activity_type": "homework_completion",
                "activity_date": "2024-01-01T12:00:00",
                "subject": "math",
                "description": "完成数学作业，正确率80%",
                "performance": 0.80
            }
        }


class StudentDetailResponse(StudentResponse):
    """学生详细信息响应（包含统计数据）"""
    stats: StudentStats = Field(default_factory=StudentStats, description="学习统计")
    recent_activities: List[StudentActivity] = Field(default_factory=list, description="最近活动")
    
    model_config = ConfigDict(
        from_attributes = True
        use_enum_values = True
