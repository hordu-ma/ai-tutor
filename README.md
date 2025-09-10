# AI Tutor - 学情管理AI助教 🎓

基于AI的中学生数学、物理和英语学情管理系统。通过OCR识别作业内容，AI批改和知识点分析，为学生提供个性化的学习建议。

## 🚀 快速开始

### 环境准备

1. **Python 3.12+**
2. **uv 包管理器**
3. **Tesseract OCR**（对于macOS：`brew install tesseract tesseract-lang`）

### 安装和运行

```bash
# 安装依赖
uv sync

# 复制环境变量配置
cp .env.example .env
# 编辑 .env 文件，配置您的API密钥和数据库连接

# 运行开发服务器
uv run uvicorn src.ai_tutor.main:app --reload --host 0.0.0.0 --port 8000

# 或使用Makefile
make dev
```

### 访问服务

- **主页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **OCR服务**: http://localhost:8000/api/v1/ocr/health

## 📚 项目结构

```
ai-tutor/
├── src/ai_tutor/           # 主应用代码
│   ├── api/v1/               # API路由层 (FastAPI endpoints)
│   ├── services/             # 业务逻辑层
│   │   ├── ocr/              # OCR服务抽象 (TesseractOCR)
│   │   ├── llm/              # AI服务抽象 (QwenService, KimiService)
│   │   │   └── prompts/      # 提示词模板系统 (科目化、版本化)
│   │   ├── parsing/          # 题目解析服务 (QuestionParser, TextAnalyzer)
│   │   ├── knowledge/        # 知识点提取服务 (KnowledgeExtractor)
│   │   └── student/          # 学生相关服务 (HomeworkService)
│   ├── models/               # 数据模型层 (SQLAlchemy)
│   ├── schemas/              # API模型 (Pydantic)
│   ├── core/                 # 核心配置 (config.py, logger.py)
│   ├── db/                   # 数据库连接
│   └── utils/                # 工具函数
├── tests/                   # 测试模块
│   ├── integration/          # 集成测试
│   ├── unit/                 # 单元测试
│   ├── e2e/                  # 端到端测试
│   └── fixtures/             # 测试数据
├── static/                  # 静态文件
├── scripts/                 # 工具脚本
└── docs/                    # 文档
```

## 🔧 开发命令

```bash
# 安装依赖
make install

# 运行开发服务器
make dev

# 运行测试
make test

# 代码格式化
make format

# 代码质量检查
make lint

# Docker运行
make docker-up
make docker-down

# 清理缓存
make clean
```

## 📡 API使用示例

### OCR文本提取

```bash
# 上传图片进行OCR识别
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@homework.jpg"
```

### 作业批改

```bash
# 批改数学作业
curl -X POST "http://localhost:8000/api/v1/homework/grade" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@math_homework.jpg" \
  -F "subject=math"

# 批改物理作业
curl -X POST "http://localhost:8000/api/v1/homework/grade" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@physics_homework.jpg" \
  -F "subject=physics"
```

### 返回示例

```json
{
    "success": true,
    "data": {
        "text": "识别到的文本内容",
        "metadata": {
            "filename": "homework.jpg",
            "content_type": "image/jpeg",
            "file_size": 245760,
            "text_length": 150,
            "ocr_engine": "tesseract"
        }
    },
    "message": "文本提取成功"
}
```

## 🎨 技术栈

- **后端框架**: FastAPI + Python 3.12
- **包管理**: uv
- **OCR引擎**: Tesseract OCR
- **AI服务**: 通义千问 (Qwen) / Kimi
- **支持科目**: 数学、物理、英语
- **日志**: structlog (结构化日志)
- **数据库**: PostgreSQL + Redis
- **容器化**: Docker + Docker Compose
- **测试**: pytest + pytest-cov
- **代码质量**: black + flake8 + mypy

## ✨ 核心功能

### 🔍 智能OCR识别

- 支持中英文混合识别
- 自动图片预处理和优化
- 多种图片格式支持

### 🧠 AI智能批改

- **数学**: 一元一次方程、函数、几何等知识点识别
- **物理**: 力学、电磁学、热学、光学等分类批改
- **英语**: 语法、词汇、阅读理解等

### 📊 知识点提取

- 自动识别题目涉及的知识点
- 科目化分类管理 (数学/物理/英语)
- 智能错误模式分析

### 📈 学情分析

- 个性化学习建议
- 薄弱知识点识别
- 学习进度跟踪

## 🗺️ 路线图

### ✅ 第一阶段已完成

- [x] 项目初始化和基础架构
- [x] OCR文本提取功能
- [x] 大模型集成（通义千问/Kimi）
- [x] 作业批改基础功能
- [x] 智能提示词系统（科目化、版本化）
- [x] JSON解析容错机制
- [x] 题目智能解析和文本分析

### ✅ 第三阶段已完成

- [x] 数学知识点提取功能
- [x] 物理知识点提取功能
- [x] 物理科目schemas和数据模型
- [x] 完整的测试框架和覆盖率

### 🚧 进行中

- [ ] 学生学情数据管理
- [ ] 错误模式分析

### 📋 待开发

- [ ] RAG系统实现
- [ ] 个性化学习建议
- [ ] 前端界面完善
- [ ] 更多科目支持（化学、生物等）

## 🐛 问题排查

### OCR问题

1. **Tesseract未安装**

    ```bash
    # macOS
    brew install tesseract tesseract-lang

    # Ubuntu/Debian
    sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
    ```

2. **中文识别精度低**
    - 确保安装了中文语言包
    - 考虑使用PaddleOCR替代Tesseract

3. **文件上传失败**
    - 检查文件大小是否超过10MB
    - 确认文件格式支持（JPEG/PNG/JPG/WEBP）

## 🏗️ 架构设计

### 分层架构

系统采用清晰的分层架构设计，职责分离：

- **API路由层**: FastAPI endpoints，处理HTTP请求和响应
- **业务逻辑层**: 核心服务抽象，包含OCR、LLM、知识点提取等
- **数据模型层**: SQLAlchemy模型定义和数据库操作
- **配置层**: 应用配置、日志配置和环境变量管理

### 核心服务

#### OCR服务 (`services/ocr/base.py`)

- **抽象基类**: `OCRService`
- **实现**: `TesseractOCR`
- **工厂函数**: `get_ocr_service()`
- **特性**: 异步处理、图片预处理、支持中英文

#### LLM服务 (`services/llm/base.py`)

- **抽象基类**: `LLMService`
- **实现**: `QwenService`, `KimiService`
- **工厂函数**: `get_llm_service(provider="qwen")`
- **接口**: `chat()`, `generate()`, `safe_json_parse()`
- **增强功能**: JSON解析容错、多级降级策略

#### 提示词系统 (`services/llm/prompts/`)

- **基类**: `BaseGradingPrompts`, `PromptTemplate`
- **科目实现**: `MathGradingPrompts`, `PhysicsGradingPrompts`
- **版本管理**: `PromptVersion` (支持v1.0, v1.1, v2.0)
- **A/B测试**: `PromptManager` (支持流量分配)

#### 知识点提取服务 (`services/knowledge/`)

- **抽象基类**: `KnowledgeExtractor`
- **科目实现**: `MathKnowledgeExtractor`, `PhysicsKnowledgeExtractor`
- **工厂函数**: `get_knowledge_extractor(subject)`
- **特性**: 科目化分类、智能识别、容错处理

### 数据模型关系

- `Student` -> `HomeworkSession` (一对多)
- `HomeworkSession` -> `Question` (一对多)
- 支持多科目: 数学、英语、物理、化学等

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
OCR_ENGINE=tesseract  # 或 paddleocr
DEBUG=True
LOG_LEVEL=INFO

# 服务配置
LLM_PROVIDER=qwen  # 或 kimi
MAX_FILE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=jpg,jpeg,png,webp
```

### OCR 依赖安装

```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 验证安装
tesseract --version
tesseract --list-langs
```

## 🛠️ 开发规范

### 日志使用

```python
from ai_tutor.core.logger import get_logger

logger = get_logger(__name__)

# 结构化日志
logger.info("Processing homework", student_id="123", subject="math")
logger.error("OCR failed", error=str(e), filename="test.jpg")
```

### 错误处理

- 服务层使用抽象基类和工厂模式
- API层统一异常处理和响应格式
- 健康检查端点监控各服务状态
- 使用显式异常处理 (`try...except SpecificError`)

### 异步模式

- 所有I/O操作使用异步 (`async/await`)
- OCR和LLM服务支持异步调用
- FastAPI原生异步支持

### 测试策略

- 单元测试覆盖核心逻辑
- 集成测试验证服务协作
- 端到端测试完整流程验证
- 使用 `pytest-mock` 进行模拟测试

## 🤝 贡献

欢迎提交Issue和Pull Request！请遵循以下规范：

### 代码规范

- 遵循 **Unix 哲学** (专一、简洁、组合) 和 **Python 之禅**
- 使用 `black` 格式化代码 (line-length=88)
- 通过 `flake8` 和 `mypy` 检查
- 函数单一职责，长度不超过60行，必须包含类型注解

### 测试要求

- 为核心功能编写 `pytest` 单元测试
- 覆盖正常和边界情况
- 测试覆盖率保持在合理水平

### 提交规范

- 使用语义化提交信息: `feat/fix/docs/style/refactor/test/chore`
- 清晰描述变更内容和影响范围
- 更新相关文档

### 安全注意事项

- 严禁在代码中硬编码任何凭证
- 注意算法复杂度，避免 O(n²) 及以上复杂度
- 使用环境变量管理敏感配置

---

## 🚧 当前开发任务详情

### 📊 当前状态分析

根据最新检查，当前系统的状态如下：

#### ✅ 已完成的基础设施

- **完整的数据模型**：Student、HomeworkSession、Question、KnowledgePoint、KnowledgeProgress、ErrorPattern
- **核心服务**：OCR、LLM、知识点提取、作业批改基础功能
- **基础API**：作业批改端点 `/api/v1/homework/grade`

#### 🚧 当前缺少的关键组件

1. **学生管理服务层**：缺少 StudentService 和 ProgressService
2. **数据持久化逻辑**：作业批改结果未保存到数据库
3. **学情分析服务**：缺少学习进度分析和追踪
4. **错误模式识别**：缺少错误分析算法和模式提取
5. **相关API端点**：学生管理、学情查看、错误分析等API

---

## 🎯 优先开发任务

### 任务1：学生学情数据管理

#### 📊 当前状态

- ✅ **数据模型完整**：Student、KnowledgeProgress 模型已定义
- ❌ **服务层缺失**：无 StudentService、ProgressService
- ❌ **数据持久化缺失**：批改结果未保存到数据库
- ❌ **API端点缺失**：无学生管理相关API

#### 🎯 开发目标

建立完整的学生学情数据管理体系，包括学生信息管理、学习进度跟踪、作业记录持久化。

#### 📋 详细开发步骤

##### 步骤1.1：创建学生管理服务 (2-3小时)

**输出文件**：`src/ai_tutor/services/student/student_service.py`

```python
class StudentService:
    async def create_student(student_data) -> Student
    async def get_student(student_id) -> Student
    async def update_student(student_id, updates) -> Student
    async def list_students(filters) -> List[Student]
    async def get_student_progress(student_id) -> Dict
```

**关键功能**：

- 学生CRUD操作
- 学生信息验证和格式化
- 学生查询和筛选
- 学生学习统计概览

##### 步骤1.2：创建学习进度服务 (2-3小时)

**输出文件**：`src/ai_tutor/services/student/progress_service.py`

```python
class ProgressService:
    async def update_knowledge_progress(student_id, knowledge_points, performance)
    async def get_student_mastery_report(student_id) -> Dict
    async def identify_weak_areas(student_id) -> List[KnowledgePoint]
    async def generate_recommendations(student_id) -> List[str]
```

**关键功能**：

- 知识点掌握度计算和更新
- 学习进度追踪算法
- 薄弱环节识别
- 个性化学习建议生成

##### 步骤1.3：增强作业服务，支持数据持久化 (2-3小时)

**修改文件**：`src/ai_tutor/services/student/homework_service.py`

**新增功能**：

```python
class HomeworkService:
    async def save_homework_session(session_data) -> HomeworkSession
    async def save_questions_and_analyze(questions_data) -> List[Question]
    async def update_student_progress_from_homework(session_id)
```

**关键改进**：

- 将批改结果保存到数据库
- 自动更新学生知识点进度
- 关联作业记录和学生档案

##### 步骤1.4：创建学生管理API端点 (2-3小时)

**输出文件**：`src/ai_tutor/api/v1/students.py`

**API端点**：

- `POST /api/v1/students` - 创建学生
- `GET /api/v1/students/{student_id}` - 获取学生信息
- `PUT /api/v1/students/{student_id}` - 更新学生信息
- `GET /api/v1/students` - 学生列表
- `GET /api/v1/students/{student_id}/progress` - 学习进度
- `GET /api/v1/students/{student_id}/homework-history` - 作业历史

##### 步骤1.5：创建数据库初始化和测试数据 (1-2小时)

**输出文件**：

- `scripts/init_student_data.py` - 初始化测试学生数据
- `tests/unit/test_student_service.py` - 学生服务测试
- `tests/unit/test_progress_service.py` - 进度服务测试

##### 步骤1.6：端到端集成测试 (1-2小时)

**验证目标**：

- 完整的"学生注册 → 作业批改 → 进度更新 → 学情查看"流程
- API响应格式和性能验证
- 数据一致性验证

#### 📈 预期成果

- 完整的学生生命周期管理
- 自动化的学习进度跟踪
- 持久化的作业记录体系
- 8-10个新的API端点
- 测试覆盖率提升至65%+

---

### 任务2：错误模式分析

#### 📊 当前状态

- ✅ **数据模型完整**：ErrorPattern 模型已定义
- ❌ **分析算法缺失**：无错误模式识别逻辑
- ❌ **知识库缺失**：无错误模式数据积累
- ❌ **分析服务缺失**：无错误分析服务

#### 🎯 开发目标

建立智能的错误模式分析系统，能够识别学生常见错误，提供个性化的改进建议。

#### 📋 详细开发步骤

##### 步骤2.1：创建错误模式分析服务 (3-4小时)

**输出文件**：`src/ai_tutor/services/analysis/error_pattern_service.py`

```python
class ErrorPatternService:
    async def analyze_student_errors(questions: List[Question]) -> List[ErrorPattern]
    async def identify_error_patterns(error_text: str, subject: str) -> Dict
    async def update_pattern_statistics(pattern_id: int)
    async def get_common_patterns(subject: str) -> List[ErrorPattern]
```

**关键功能**：

- 基于LLM的错误模式识别
- 错误分类和聚类算法
- 错误模式统计更新
- 常见错误模式查询

##### 步骤2.2：创建错误模式LLM提示词系统 (2-3小时)

**输出文件**：`src/ai_tutor/services/llm/prompts/error_analysis.py`

```python
class ErrorAnalysisPrompts:
    def get_error_identification_prompt() -> str
    def get_error_classification_prompt() -> str
    def get_correction_strategy_prompt() -> str
```

**关键内容**：

- 数学错误识别提示词
- 物理错误识别提示词
- 错误原因分析提示词
- 改进建议生成提示词

##### 步骤2.3：创建个性化分析服务 (2-3小时)

**输出文件**：`src/ai_tutor/services/analysis/personalized_service.py`

```python
class PersonalizedAnalysisService:
    async def generate_student_error_report(student_id: int) -> Dict
    async def get_improvement_plan(student_id: int) -> Dict
    async def predict_learning_difficulties(student_id: int) -> List[str]
```

**关键功能**：

- 学生个人错误模式分析
- 基于历史数据的学习建议
- 学习困难预测
- 个性化练习推荐

##### 步骤2.4：创建错误分析API端点 (2-3小时)

**输出文件**：`src/ai_tutor/api/v1/analysis.py`

**API端点**：

- `GET /api/v1/analysis/error-patterns` - 常见错误模式
- `POST /api/v1/analysis/analyze-errors` - 分析特定错误
- `GET /api/v1/analysis/students/{student_id}/error-report` - 学生错误报告
- `GET /api/v1/analysis/students/{student_id}/improvement-plan` - 改进计划

##### 步骤2.5：创建错误模式知识库初始化 (2-3小时)

**输出文件**：

- `scripts/init_error_patterns.py` - 初始化常见错误模式
- `data/error_patterns_math.json` - 数学错误模式库
- `data/error_patterns_physics.json` - 物理错误模式库

**知识库内容**：

- 50+ 常见数学错误模式
- 30+ 常见物理错误模式
- 每个模式的解决策略和练习建议

##### 步骤2.6：集成到作业批改流程 (1-2小时)

**修改文件**：`src/ai_tutor/services/student/homework_service.py`

**新增功能**：

- 作业批改时自动进行错误分析
- 更新学生错误模式统计
- 在批改结果中包含个性化建议

##### 步骤2.7：测试和验证 (2-3小时)

**输出文件**：

- `tests/unit/test_error_pattern_service.py`
- `tests/integration/test_error_analysis_flow.py`

#### 📈 预期成果

- 智能的错误模式识别系统
- 个性化的学习改进建议
- 50+ 预定义错误模式知识库
- 4-6个新的分析API端点
- 完整的错误分析工作流

---

## 🗓️ 开发时间线建议

### 第一周：学生学情数据管理 (10-15小时)

- **Day 1-2**: 步骤1.1-1.2 (服务层开发)
- **Day 3-4**: 步骤1.3-1.4 (持久化和API)
- **Day 5**: 步骤1.5-1.6 (测试和验证)

### 第二周：错误模式分析 (12-18小时)

- **Day 1-2**: 步骤2.1-2.2 (分析服务和提示词)
- **Day 3-4**: 步骤2.3-2.4 (个性化服务和API)
- **Day 5-6**: 步骤2.5-2.7 (知识库和集成测试)

### 📊 预期整体提升

- **功能完整性**: 从 MVP+ 升级为完整的学情管理系统
- **测试覆盖率**: 从 55% 提升至 70%+
- **API端点**: 新增 12-16 个端点
- **数据驱动**: 建立完整的学习数据闭环

这两个任务完成后，系统将具备完整的学生学情管理和智能错误分析能力，为后续的RAG系统和个性化推荐打下坚实基础。

## 📜 许可证

MIT License
