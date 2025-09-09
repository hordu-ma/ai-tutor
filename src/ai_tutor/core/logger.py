"""
应用日志配置模块
"""
import logging
import structlog
from typing import Dict, Any
from .config import settings


def configure_logging() -> None:
    """配置结构化日志"""
    
    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=None,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )

    # 配置structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)


class LoggerMixin:
    """日志混合类，为其他类提供日志功能"""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """获取日志记录器"""
        return get_logger(self.__class__.__name__)
    
    def log_event(self, event: str, **kwargs) -> None:
        """记录事件日志"""
        self.logger.info(event, **kwargs)
    
    def log_error(self, error: str, **kwargs) -> None:
        """记录错误日志"""
        self.logger.error(error, **kwargs)
    
    def log_warning(self, warning: str, **kwargs) -> None:
        """记录警告日志"""
        self.logger.warning(warning, **kwargs)
