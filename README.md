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
│   ├── api/                  # API路由层
│   │   └── v1/               # API v1版本
│   ├── core/                 # 核心配置
│   ├── services/             # 业务逻辑层
│   │   ├── ocr/              # OCR服务
│   │   ├── llm/              # 大模型服务
│   │   ├── knowledge/        # 知识点提取服务
│   │   ├── parsing/          # 题目解析服务
│   │   └── student/          # 学生服务
│   ├── models/               # 数据模型层
│   ├── schemas/              # Pydantic模型
│   └── db/                   # 数据库连接
├── tests/                   # 测试代码
├── static/                  # 静态文件
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

## 🤝 贡献

欢迎提交Issue和Pull Request！请遵循以下规范：

1. 使用`black`格式化代码
2. 通过`flake8`检查
3. 添加相应的测试用例
4. 更新相关文档

## 📜 许可证

MIT License
