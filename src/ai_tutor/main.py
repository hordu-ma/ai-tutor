"""
FastAPI主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from .core.config import settings
from .core.logger import configure_logging, get_logger
from .api.v1 import router as api_v1_router

# 配置日志
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")

    # 启动时的初始化逻辑
    # TODO: 初始化数据库连接池
    # TODO: 初始化Redis连接
    # TODO: 加载AI模型配置

    yield

    # 关闭时的清理逻辑
    logger.info("应用关闭中...")
    # TODO: 关闭数据库连接
    # TODO: 关闭Redis连接


# 创建FastAPI应用实例
app = FastAPI(
    title="AI Tutor - 学情管理AI助教",
    description="基于AI的中学生数学和英语学情管理系统",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(api_v1_router, prefix="/api/v1")

# 根路径返回简单的HTML页面
@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径页面"""
    # 返回静态文件中的主页
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/favicon.ico")
async def favicon():
    """favicon.ico重定向到静态文件"""
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.ai_tutor.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
