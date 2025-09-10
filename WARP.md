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
│   │   └── prompts/  # 提示词模板系统 (科目化、版本化)
│   ├── parsing/      # 题目解析服务 (QuestionParser, TextAnalyzer)
│   ├── knowledge/    # 知识点提取服务 (KnowledgeExtractor)
│   └── student/      # 学生相关服务 (HomeworkService)
├── models/           # 数据模型层 (SQLAlchemy)
├── schemas/          # API模型 (Pydantic)
├── core/             # 核心配置 (config.py, logger.py)
├── db/               # 数据库连接
└── tests/            # 测试模块
    ├── integration/  # 集成测试
    ├── unit/         # 单元测试
    └── fixtures/     # 测试数据
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

# 题目解析功能测试
uv run python scripts/test_question_parsing.py
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
- **接口**: `chat()`, `generate()`, `safe_json_parse()`
- **增强功能**: JSON解析容错、多级降级策略

### 提示词系统 (`services/llm/prompts/`)
- **基类**: `BaseGradingPrompts`, `PromptTemplate`
- **科目实现**: `MathGradingPrompts`, `PhysicsGradingPrompts`
- **版本管理**: `PromptVersion` (支持v1.0, v1.1, v2.0)
- **A/B测试**: `PromptManager` (支持流量分配)

### 题目解析服务 (`services/parsing/`)
- **题目解析器**: `QuestionParser`
  - 支持多种编号格式: 1. 一、(1) 等
  - 题目类型识别: 选择题、填空题、计算题等
  - 答案区域检测和提取
- **文本分析器**: `TextAnalyzer`
  - OCR质量评估、复杂度分析
  - 科目检测、年级估算
  - 数学内容识别和结构分析

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

### 🎉 第一阶段完成 (2025-09-10)
在第一阶段开发中，我们显著提升了系统的可靠性和功能性：

#### ✅ 已完成的核心改进
1. **环境准备和依赖验证** - 确保开发环境稳定
2. **端到端测试验证** - 确认系统MVP功能完整可用
3. **AI服务集成测试** - 建立了完善的测试框架，包含错误处理和并发测试
4. **优化提示词工程** - 实现了科目化、版本化的提示词管理系统，支持A/B测试
5. **增强JSON解析容错机制** - 大幅提升了AI响应解析的稳定性，支持多级降级策略
6. **完善题目识别和结构化解析** - 实现智能题目解析和文本分析功能

#### 📊 系统升级效果
- **稳定的AI服务集成** - 支持错误处理、超时重试  
- **智能提示词系统** - 科目化模板、版本管理、A/B测试支持
- **强大的容错机制** - 多级JSON解析，降级策略完善
- **完整的测试框架** - 集成测试、端到端测试、健康检查
- **智能题目解析** - 支持多种编号格式、类型识别、答案提取
- **文本深度分析** - OCR质量评估、复杂度分析、科目检测

### 🎯 下一阶段开发计划 (优先级排序)

#### 高优先级 - 即将开发
1. **知识点提取和分类系统** (步骤7 - 部分完成)
   - ✅ 创建 `src/ai_tutor/services/knowledge/` 目录
   - 🔄 实现 `KnowledgeExtractor` 基类
   - 🔄 为数学、英语、物理创建知识点映射表
   - 🔄 实现基于题目内容的知识点自动标注
   - 🔄 添加知识点层级结构（章节-知识点-子知识点）

2. **物理科目批改支持完善** (步骤8)
   - 在 `src/ai_tutor/schemas/` 添加 `physics_schemas.py`
   - 创建物理题目类型枚举（力学、电学、光学等）
   - 实现物理公式识别和验证逻辑
   - 添加物理单位检查和换算功能

3. **测试和文档完善** (步骤9)
   - 准备真实作业图片（数学、英语、物理各3张）
   - 运行完整批改流程测试，记录准确率
   - 执行 `make test-cov` 确保测试覆盖率达标
   - 更新 README.md 添加新功能说明
   - 创建 CHANGELOG.md 记录所有改进

#### 中优先级 - 后续开发
4. **学生学情数据管理**
   - 完善Student和HomeworkSession数据模型
   - 实现学生学习记录的持久化
   - 添加学情分析和进度跟踪

5. **RAG系统实现**
   - 集成向量数据库存储知识点
   - 实现基于历史数据的个性化建议
   - 构建智能推荐系统

6. **前端界面完善**
   - 改进static/index.html用户界面
   - 添加批改结果展示组件
   - 实现实时批改状态反馈

### 📝 开发备注
- **当前系统状态**: MVP+ 水平，具备稳定的OCR、多科目批改、智能容错和降级能力
- **最后中断点**: 步骤7 开始实现知识点提取系统，已创建目录结构
- **重要改进**: JSON解析容错、题目智能解析、提示词系统化显著提升了系统可靠性
