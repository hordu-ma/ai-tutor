# AI Tutor 测试目录结构

本目录包含 AI Tutor 项目的所有测试文件，按照测试类型和用途进行分类组织。

## 📁 目录结构

### `unit/` - 单元测试
独立测试单个模块、函数或类的功能，不依赖外部服务。

**文件说明：**
- `test_algorithm_only.py` - 进度算法核心逻辑测试
- `test_knowledge_service.py` - 知识服务单元测试
- `test_physics_schemas.py` - 物理学科数据模型测试
- `test_english_knowledge.py` - 英语知识点测试
- `test_error_handling.py` - 错误处理机制测试
- `test_subject_router.py` - 科目路由测试

**子目录：**
- `services/` - 服务层单元测试
  - `test_progress_service.py` - 学习进度服务测试
  - `test_error_analysis.py` - 错误分析服务测试
  - `student/test_student_service.py` - 学生管理服务测试

### `integration/` - 集成测试
测试多个模块间的交互和外部服务集成。

**文件说明：**
- `test_physics_support.py` - 物理学科功能集成测试
- `test_qwen_api.py` - Qwen API 集成测试
- `test_progress_api.py` - 进度管理 API 集成测试
- `test_llm_services.py` - 大语言模型服务集成测试
- `test_error_analysis_api.py` - 错误分析 API 集成测试
- `test_english_grading_flow.py` - 英语批改流程集成测试

### `e2e/` - 端到端测试
完整的用户流程测试，从前端到后端的全链路验证。

**文件说明：**
- `test_full_flow.py` - 完整作业批改流程测试
- `test_question_parsing.py` - 题目解析端到端测试

### `manual/` - 手动测试
需要人工干预或特殊环境的测试脚本。

**文件说明：**
- `test_api_manual.py` - API 手动测试脚本
- `test_api_comprehensive.py` - 综合 API 测试脚本

### `demos/` - 演示测试
用于功能演示和验证的测试脚本。

**文件说明：**
- `test_error_analysis_demo.py` - 错误分析功能演示
- `test_progress_verification.py` - 学习进度验证演示

### `fixtures/` - 测试数据
测试用的静态数据和模拟数据。

## 🚀 运行测试

### 运行所有测试
```bash
make test
```

### 按类型运行测试
```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 端到端测试
pytest tests/e2e/ -v
```

### 运行特定测试文件
```bash
pytest tests/unit/test_algorithm_only.py -v
```

### 生成覆盖率报告
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📝 测试编写规范

### 命名规则
- 测试文件：`test_*.py`
- 测试类：`TestClassName`
- 测试方法：`test_method_name`

### 目录选择指导

**单元测试 (`unit/`)：**
- 测试单个函数或方法
- 使用 mock 替代外部依赖
- 执行速度快，不依赖网络或数据库

**集成测试 (`integration/`)：**
- 测试多个组件的交互
- 可能涉及真实的外部服务
- 验证API接口和数据流

**端到端测试 (`e2e/`)：**
- 模拟完整的用户场景
- 从前端UI到后端数据库的全链路
- 执行时间较长，但最接近真实使用

**手动测试 (`manual/`)：**
- 需要特殊配置或环境
- 需要人工判断结果
- 用于调试和问题排查

**演示测试 (`demos/`)：**
- 用于功能展示
- 包含详细的输出和说明
- 适合向他人演示系统功能

## 🔧 配置文件

- `conftest.py` - pytest 配置和共享 fixtures
- `pytest.ini` - pytest 运行配置（如果存在）

## 📊 测试覆盖率目标

- 单元测试：≥ 90%
- 集成测试：覆盖关键业务流程
- 端到端测试：覆盖主要用户场景
