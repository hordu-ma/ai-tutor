# AI Tutor - 学情管理AI助教 🎓

基于AI的中学生数学和英语学情管理系统。通过OCR识别作业内容，AI批改和知识点分析，为学生提供个性化的学习建议。

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
│   │   └── llm/              # 大模型服务
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
- **日志**: structlog
- **数据库**: PostgreSQL + Redis
- **容器化**: Docker + Docker Compose
- **测试**: pytest
- **代码质量**: black + flake8 + mypy

## 🗺️ 路线图

### MVP阶段（当前）
- [x] 项目初始化和基础架构
- [x] OCR文本提取功能
- [ ] 大模型集成（通义千问/Kimi）
- [ ] 作业批改基础功能

### 第二阶段
- [ ] 知识点提取和分类
- [ ] 学生学情数据管理
- [ ] 错误模式分析

### 第三阶段
- [ ] RAG系统实现
- [ ] 个性化学习建议
- [ ] 前端界面完善

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
