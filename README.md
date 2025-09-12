# AI Tutor - 学情管理AI助教 🎓

基于AI的中学生数学、物理和英语学情管理系统。通过OCR识别作业内容，AI批改和知识点分析，为学生提供个性化的学习建议。

## 🚀 快速开始

### 环境准备

- **Python 3.12+**
- **uv 包管理器** (项目依赖管理)
- **Tesseract OCR** (macOS: `brew install tesseract tesseract-lang`)

### 开发环境启动

```bash
# 安装依赖 (使用uv管理)
uv sync

# 复制环境变量配置
cp .env.example .env
# 编辑 .env 文件，配置API密钥

# 启动开发服务器 (推荐使用make)
make dev
```

**重要**: 开发服务器启动始终使用 `make dev` 命令，确保环境一致性。

### 访问服务

- **主页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🏗️ 项目结构

```
ai-tutor/
├── src/ai_tutor/           # 主应用代码
│   ├── api/v1/               # API路由层 (FastAPI endpoints)
│   ├── services/             # 业务逻辑层
│   │   ├── ocr/              # OCR服务抽象 (TesseractOCR)
│   │   ├── llm/              # AI服务抽象 (QwenService, KimiService)
│   │   │   └── prompts/      # 提示词模板系统 (科目化、版本化)
│   │   ├── knowledge/        # 知识点提取服务
│   │   └── student/          # 学生相关服务
│   ├── models/               # 数据模型层 (SQLAlchemy)
│   ├── schemas/              # API模型 (Pydantic)
│   └── core/                 # 核心配置
├── tests/                   # 测试模块 (单元/集成/端到端)
├── static/                  # 静态前端文件
└── scripts/                 # 开发工具脚本
```

## 🔧 开发命令

```bash
# 依赖管理 (使用uv)
uv sync                     # 安装依赖
uv add package-name         # 添加新依赖
uv remove package-name      # 移除依赖

# 开发服务器 (必须使用make)
make dev                    # 启动开发服务器
make test                   # 运行测试套件
make format                 # 代码格式化
make lint                   # 代码质量检查
```

## 🎨 技术栈

- **后端框架**: FastAPI + Python 3.12
- **包管理**: uv (现代Python包管理器)
- **OCR引擎**: Tesseract OCR
- **AI服务**: 通义千问 (Qwen) / Kimi
- \*\*支持科
  目\*\*: 数学、物理、英语
- **数据库**: PostgreSQL + Redis
- **测试**: pytest + pytest-cov
- **代码质量**: black + flake8 + mypy

## ✨ 核心功能

### 🔍 智能OCR识别

- 支持中英文混合识别，自动图片预处理

### 🧠 AI智能批改

- **数学**: 一元一次方程、函数、几何等
- **物理**: 力学、电磁学、热学、光学等
- **英语**: 语法、词汇、阅读理解等

### 📊 知识点提取

- 自动识别题目涉及的知识点，科目化分类管理

### 📈 学情分析

- 个性化学习建议，薄弱知识点识别，学习进度跟踪

## 🔧 环境配置

### 必需配置 (.env)

```bash
# AI服务配置
QWEN_API_KEY=your_qwen_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/ai_tutor
REDIS_URL=redis://localhost:6379/0

# 应用配置
SECRET_KEY=your_secret_key_here
OCR_ENGINE=tesseract
DEBUG=True
LOG_LEVEL=INFO
LLM_PROVIDER=qwen
```

## 🛠️ 开发规范

### 编码标准

- **函数**: 单一职责，长度≤60行，必须类型注解
- **错误处理**: 显式异常处理 (`try...except SpecificError`)
- **异步优先**: 所有I/O操作使用 `async/await`
- **测试覆盖**: 核心功能必须有pytest单元测试

### 代码风格

- **格式化**: Black (line-length=88)
- **检查**: flake8 + mypy
- **提交**: 语义化提交信息 (`feat/fix/docs/refactor`)

### 日志使用

```python
from ai_tutor.core.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing homework", student_id="123", subject="math")
```

## 🗺️ 开发路线图

### ✅ 已完成

- [x] 基础架构和OCR文本提取
- [x] AI批改服务 (数学/物理/英语)
- [x] 知识点提取和学生管理服务
- [x] 完整测试框架 (118个单元测试100%通过)

### 🚧 进行中

- [ ] **学习进度管理服务** - ProgressService核心算法
- [ ] **数据持久化完善** - 作业批改结果完整保存
- [ ] **错误模式分析** - 智能错误识别和改进建议

### 📋 近期计划

- [ ] **知识图谱构建** - 构建学科知识点关联网络
- [ ] **学习报告生成** - 自动生成PDF学情报告
- [ ] **前端界面完善** - Vue3 + TypeScript界面

## 📡 API使用示例

### 作业批改

```bash
# 批改数学作业
curl -X POST "http://localhost:8000/api/v1/homework/grade" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@math_homework.jpg" \
  -F "subject=math"

# 支持科目查询
curl "http://localhost:8000/api/v1/homework/subjects"
# 返回: ["math", "physics", "english"]
```

### 返回格式

```json
{
    "success": true,
    "data": {
        "text": "识别到的文本内容",
        "grading_result": {...},
        "knowledge_points": [...]
    },
    "message": "批改完成"
}
```

## 🧪 测试策略

```bash
# 分层测试执行
make test                   # 完整测试套件
scripts/test-summary.sh     # 分层测试报告

# 测试分类
tests/unit/                 # 单元测试 (2秒完成)
tests/integration/          # 集成测试 (15秒完成)
tests/e2e/                  # 端到端测试 (2-3分钟)
```

## 🐛 常见问题

### OCR问题

```bash
# macOS安装Tesseract
brew install tesseract tesseract-lang

# 验证安装
tesseract --version
tesseract --list-langs
```

### 依赖问题

```bash
# 重新同步依赖
uv sync --force

# 清理缓存
make clean
```

## 🔗 核心文档

- **API文档**: http://localhost:8000/docs
- **提交规范**: 使用 `feat/fix/docs/style/refactor/test/chore` 前缀
- **分支策略**: `main` 为稳定分支，功能开发使用 `feature/` 分支
- **安全**: 严禁硬编码凭证，使用环境变量管理敏感配置

---

**开发提醒**:

- 始终使用 `make dev` 启动服务器
- 使用 `uv` 管理所有Python依赖
- 新功能开发遵循TDD (测试驱动开发)
- 代码提交前运行 `make test` 和 `make lint`

## 📜 许可证

MIT License
