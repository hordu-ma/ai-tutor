"""
知识点和学习进度相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..db.database import Base


class KnowledgePoint(Base):
    """知识点模型"""
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, index=True)
    
    # 知识点基本信息
    name = Column(String(200), nullable=False, comment="知识点名称")
    code = Column(String(50), unique=True, index=True, comment="知识点编码")
    subject = Column(String(50), nullable=False, comment="所属科目")
    grade_level = Column(String(20), comment="适用年级")
    
    # 知识点层级结构
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), comment="父级知识点ID")
    level = Column(Integer, default=1, comment="层级深度")
    path = Column(String(500), comment="知识点路径")
    
    # 知识点内容
    description = Column(Text, comment="知识点描述")
    keywords = Column(JSON, comment="关键词列表")
    difficulty_level = Column(Integer, default=1, comment="难度等级（1-5）")
    
    # 学习资源
    learning_materials = Column(JSON, comment="学习资料链接")
    practice_tips = Column(Text, comment="练习建议")
    common_mistakes = Column(JSON, comment="常见错误列表")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    parent = relationship("KnowledgePoint", remote_side=[id], backref="children")
    progresses = relationship("KnowledgeProgress", back_populates="knowledge_point")

    def __repr__(self):
        return f"<KnowledgePoint(id={self.id}, name='{self.name}', subject='{self.subject}')>"


class KnowledgeProgress(Base):
    """学生知识点掌握进度模型"""
    __tablename__ = "knowledge_progresses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    
    # 掌握程度
    mastery_level = Column(Float, default=0.0, comment="掌握程度（0.0-1.0）")
    confidence_score = Column(Float, default=0.0, comment="置信度分数")
    
    # 练习统计
    total_attempts = Column(Integer, default=0, comment="总练习次数")
    correct_attempts = Column(Integer, default=0, comment="正确次数")
    accuracy_rate = Column(Float, default=0.0, comment="正确率")
    
    # 错误分析
    common_errors = Column(JSON, comment="常见错误类型统计")
    error_patterns = Column(JSON, comment="错误模式分析")
    
    # 学习建议
    improvement_suggestions = Column(JSON, comment="提升建议")
    recommended_exercises = Column(JSON, comment="推荐练习")
    
    # 时间信息
    last_practiced_at = Column(DateTime, comment="最后练习时间")
    first_learned_at = Column(DateTime, comment="首次学习时间")
    mastery_achieved_at = Column(DateTime, comment="掌握达成时间")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    student = relationship("Student", back_populates="knowledge_progresses")
    knowledge_point = relationship("KnowledgePoint", back_populates="progresses")

    def __repr__(self):
        return f"<KnowledgeProgress(student_id={self.student_id}, knowledge_point_id={self.knowledge_point_id}, mastery={self.mastery_level})>"


class ErrorPattern(Base):
    """错误模式分析模型"""
    __tablename__ = "error_patterns"

    id = Column(Integer, primary_key=True, index=True)
    
    # 错误模式基本信息
    pattern_name = Column(String(200), nullable=False, comment="错误模式名称")
    pattern_type = Column(String(100), comment="错误类型")
    subject = Column(String(50), nullable=False, comment="科目")
    
    # 错误描述
    description = Column(Text, comment="错误模式描述")
    typical_mistakes = Column(JSON, comment="典型错误示例")
    root_causes = Column(JSON, comment="根本原因分析")
    
    # 解决方案
    correction_strategies = Column(JSON, comment="纠正策略")
    practice_recommendations = Column(JSON, comment="练习建议")
    prevention_tips = Column(Text, comment="预防提示")
    
    # 统计信息
    occurrence_count = Column(Integer, default=0, comment="出现次数")
    affected_students_count = Column(Integer, default=0, comment="影响学生数")
    
    # 关联知识点
    related_knowledge_points = Column(JSON, comment="相关知识点ID列表")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ErrorPattern(id={self.id}, name='{self.pattern_name}', subject='{self.subject}')>"
