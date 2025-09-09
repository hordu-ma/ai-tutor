# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 项目简介

AI Tutor 是基于AI的中学生数学和英语学情管理系统。通过OCR识别作业内容，AI批改和知识点分析，为学生提供个性化的学习建议。

## 核心架构

### 技术栈
- **后端**: FastAPI + Python 3.12
- **包管理**: uv (符合用户规则中的 Python 管理偏好)
- **OCR**: Tesseract (支持中文简体+英文)
- **AI服务**: 通义千问 (Qwen) / Kimi
- **数据库**: PostgreSQL + Redis
- **日志**: structlog (结构化日志)

### 分层架构
```
src/ai_tutor/
├── api/v1/           # API路由层 (FastAPI endpoints)
├── services/         # 业务逻辑层
│   ├── ocr/          # OCR服务抽象 (TesseractOCR)
│   ├── llm/          # AI服务抽象 (QwenService, KimiService)
│   └── student/      # 学生相关服务 (HomeworkService)
├── models/           # 数据模型层 (SQLAlchemy)
├── schemas/          # API模型 (Pydantic)
├── core/             # 核心配置 (config.py, logger.py)
└── db/               # 数据库连接
```

### 数据模型关系
- `Student` -> `HomeworkSession` (一对多)
- `HomeworkSession` -> `Question` (一对多)
- 支持多科目: 数学、英语、物理、化学等

## 常用开发命令

### 环境管理 (使用 uv)
```bash
# 安装依赖
uv sync

# 设置开发环境 (创建 .env 文件)
make setup-dev
```

### 开发服务器
```bash
# 启动开发服务器
make dev
# 或
uv run uvicorn src.ai_tutor.main:app --reload --host 0.0.0.0 --port 8000

# 测试端口启动
make dev-test  # 端口 8001
```

### 测试
```bash
# 运行所有测试
make test
# 或
uv run pytest -v

# 测试覆盖率
make test-cov

# 端到端测试 (测试完整批改流程)
uv run python scripts/test_full_flow.py
```

### 代码质量
```bash
# 格式化
make format  # black

# 检查格式
make format-check

# 代码检查
make lint  # flake8 + mypy
```

### 服务健康检查
```bash
# 检查所有服务
make health

# API快速测试
make api-test

# 测试核心服务
make test-services
```

## 核心服务接口

### OCR服务 (`services/ocr/base.py`)
- **抽象基类**: `OCRService`
- **实现**: `TesseractOCR`
- **工厂函数**: `get_ocr_service()`
- **特性**: 异步处理、图片预处理、支持中英文

### LLM服务 (`services/llm/base.py`)
- **抽象基类**: `LLMService`
- **实现**: `QwenService`, `KimiService`
- **工厂函数**: `get_llm_service(provider="qwen")`
- **接口**: `chat()`, `generate()`

### 作业批改服务 (`services/student/homework_service.py`)
- **核心类**: `HomeworkService`
- **核心方法**: `grade_homework(image, subject)`
- **流程**: OCR → AI分析 → 结构化结果

## API 端点

### 主要路由
- `GET /` - 主页 (static/index.html)
- `GET /health` - 应用健康检查
- `GET /api/v1/health` - API健康检查

### OCR服务
- `POST /api/v1/ocr/extract` - 图片文本提取
- `GET /api/v1/ocr/health` - OCR服务健康检查

### 作业批改
- `POST /api/v1/homework/grade` - 作业批改
- `GET /api/v1/homework/health` - 批改服务健康检查

## 配置和环境变量

### 必需配置 (.env)
```bash
# AI服务
QWEN_API_KEY=your_qwen_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# 数据库
DATABASE_URL=postgresql://user:pass@localhost/ai_tutor
REDIS_URL=redis://localhost:6379/0

# 其他
SECRET_KEY=your_secret_key_here
OCR_ENGINE=tesseract  # 或 paddleocr
DEBUG=True
LOG_LEVEL=INFO
```

### OCR 依赖安装
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian  
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

## 开发注意事项

### 日志使用
- 使用 `get_logger(__name__)` 获取结构化日志器
- 所有服务继承 `LoggerMixin` 获得日志能力
- 中文输出，符合用户规则偏好

### 错误处理
- 服务层使用抽象基类和工厂模式
- API层统一异常处理和响应格式
- 健康检查端点监控各服务状态

### 异步模式
- 所有I/O操作使用异步 (`async/await`)
- OCR和LLM服务支持异步调用
- FastAPI原生异步支持

### 测试策略
- 单元测试覆盖核心逻辑
- `scripts/test_full_flow.py` 提供端到端测试
- 创建测试图片进行完整流程验证

## 项目状态

### MVP 阶段 (当前)
- ✅ 项目架构和基础设施
- ✅ OCR文本提取功能
- 🔄 AI服务集成 (通义千问/Kimi)
- 🔄 作业批改基础功能

### 下一步开发
- 知识点提取和分类
- 学生学情数据管理
- RAG系统实现
- 前端界面完善
