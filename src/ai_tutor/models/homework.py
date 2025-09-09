"""
作业相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..db.database import Base


class SubjectEnum(enum.Enum):
    """科目枚举"""
    MATH = "math"
    ENGLISH = "english"
    CHINESE = "chinese"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"


class HomeworkStatusEnum(enum.Enum):
    """作业状态枚举"""
    PENDING = "pending"        # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    ERROR = "error"           # 处理错误


class HomeworkSession(Base):
    """作业会话模型"""
    __tablename__ = "homework_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # 作业基本信息
    title = Column(String(200), comment="作业标题")
    subject = Column(Enum(SubjectEnum), nullable=False, comment="科目")
    status = Column(Enum(HomeworkStatusEnum), default=HomeworkStatusEnum.PENDING, comment="状态")
    
    # 图片和OCR信息
    image_url = Column(String(500), comment="原始图片URL")
    ocr_text = Column(Text, comment="OCR识别的原始文本")
    ocr_confidence = Column(Float, comment="OCR识别置信度")
    
    # AI批改结果
    ai_response = Column(Text, comment="AI批改原始响应")
    correction_result = Column(JSON, comment="结构化批改结果")
    overall_score = Column(Float, comment="总体得分")
    
    # 处理信息
    processing_time = Column(Float, comment="处理耗时（秒）")
    error_message = Column(Text, comment="错误信息")
    ai_provider = Column(String(50), default="qwen", comment="使用的AI服务商")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, comment="完成时间")
    
    # 关系
    student = relationship("Student", back_populates="homework_sessions")
    questions = relationship("Question", back_populates="homework_session")

    def __repr__(self):
        return f"<HomeworkSession(id={self.id}, subject='{self.subject}', status='{self.status}')>"


class Question(Base):
    """题目模型"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    homework_session_id = Column(Integer, ForeignKey("homework_sessions.id"), nullable=False)
    
    # 题目内容
    question_number = Column(Integer, comment="题目序号")
    question_text = Column(Text, comment="题目原文")
    question_type = Column(String(50), comment="题目类型（选择题、填空题、计算题等）")
    
    # 学生答案
    student_answer = Column(Text, comment="学生答案")
    student_answer_image = Column(String(500), comment="学生答案图片URL")
    
    # 标准答案和批改
    correct_answer = Column(Text, comment="正确答案")
    is_correct = Column(Boolean, comment="答案是否正确")
    score = Column(Float, comment="得分")
    max_score = Column(Float, comment="满分")
    
    # AI分析结果
    error_analysis = Column(Text, comment="错误分析")
    solution_steps = Column(JSON, comment="解题步骤")
    knowledge_points = Column(JSON, comment="涉及的知识点")
    difficulty_level = Column(Integer, comment="难度等级（1-5）")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    homework_session = relationship("HomeworkSession", back_populates="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, number={self.question_number}, is_correct={self.is_correct})>"
