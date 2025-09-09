"""
数据库连接和会话配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import redis
from typing import Generator

from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 在调试模式下打印SQL语句
    pool_pre_ping=True,   # 在每次连接前测试连接
    pool_recycle=3600,    # 每小时回收连接池
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# Redis连接
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()  # 测试连接
    logger.info("Redis连接成功", redis_url=settings.REDIS_URL)
except Exception as e:
    logger.warning("Redis连接失败", error=str(e))
    redis_client = None


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """获取数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    logger.info("初始化数据库...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化完成")


def get_redis() -> redis.Redis:
    """获取Redis客户端"""
    if redis_client is None:
        raise Exception("Redis未连接")
    return redis_client
