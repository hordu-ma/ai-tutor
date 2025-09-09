"""
学生相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..db.database import Base


class Student(Base):
    """学生模型"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="学生姓名")
    grade = Column(String(20), nullable=False, comment="年级")
    class_name = Column(String(50), comment="班级")
    student_id = Column(String(50), unique=True, index=True, comment="学号")
    
    # 联系信息
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    parent_phone = Column(String(20), comment="家长电话")
    
    # 学习偏好和设置
    preferred_subjects = Column(JSON, comment="偏好科目列表")
    learning_style = Column(String(50), comment="学习风格")
    
    # 状态和元数据
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    homework_sessions = relationship("HomeworkSession", back_populates="student")
    knowledge_progresses = relationship("KnowledgeProgress", back_populates="student")

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', grade='{self.grade}')>"
