# AI Tutor 项目技术概览

本文档为开发者提供 AI Tutor 项目的技术栈、架构和核心开发流程的快速指南。

## 1. 项目概述

AI Tutor 是一个基于 Python (FastAPI) 和 Vue.js 的全栈智能学习管理系统。它利用光学字符识别（OCR）技术分析学生提交的作业图片，并通过大型语言模型（LLM）进行自动批改、错误分析，最终为学生提供个性化的学习反馈和指导。

## 2. 关键技术

| 类别       | 技术/库              | 描述                                |
| :--------- | :------------------- | :---------------------------------- |
| **后端**   | FastAPI              | 高性能 Web 框架                     |
|            | Python 3.12+         | 核心编程语言                        |
|            | uv                   | 高效的 Python 包管理器              |
|            | SQLAlchemy           | 数据库 ORM (对象关系映射)           |
| **前端**   | Vue.js 3             | 渐进式 JavaScript 框架              |
|            | TypeScript           | JavaScript 的超集，提供类型安全     |
|            | Vite                 | 下一代前端构建工具                  |
|            | Element Plus         | 基于 Vue 3 的 UI 组件库             |
|            | ECharts              | 用于数据可视化的图表库              |
| **AI/ML**  | OpenAI, Qwen, Kimi   | 大型语言模型服务 (LLM)              |
|            | Tesseract, PaddleOCR | 光学字符识别引擎 (OCR)              |
| **数据库** | PostgreSQL           | 关系型数据库 (通过 `psycopg2` 推断) |

## 3. 项目结构

```
/
├── src/ai_tutor/       # 后端 FastAPI 源代码
│   ├── api/            # API 路由和端点
│   ├── core/           # 配置、依赖项和日志
│   ├── db/             # 数据库设置和模型
│   └── services/       # 核心业务逻辑 (AI, OCR, 学生管理等)
├── frontend/           # 前端 Vue.js 源代码
│   ├── src/
│   │   ├── views/      # 应用的主要页面
│   │   ├── components/ # 可复用的 UI 组件
│   │   ├── router/     # 前端路由
│   │   └── services/   # 与后端 API 的交互
│   └── package.json    # 前端依赖和脚本
├── tests/              # 后端测试代码
├── Makefile            # 常用开发命令的快捷方式
├── pyproject.toml      # Python 项目定义和依赖 (uv)
└── README.md           # 项目详细介绍文档
```

## 4. 环境搭建与运行

### 后端

1.  **安装依赖:**

    ```bash
    # 确保已安装 uv
    uv sync
    ```

2.  **配置环境:**
    复制 `.env.example` 为 `.env`，并填入所需的 API 密钥。

    ```bash
    cp .env.example .env
    ```

3.  **启动开发服务器:**
    ```bash
    make dev
    ```
    后端服务将在 `http://localhost:8000` 上可用。API 文档位于 `http://localhost:8000/docs`。

### 前端

1.  **进入前端目录并安装依赖:**

    ```bash
    cd frontend
    npm install
    ```

2.  **启动开发服务器:**
    ```bash
    npm run dev
    ```
    前端应用将在 `http://localhost:6173` 上可用。

## 5. 核心开发命令

项目根目录下的 `Makefile` 提供了一系列快捷命令以简化开发流程。

- `make dev`: 启动后端开发服务器（带热重载）。
- `make test`: 运行后端的 `pytest` 测试套件。
- `make lint`: 对后端代码执行 `flake8` 和 `mypy` 静态检查。
- `make format`: 使用 `black` 格式化后端代码。
- `make install`: 等同于 `uv sync`，安装 Python 依赖。
- `make help`: 显示所有可用的命令及其描述。
