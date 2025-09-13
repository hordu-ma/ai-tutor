# AI Tutor 配置指南

本文档提供 AI Tutor 智能学习管理系统的完整配置指南，帮助您快速设置和部署项目。

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd ai-tutor

# 设置开发环境
make setup-dev
```

### 2. 配置文件设置

复制并编辑环境变量文件：

```bash
cp .env.example .env
```

## 📝 配置项详解

### 核心配置 (.env)

```bash
# ===========================================
# 🤖 AI 服务配置
# ===========================================

# Qwen (通义千问) API 配置
QWEN_API_KEY=your-qwen-api-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Kimi (月之暗面) API 配置 (可选)
KIMI_API_KEY=your-kimi-api-key-here
KIMI_BASE_URL=https://api.moonshot.cn/v1

# ===========================================
# 🗃️ 数据库配置
# ===========================================

# PostgreSQL 数据库连接
DATABASE_URL=postgresql://username:password@localhost:5432/ai_tutor

# Redis 缓存连接
REDIS_URL=redis://localhost:6379/0

# ===========================================
# 🔧 应用配置
# ===========================================

# 应用密钥 (生产环境请更改)
SECRET_KEY=your-super-secret-key-change-in-production

# 调试模式
DEBUG=true

# 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ===========================================
# 📁 文件上传配置
# ===========================================

# 最大文件大小 (字节)
MAX_FILE_SIZE=10485760

# 允许的图片类型
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg,image/webp

# ===========================================
# 🌐 跨域配置
# ===========================================

# 允许的前端域名
CORS_ORIGINS=http://localhost:6173,http://localhost:3000

# ===========================================
# 🔍 OCR 配置
# ===========================================

# OCR 引擎选择 (tesseract 或 paddleocr)
OCR_ENGINE=tesseract
```

### AI API 密钥获取指南

#### 1. 通义千问 (Qwen) API 密钥

1. **访问阿里云控制台**
   - 登录 [阿里云控制台](https://ecs.console.aliyun.com/)
   - 搜索并进入 "模型服务灵积"

2. **创建 API 密钥**
   - 在控制台中找到 "API 密钥管理"
   - 点击 "创建新的API密钥"
   - 复制生成的密钥

3. **配置到项目**
   ```bash
   QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

#### 2. Kimi API 密钥 (可选)

1. **访问月之暗面平台**
   - 登录 [Kimi 开发平台](https://platform.moonshot.cn/)

2. **获取 API 密钥**
   - 在控制台中创建新的密钥
   - 复制密钥到配置文件

3. **配置到项目**
   ```bash
   KIMI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## 🗄️ 数据库配置

### PostgreSQL 设置

#### 方式一：使用 Docker (推荐)

```bash
# 启动 PostgreSQL 容器
docker run --name ai-tutor-postgres \
  -e POSTGRES_DB=ai_tutor \
  -e POSTGRES_USER=ai_tutor_user \
  -e POSTGRES_PASSWORD=ai_tutor_pass \
  -p 5432:5432 \
  -d postgres:14

# 更新 .env 配置
DATABASE_URL=postgresql://ai_tutor_user:ai_tutor_pass@localhost:5432/ai_tutor
```

#### 方式二：本地安装

```bash
# macOS
brew install postgresql
brew services start postgresql

# 创建数据库和用户
createdb ai_tutor
createuser ai_tutor_user
```

### Redis 设置

```bash
# 使用 Docker
docker run --name ai-tutor-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# 或使用 Homebrew (macOS)
brew install redis
brew services start redis
```

## 🚀 启动服务

### 1. 后端服务

```bash
# 安装依赖
make install

# 启动开发服务器
make dev

# 检查服务状态
make health
```

### 2. 前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 🧪 功能测试

### 基础连接测试

```bash
# 测试后端连接
python test_backend_connection.py

# 测试作业批改功能
python test_homework_api.py
```

### API 端点测试

```bash
# 健康检查
curl http://localhost:8000/health

# 科目列表
curl http://localhost:8000/api/v1/homework/subjects

# 服务状态
curl http://localhost:8000/api/v1/homework/health
```

## ⚙️ 开发模式配置

### 最小化配置 (仅测试基础功能)

如果您只想测试基础功能，可以使用最小化配置：

```bash
# .env 最小配置
DEBUG=true
LOG_LEVEL=INFO

# 暂时跳过数据库配置
# DATABASE_URL=sqlite:///./ai_tutor.db

# 必需的 AI API 配置
QWEN_API_KEY=your-api-key
```

### Mock 模式 (无需 API 密钥)

前端支持 Mock 模式，可以在没有 API 密钥的情况下测试界面：

```bash
# 前端环境变量
VITE_USE_MOCK=true
```

## 🔧 故障排除

### 常见问题

#### 1. API 密钥错误
```
错误: Qwen API调用失败 (HTTP 401)
解决: 检查 QWEN_API_KEY 是否正确配置
```

#### 2. 数据库连接失败
```
错误: 服务器内部错误 (学生管理相关API)
解决: 配置 PostgreSQL 数据库连接
```

#### 3. 前端无法连接后端
```
错误: 网络请求失败
解决: 确认后端服务在 8000 端口运行
```

#### 4. CORS 错误
```
错误: 跨域请求被阻止
解决: 检查 CORS_ORIGINS 配置是否包含前端地址
```

### 调试技巧

#### 查看日志

```bash
# 后端日志 (如果使用 make dev)
tail -f logs/app.log

# 或直接查看控制台输出
```

#### 测试各个服务

```bash
# 测试 OCR 服务
make test-services

# 测试 API 端点
make api-test
```

## 📋 配置检查清单

在部署之前，请确保以下配置正确：

- [ ] **AI API 密钥已配置**
  - [ ] QWEN_API_KEY 设置且有效
  - [ ] API 额度充足

- [ ] **数据库连接正常**
  - [ ] PostgreSQL 服务运行
  - [ ] DATABASE_URL 配置正确
  - [ ] 数据库连接测试通过

- [ ] **Redis 缓存可用** (可选)
  - [ ] Redis 服务运行
  - [ ] REDIS_URL 配置正确

- [ ] **服务端口可用**
  - [ ] 8000 端口未被占用 (后端)
  - [ ] 6173 端口未被占用 (前端)

- [ ] **CORS 配置正确**
  - [ ] 前端域名在 CORS_ORIGINS 中

- [ ] **文件上传配置**
  - [ ] MAX_FILE_SIZE 适合您的需求
  - [ ] 存储空间充足

## 🔒 生产环境配置

### 安全配置

```bash
# 生产环境必需配置
DEBUG=false
SECRET_KEY=复杂的随机密钥

# 限制 CORS 源
CORS_ORIGINS=https://your-domain.com

# 使用强密码的数据库连接
DATABASE_URL=postgresql://secure_user:strong_password@localhost:5432/ai_tutor_prod
```

### 性能优化

```bash
# 调整日志级别
LOG_LEVEL=WARNING

# 优化文件上传大小
MAX_FILE_SIZE=5242880  # 5MB
```

## 📞 技术支持

如果您在配置过程中遇到问题：

1. **检查配置文件**: 确保所有必需的环境变量都已正确设置
2. **查看日志**: 检查后端服务的错误日志
3. **运行测试**: 使用提供的测试脚本验证各项功能
4. **参考文档**: 查看 `docs/` 目录中的详细文档

---

*配置指南最后更新: 2024年12月13日*
