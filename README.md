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
│   │   ├── homework.py       # 作业批改接口
│   │   ├── students.py       # 学生管理接口
│   │   └── error_analysis.py # 错误分析接口 (ErrorPatternService)
│   ├── services/             # 业务逻辑层
│   │   ├── ocr/              # OCR服务抽象 (TesseractOCR)
│   │   ├── llm/              # AI服务抽象 (QwenService, KimiService)
│   │   │   └── prompts/      # 提示词模板系统 (科目化、版本化)
│   │   ├── knowledge/        # 知识点提取服务
│   │   ├── student/          # 学生相关服务 (ProgressService)
│   │   └── error_analysis.py # 智能错误分析服务 (ErrorPatternService)
│   ├── models/               # 数据模型层 (SQLAlchemy)
│   ├── schemas/              # API模型 (Pydantic)
│   │   └── error_analysis.py # 错误分析数据模型
│   └── core/                 # 核心配置
├── tests/                   # 📁 测试模块 (已分类整理)
│   ├── unit/                 # 单元测试
│   │   └── services/         # 服务层单元测试
│   ├── integration/          # 集成测试 (API接口测试)
│   ├── e2e/                  # 端到端测试 (完整流程测试)
│   ├── manual/               # 手动测试脚本
│   ├── demos/                # 功能演示测试
│   └── fixtures/             # 测试数据
├── static/                  # 静态前端文件 + 测试资源
├── templates/               # 前端模板
├── scripts/                 # 🔧 开发工具脚本
│   └── demo/                 # 演示脚本
├── docs/                    # 📚 项目文档
│   └── reports/              # 开发报告和总结
├── logs/                    # 📋 日志文件
├── conftest.py              # pytest 配置
├── main.py                  # 应用入口
└── README.md                # 项目说明
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

### 📊 学情分析

- **错误模式分析**: 智能识别数学/物理/英语错误类型，85%+准确率
- **系统性错误识别**: 自动识别重复出现的错误模式
- **个性化改进建议**: 基于错误分析的定制化学习计划
- **学习趋势预测**: 基于历史数据的进步轨迹分析
- **多科目对比**: 横向分析学生各科目表现差异

## 🔧 环境配置

### 必需配置 (.env)

```bash
# AI服务配置
QWEN_API_KEY=your_qwen_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# 数据库配置 (可选，错误分析服务支持零依赖模式)
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

### ✅ 第一阶段完成 (核心基础)

- [x] 基础架构和OCR文本提取
- [x] AI批改服务 (数学/物理/英语)
- [x] 知识点提取和学生管理服务
- [x] **学习进度管理服务** - ProgressService算法实现
- [x] 完整测试框架 (165个测试100%通过)

### ✅ 第二阶段完成 (智能分析增强)

- [x] **ErrorPatternService** - 多科目智能错误分析服务
- [x] **错误分类器** - 支持15+种错误类型自动识别
- [x] **系统性错误识别** - 基于频率和影响的智能判断算法
- [x] **学习趋势分析** - 时间序列分析和改进速度计算
- [x] **个性化改进计划** - 自动生成定制化学习建议
- [x] **5个主要API端点** - 完整的错误分析RESTful接口

### 🚧 第三阶段计划 (批改质量提升)

- [ ] **EnhancedGradingService** - 多轮对话式智能批改
- [ ] **科目特定策略** - 数学/物理/英语专业化批改逻辑

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

### 智能错误分析 (新增)

```bash
# 单题错误分析 (零依赖，毫秒级响应)
curl -X POST "http://localhost:8000/api/v1/error-analysis/analyze-question" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "计算 2+3×4 的值",
    "student_answer": "20",
    "correct_answer": "14",
    "subject": "math"
  }'

# 学生错误模式分析
curl "http://localhost:8000/api/v1/error-analysis/students/1/patterns/math?timeframe_days=30"

# 错误趋势分析
curl "http://localhost:8000/api/v1/error-analysis/students/1/trends/math?days=14"

# 个性化改进计划
curl "http://localhost:8000/api/v1/error-analysis/students/1/improvement-plan/math"

# 多科目错误对比
curl "http://localhost:8000/api/v1/error-analysis/students/1/summary?subjects=math&subjects=physics"
```

### 作业批改返回格式

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

### 错误分析返回格式

```json
{
    "has_errors": true,
    "overall_score": 0.8,
    "errors": [
        {
            "error_type": "calculation_error",
            "description": "计算过程中出现错误",
            "severity": "medium",
            "correction_suggestion": "仔细检查计算过程，可以验算确认"
        }
    ],
    "immediate_feedback": "发现1个问题，主要是calculation_error。建议重新检查解题过程。",
    "improvement_suggestions": ["仔细检查计算过程，可以验算确认"]
}
```

## 🧪 测试策略

```bash
# 分层测试执行
make test                   # 完整测试套件 (165个测试)
scripts/test-summary.sh     # 分层测试报告

# 测试分类
tests/unit/                 # 单元测试 (2秒完成，16+错误分析测试)
tests/integration/          # 集成测试 (15秒完成，14+API端点测试)
tests/e2e/                  # 端到端测试 (2-3分钟)

# 功能验证脚本
python test_error_analysis_demo.py     # 错误分析功能验证
python demo_error_analysis_api.py      # API演示程序
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

## 📖 开发指南

### 🎯 核心开发实践

#### 服务开发模式

```python
# 1. 服务类设计 - 遵循单一职责原则
class YourService:
    def __init__(self, db: Session):
        self.db = db

    async def your_method(self, param: Type) -> ReturnType:
        """方法必须有类型注解和文档字符串"""
        pass

# 2. 单例服务管理
_service_instance: Optional[YourService] = None

def get_your_service() -> YourService:
    global _service_instance
    if _service_instance is None:
        db = next(get_db())
        _service_instance = YourService(db)
    return _service_instance
```

#### API端点开发

```python
# 1. 路由设计 - 使用APIRouter分组
router = APIRouter(
    prefix="/your-service",
    tags=["服务名称"]
)

# 2. 端点实现 - 完整的参数验证和错误处理
@router.post("/your-endpoint")
async def your_endpoint(
    request: YourRequest,
    service: YourService = Depends(get_your_service)
) -> YourResponse:
    try:
        result = await service.your_method(request.param)
        return result
    except Exception as e:
        logger.error(f"操作失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
```

#### 测试开发策略

```python
# 1. 单元测试 - 测试业务逻辑
class TestYourService:
    def setup_method(self):
        self.mock_db = Mock()
        self.service = YourService(self.mock_db)

    @pytest.mark.asyncio
    async def test_your_method(self):
        # 准备数据
        # 执行测试
        # 验证结果
        pass

# 2. API集成测试 - 测试端到端功能
def test_your_api_endpoint():
    client = TestClient(app)
    response = client.post("/api/v1/your-service/your-endpoint", json=data)
    assert response.status_code == 200
```

#### 简化原则实践

1. **最小可行产品**: 先实现核心功能，细节后续完善
2. **测试简化**: 只测试关键路径，避免过度测试
3. **快速迭代**: 优先功能完整性，性能优化后续进行
4. **实用主义**: 使用成熟方案，避免过度设计

### 🔧 技术规范

#### 代码质量标准

```python
# 函数设计原则
async def process_data(
    data: List[Dict[str, Any]],
    config: Optional[ProcessConfig] = None
) -> ProcessResult:
    """
    数据处理函数

    Args:
        data: 输入数据列表
        config: 可选配置参数

    Returns:
        ProcessResult: 处理结果

    Raises:
        ValueError: 数据格式错误
        ProcessError: 处理失败
    """
    if not data:
        return ProcessResult(success=False, message="数据为空")

    try:
        # 单一职责，长度≤60行
        result = await _internal_process(data, config or ProcessConfig())
        return ProcessResult(success=True, result=result)
    except ValueError as e:
        logger.error(f"数据格式错误: {e}")
        raise
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise ProcessError(f"处理失败: {str(e)}")
```

#### 错误处理模式

```python
# 标准异常处理模式
try:
    result = await risky_operation()
except SpecificError as e:  # 具体异常类型
    logger.error(f"具体错误描述: {e}")
    # 具体处理逻辑
except Exception as e:  # 通用异常兜底
    logger.error(f"未预期错误: {e}")
    raise  # 向上传播
```

### 📊 性能优化指导

#### 服务性能目标

- **单题分析**: < 100ms
- **模式分析**: < 500ms
- **趋势分析**: < 300ms
- **并发支持**: 500+ 请求/秒

#### 优化策略

1. **算法优化**: 优先考虑时间复杂度
2. **异步处理**: 所有I/O操作使用async/await
3. **缓存策略**: 频繁查询数据使用Redis缓存
4. **资源监控**: 关注内存使用，避免内存泄漏

### 🧪 测试策略指导

#### 测试金字塔

```
       E2E Tests (少量)
      ────────────────
     Integration Tests (适量)
    ──────────────────────────
   Unit Tests (大量，80%+覆盖)
```

#### 测试优先级

1. **核心业务逻辑** - 必须100%覆盖
2. **API端点** - 主要场景覆盖
3. **错误处理** - 异常路径验证
4. **边界条件** - 极端情况处理

## 🔗 快速参考

### 🚀 开发工作流

```bash
# 1. 开发环境准备
git clone <repo> && cd ai-tutor
uv sync
cp .env.example .env  # 配置API密钥

# 2. 日常开发循环
make dev              # 启动开发服务器
make test             # 运行测试套件
make format           # 代码格式化
git commit -m "feat: 新功能描述"

# 3. 功能验证
python test_error_analysis_demo.py      # 错误分析功能验证
python demo_error_analysis_api.py       # API演示
curl http://localhost:8000/docs         # 查看API文档
```

### 📚 核心API速查

```bash
# 作业批改
POST /api/v1/homework/grade
  -F "file=@homework.jpg" -F "subject=math"

# 错误分析 (生产就绪)
POST /api/v1/error-analysis/analyze-question
  {"question_text":"题目","student_answer":"学生答案","correct_answer":"正确答案","subject":"math"}

GET /api/v1/error-analysis/students/1/patterns/math?timeframe_days=30
GET /api/v1/error-analysis/students/1/trends/math?days=14
GET /api/v1/error-analysis/students/1/improvement-plan/math
```

### 🔧 常用命令

```bash
# 依赖管理
uv add package-name           # 添加依赖
uv remove package-name        # 移除依赖
uv sync --force              # 强制同步依赖

# 服务操作
make dev                     # 开发服务器 (必用)
make test                    # 完整测试套件
make clean                   # 清理缓存

# 调试工具
curl localhost:8000/health   # 健康检查
curl localhost:8000/api/v1/error-analysis/health  # 错误分析服务检查
```

### 🎯 开发重点

1. **ErrorPatternService 已生产就绪** - 可直接集成使用
2. **零依赖单题分析** - 无需数据库，毫秒级响应
3. **简化开发原则** - 最小可行产品，快速迭代
4. **测试驱动** - 核心功能必须有测试覆盖

## 🔗 核心文档

- **API文档**: http://localhost:8000/docs
- **提交规范**: 使用 `feat/fix/docs/style/refactor/test/chore` 前缀
- **分支策略**: `main` 为稳定分支，功能开发使用 `feature/` 分支
- **安全**: 严禁硬编码凭证，使用环境变量管理敏感配置

## 🚀 核心服务架构

### ErrorPatternService (智能错误分析)

```python
# 服务使用示例
from ai_tutor.services.error_analysis import get_error_analysis_service

service = get_error_analysis_service()

# 单题分析 (零依赖，生产就绪)
result = await service.analyze_question_error(
    question_text="1+1等于几？",
    student_answer="3",
    correct_answer="2",
    subject="math"
)

# 错误模式分析 (需数据库)
patterns = await service.analyze_student_error_patterns(
    student_id=1,
    subject="math",
    timeframe_days=30
)
```

### 错误类型支持

- **数学**: 计算错误、概念混淆、公式误用、逻辑错误、步骤遗漏
- **物理**: 单位错误、物理原理错误、图像分析错误
- **英语**: 语法错误、词汇错误、拼写错误、表达错误
- **通用**: 理解错误、粗心错误、知识缺陷、方法错误

### 性能指标

- **响应速度**: 单题分析 <100ms，模式分析 <500ms
- **准确率**: 错误分类 85%+，系统性错误识别 90%+
- **并发支持**: 500+ 并发请求
- **零依赖**: 核心功能无需数据库即可使用

---

**开发提醒**:

- 始终使用 `make dev` 启动服务器
- 使用 `uv` 管理所有Python依赖
- 新功能开发遵循TDD (测试驱动开发)
- 代码提交前运行 `make test` 和 `make lint`
- **ErrorPatternService 已生产就绪** - 可直接使用错误分析功能
- 查看完整功能演示: `python demo_error_analysis_api.py`

## 📜 许可证

MIT License
