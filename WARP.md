# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 项目概述

AI Tutor 是一个基于AI的中学生学情管理系统，支持数学、物理和英语作业的智能批改和学习分析。通过OCR识别作业内容，结合AI大模型进行题目解析和批改，为学生提供个性化的学习建议和知识点分析。

### 技术栈

- **后端框架**: FastAPI + Python 3.12+
- **包管理器**: uv (高性能Python包管理器)
- **OCR引擎**: Tesseract OCR (支持中英文识别)
- **AI服务**: 通义千问(Qwen) / Kimi API
- **数据库**: PostgreSQL + Redis
- **测试框架**: pytest + pytest-cov + pytest-asyncio
- **代码质量**: black + flake8 + mypy
- **容器化**: Docker + Docker Compose

### 项目特点

- **分层架构设计**: API层、服务层、数据层清晰分离
- **多AI服务支持**: 可配置切换不同AI提供商
- **科目化处理**: 针对数学、物理、英语的专业化批改算法
- **容错机制**: JSON解析容错、多级降级策略
- **异步处理**: 全面支持异步I/O操作
- **结构化日志**: 基于structlog的结构化日志系统

## 🚀 快速开始

### 环境准备

1. **Python 3.12+** - 项目基础运行环境
2. **uv包管理器** - 项目依赖管理
   ```bash
   # macOS
   brew install uv
   # 或
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Tesseract OCR** - 图像文字识别引擎
   ```bash
   # macOS
   brew install tesseract tesseract-lang
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
   ```

### 项目初始化

```bash
# 1. 克隆仓库
git clone <repository-url>
cd ai-tutor

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置API密钥：
# QWEN_API_KEY=your_api_key
# KIMI_API_KEY=your_api_key

# 4. 验证安装
uv run python -c "from src.ai_tutor.core.config import settings; print('配置成功')"
```

### 启动开发服务器

```bash
# 标准启动（推荐）
make dev

# 或手动启动
uv run uvicorn src.ai_tutor.main:app --reload --host 0.0.0.0 --port 8000

# 稳定模式（无reload，用于调试）
make dev-stable
```

### 访问服务

- **主页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **作业批改API**: http://localhost:8000/api/v1/homework/grade

## 🔧 常用开发命令

### 开发运行
```bash
make dev              # 启动开发服务器（热重载）
make dev-stable       # 启动开发服务器（稳定模式）
make dev-debug        # 调试模式启动
make health           # 服务健康检查
```

### 测试命令
```bash
make test             # 运行所有测试
make test-cov         # 运行测试并生成覆盖率报告
uv run pytest -v     # 详细测试输出
uv run pytest tests/unit/  # 运行单元测试
uv run pytest tests/integration/  # 运行集成测试
```

### 代码质量
```bash
make format           # 代码格式化 (black)
make format-check     # 检查代码格式（不修改）
make lint             # 代码质量检查 (flake8 + mypy)
uv run black src/ tests/         # 手动格式化
uv run flake8 src/ tests/        # 手动检查语法
uv run mypy src/                 # 手动类型检查
```

### 项目管理
```bash
make install          # 安装/更新依赖
make clean            # 清理缓存文件
uv sync               # 同步依赖（更安全的install）
uv add <package>      # 添加新依赖
uv remove <package>   # 移除依赖
```

### Docker操作
```bash
make docker-up        # 启动Docker服务
make docker-down      # 停止Docker服务
make docker-restart   # 重启Docker服务
make docker-logs      # 查看服务日志
```

## 🏗️ 项目架构

### 分层架构设计

```
src/ai_tutor/
├── api/v1/              # API路由层
│   ├── homework.py      # 作业批改端点
│   ├── ocr.py          # OCR服务端点
│   └── ai.py           # AI服务端点
├── services/           # 业务逻辑层
│   ├── ocr/            # OCR抽象服务
│   ├── llm/            # AI大模型服务
│   ├── parsing/        # 题目解析服务
│   ├── knowledge/      # 知识点提取服务
│   └── student/        # 学生相关服务
├── models/             # 数据模型层
├── schemas/            # API数据模型
├── core/               # 核心配置
├── db/                 # 数据库连接
└── utils/              # 工具函数
```

### 核心服务说明

#### OCR服务 (`services/ocr/`)
- **抽象基类**: `OCRService` - 定义OCR服务接口
- **实现**: `TesseractOCR` - 基于Tesseract的OCR实现
- **特性**: 异步处理、图像预处理、中英文混合识别
- **工厂函数**: `get_ocr_service()` - 根据配置返回OCR服务实例

#### AI大模型服务 (`services/llm/`)
- **抽象基类**: `LLMService` - 统一AI服务接口
- **实现**: `QwenService`, `KimiService` - 支持多AI提供商
- **容错机制**: `safe_json_parse()` - 多级JSON解析降级策略
- **提示词系统**: 科目化、版本化的提示词管理

#### 知识点提取服务 (`services/knowledge/`)
- **科目分离**: `MathKnowledgeExtractor`, `PhysicsKnowledgeExtractor`
- **智能识别**: 基于AI的知识点自动提取和分类
- **工厂模式**: `get_knowledge_extractor(subject)` 按学科获取提取器

#### 作业批改服务 (`services/student/`)
- **核心服务**: `HomeworkService` - 协调OCR、AI和知识点提取
- **处理流程**: 图像→OCR→题目解析→AI批改→知识点提取→结果组装

### 数据流设计

1. **图像上传** → **文件验证** → **图像预处理**
2. **OCR文字识别** → **题目解析** → **文本分析**
3. **AI批改** → **JSON结果解析** → **容错处理**
4. **知识点提取** → **学情分析** → **建议生成**
5. **结果封装** → **结构化返回** → **日志记录**

## 🔄 开发工作流

### 功能开发标准流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **开发前准备**
   ```bash
   uv sync                    # 确保依赖最新
   make test                  # 确保现有测试通过
   ```

3. **编写代码**
   - 遵循分层架构原则
   - 使用类型注解
   - 添加结构化日志
   - 编写对应测试

4. **提交前检查**
   ```bash
   make format               # 代码格式化
   make lint                # 代码质量检查
   make test                # 运行测试
   make test-cov            # 检查覆盖率
   ```

### API开发指南

1. **新增API端点**
   - 在 `src/ai_tutor/api/v1/` 中创建或修改路由文件
   - 使用Pydantic schemas定义请求/响应模型
   - 添加完整的API文档字符串
   - 实现错误处理和参数验证

2. **API测试**
   ```bash
   # 启动服务
   make dev
   
   # 访问API文档
   open http://localhost:8000/docs
   
   # 手动测试端点
   curl -X POST "http://localhost:8000/api/v1/homework/grade" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_image.jpg" \
     -F "subject=math"
   ```

### 服务扩展指南

1. **添加新学科支持**
   - 在 `schemas/` 中定义学科专用数据模型
   - 在 `services/knowledge/` 中实现知识点提取器
   - 在 `services/llm/prompts/` 中添加专业提示词
   - 更新工厂函数和配置

2. **集成新AI服务**
   - 继承 `LLMService` 基类
   - 实现 `chat()` 和 `generate()` 方法
   - 在配置文件中添加相关配置项
   - 更新 `get_llm_service()` 工厂函数

## 🛠️ 故障排查和最佳实践

### 常见问题解决方案

#### 1. OCR识别问题
**症状**: 上传图片后OCR返回空文本或识别错误
```bash
# 检查Tesseract安装
tesseract --version
tesseract --list-langs

# macOS重新安装
brew reinstall tesseract tesseract-lang

# Ubuntu/Debian重新安装  
sudo apt-get install --reinstall tesseract-ocr tesseract-ocr-chi-sim
```

#### 2. AI服务调用失败
**症状**: 批改接口返回500错误，日志显示AI调用异常
```bash
# 检查API密钥配置
uv run python -c "from src.ai_tutor.core.config import settings; print('QWEN_API_KEY:', 'YES' if settings.QWEN_API_KEY else 'NO')"

# 测试网络连接
curl -H "Authorization: Bearer $QWEN_API_KEY" https://dashscope.aliyuncs.com/compatible-mode/v1/models

# 查看详细日志
tail -f logs/ai-tutor.log
```

#### 3. 服务启动失败
**症状**: `make dev` 无响应或启动失败
```bash
# 检查端口占用
lsof -ti:8000
kill -9 $(lsof -ti:8000)

# 清理进程
pkill -f uvicorn

# 稳定模式启动
make dev-stable
```

### 调试技巧

#### 1. 结构化日志查看
```python
from ai_tutor.core.logger import get_logger
logger = get_logger(__name__)

# 记录结构化信息
logger.info("处理作业批改", student_id="123", subject="math", processing_time=1.2)
logger.error("OCR识别失败", filename="test.jpg", error_type="ImageError")
```

#### 2. API调试
```bash
# 健康检查
make health

# 详细API测试
uv run python test_api_upload.py --comprehensive

# 查看API响应时间
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/health
```

#### 3. 数据库调试
```bash
# 查看数据库连接
uv run python -c "from src.ai_tutor.db.database import get_db_url; print(get_db_url())"

# 运行数据库脚本
uv run python scripts/init_db.py
```

### 性能优化建议

1. **图片处理优化**
   - 上传前压缩大图片
   - 使用适合的图片格式（JPEG for photos, PNG for text）
   - 配置合理的文件大小限制

2. **AI调用优化**  
   - 实现请求去重和缓存
   - 使用连接池管理HTTP请求
   - 设置合适的超时时间

3. **数据库优化**
   - 为常用查询字段添加索引
   - 使用Redis缓存热点数据
   - 实现数据库连接池

### 安全注意事项

1. **API密钥管理**
   ```bash
   # 绝不将密钥硬编码到代码中
   # 使用环境变量
   export QWEN_API_KEY="your-secret-key"
   
   # 在.env文件中配置（不要提交到版本控制）
   echo "QWEN_API_KEY=your-secret-key" >> .env
   ```

2. **文件上传安全**
   - 验证文件类型和大小
   - 扫描恶意文件内容
   - 使用安全的文件存储路径

3. **数据隐私**
   - 不记录敏感的学生信息到日志
   - 实现数据脱敏处理
   - 遵循数据保护法规

### 代码规范

1. **Python代码风格**
   - 使用black格式化（line-length=88）
   - 遵循PEP 8规范
   - 使用类型注解
   - 函数长度不超过60行

2. **异步编程规范**
   ```python
   # 所有I/O操作使用async/await
   async def process_image(image: Image.Image) -> str:
       result = await ocr_service.extract_text(image)
       return result
   ```

3. **错误处理规范**
   ```python
   # 使用具体的异常类型
   try:
       result = await ai_service.chat(messages)
   except httpx.TimeoutException:
       logger.error("AI服务调用超时")
       raise HTTPException(status_code=503, detail="AI服务暂时不可用")
   ```

## 📖 参考资源

- **项目文档**: [README.md](./README.md)
- **故障排查**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **FastAPI文档**: https://fastapi.tiangolo.com/
- **uv文档**: https://docs.astral.sh/uv/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract

---

**最后更新**: 2025-09-11  
**文档版本**: v1.0
