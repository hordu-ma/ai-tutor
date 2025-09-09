#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
import os

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai_tutor.db.database import init_db, engine
from src.ai_tutor.models import *  # 导入所有模型
from src.ai_tutor.core.logger import get_logger

logger = get_logger(__name__)


def main():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 检查数据库连接
        with engine.connect() as conn:
            logger.info("数据库连接测试成功")
        
        # 创建所有表
        init_db()
        
        logger.info("数据库初始化完成！")
        
        # 可选：创建一些基础数据
        create_sample_data()
        
    except Exception as e:
        logger.error("数据库初始化失败", error=str(e))
        raise


def create_sample_data():
    """创建示例数据"""
    from src.ai_tutor.db.database import SessionLocal
    from src.ai_tutor.models import Student, KnowledgePoint, SubjectEnum
    
    try:
        db = SessionLocal()
        
        # 检查是否已有数据
        if db.query(Student).first():
            logger.info("数据库中已有数据，跳过示例数据创建")
            return
        
        logger.info("创建示例数据...")
        
        # 创建示例学生
        sample_student = Student(
            name="张三",
            grade="初二",
            class_name="2班",
            student_id="20240001",
            preferred_subjects=["math", "english"]
        )
        db.add(sample_student)
        
        # 创建一些基础知识点
        math_root = KnowledgePoint(
            name="初中数学",
            code="MATH_ROOT",
            subject="math",
            grade_level="初中",
            level=1,
            description="初中数学知识点根节点"
        )
        db.add(math_root)
        
        db.commit()
        logger.info("示例数据创建完成")
        
    except Exception as e:
        logger.error("示例数据创建失败", error=str(e))
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
