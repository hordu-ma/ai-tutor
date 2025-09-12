"""
FastAPI依赖注入配置
"""
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from ..db.database import get_db
from ..services.student.student_service import StudentService


def get_student_service(db: Session = Depends(get_db)) -> StudentService:
    """获取学生管理服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        StudentService: 学生管理服务实例
    """
    return StudentService(db)
