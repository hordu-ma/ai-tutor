# AI Tutor 智能学习管理系统 🎓

> 基于AI的智能学习管理系统，专注于作业批改、错误分析和个性化学习指导

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 🌟 项目概述

AI Tutor 是一个全栈智能学习管理系统，通过OCR技术识别手写作业内容，结合AI大模型进行智能批改和错误分析，为学生提供个性化的学习改进建议。

### ✨ 核心特性

- 🤖 **AI智能批改** - 支持数学、物理、英语多学科作业自动批改
- 📊 **错误趋势分析** - 深度学习模式识别，提供可视化错误分析
- 🎯 **个性化辅导** - AI驱动的智能问答和学习指导
- 👥 **学生管理** - 完整的学生信息管理和学习追踪系统
- 📈 **多科目汇总** - 跨学科综合学习分析和能力评估

## 🚀 快速开始

### 前置要求

- **Node.js** 18+ (前端开发)
- **Python** 3.12+ (后端开发)
- **uv** (Python包管理)

### 🎨 前端启动

```bash
# 进入前端目录
cd ai-tutor/frontend

# 安装依赖
npm install

# 启动开发服务器 (默认端口: 6173)
npm run dev
```

访问: http://localhost:6173

### 🔧 后端启动

```bash
# 进入项目根目录
cd ai-tutor

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置API密钥

# 启动后端服务器
make dev
```

访问: http://localhost:8000/docs (API文档)

## 📱 功能模块

### 🏆 高优先级功能 (100% 完成)

| 功能模块        | 文件                          | 状态    | 描述                             |
| --------------- | ----------------------------- | ------- | -------------------------------- |
| 🤖 AI智能辅导   | `AiChatView.vue`              | ✅ 完成 | 实时AI对话、多模型支持、聊天历史 |
| 👥 学生管理系统 | `StudentManagementView.vue`   | ✅ 完成 | CRUD操作、批量管理、详细统计     |
| 📊 错误趋势分析 | `ErrorTrendsView.vue`         | ✅ 完成 | 多维数据可视化、趋势图表         |
| 📈 多科目汇总   | `MultiSubjectSummaryView.vue` | ✅ 完成 | 跨科目分析、能力雷达图           |
| 📋 批改历史     | `HistoryView.vue`             | ✅ 完成 | 历史记录管理、成绩追踪           |

### 📋 中优先级功能 (100% 完成)

| 功能模块      | 文件                     | 状态    | 描述                   |
| ------------- | ------------------------ | ------- | ---------------------- |
| 🏠 学习仪表盘 | `DashboardView.vue`      | ✅ 完成 | 概览统计、知识点雷达图 |
| 📤 作业上传   | `HomeworkUploadView.vue` | ✅ 完成 | 多格式上传、智能批改   |
| ⚡ 单题分析   | `QuickAnalysisView.vue`  | ✅ 完成 | 快速错误分析、改进建议 |

## 🛠 技术栈

### 前端技术

- **框架**: Vue 3 + TypeScript + Composition API
- **构建工具**: Vite (快速构建和热更新)
- **UI组件库**: Element Plus (中文本地化)
- **数据可视化**: ECharts (专业图表库)
- **路由管理**: Vue Router 4
- **HTTP客户端**: Axios
- **代码规范**: ESLint + Prettier

### 后端技术

- **Web框架**: FastAPI + Python 3.12
- **包管理**: uv (现代Python包管理器)
- **AI服务**: 通义千问 (Qwen) / Kimi AI
- **OCR引擎**: Tesseract OCR
- **数据库**: SQLAlchemy ORM
- **API文档**: 自动生成OpenAPI/Swagger

## 🎯 系统架构

```
AI Tutor 系统架构
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   后端API层     │    │   AI服务层      │
│                 │    │                 │    │                 │
│ Vue 3 + TS      │◄──►│ FastAPI        │◄──►│ Qwen / Kimi     │
│ Element Plus    │    │ Python 3.12    │    │ OCR Engine      │
│ ECharts         │    │ SQLAlchemy     │    │ 错误分析引擎     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 核心功能展示

### 🤖 AI智能辅导

- **多AI模型支持**: 通义千问、Kimi AI自由切换
- **实时对话**: 流式响应，类ChatGPT体验
- **上下文记忆**: 智能对话历史管理
- **个性化设置**: 温度参数、最大令牌数可调

### 📈 数据可视化分析

- **错误趋势图**: 时间序列数据展示学习进步
- **知识点雷达图**: 多维度能力评估可视化
- **科目对比图**: 跨学科学习表现对比
- **交互式图表**: 支持缩放、筛选、导出

### 👥 智能学生管理

- **批量操作**: 支持批量导入、导出、删除
- **高级搜索**: 多条件组合筛选
- **详细统计**: 个人学习数据深度分析
- **状态管理**: 激活/停用状态智能管理

## 🔧 开发规范

### 代码质量保证

- ✅ **零TypeScript编译错误** - 严格类型检查
- ✅ **代码规范统一** - ESLint + Prettier配置
- ✅ **组件化设计** - 高复用性模块化架构
- ✅ **响应式适配** - 多设备完美适配
- ✅ **错误处理完善** - 统一异常处理机制

### 开发工作流

```bash
# 检查项目状态
npm run dev        # 前端开发服务器
make dev          # 后端开发服务器
make test         # 运行测试套件
make lint         # 代码质量检查
```

## 📚 项目文档

- 📋 [项目概述](./docs/AI_TUTOR_PROJECT_OVERVIEW.md) - 完整项目介绍
- 🚀 [API文档](http://localhost:8000/docs) - 后端接口文档
- 🎨 [前端组件](./frontend/src/components/) - 组件库文档
- 🧪 [测试报告](./tests/) - 测试覆盖率报告

## 🎯 应用场景

### 👨‍🎓 学生个人使用

- 作业自助批改和即时反馈
- AI辅导问答和学习答疑
- 个性化学习进度追踪
- 错误模式深度分析

### 👨‍🏫 教师课堂使用

- 批量作业智能处理
- 班级学习数据统计
- 个别学生针对性指导
- 教学重点动态调整

### 👨‍👩‍👧‍👦 家长辅导使用

- 孩子学习状况监控
- 学习进步可视化展示
- 科学家庭辅导建议
- 学习习惯培养支持

## 📈 开发里程碑

### ✅ 第一阶段: 核心功能完成 (已完成)

- [x] 8个核心功能模块全部实现
- [x] 前后端API完整对接
- [x] 零编译错误，代码质量达标
- [x] UI/UX设计完善，用户体验优秀

### 🚧 第二阶段: 功能增强 (进行中)

- [ ] Dashboard数据可视化增强
- [ ] 导出功能开发 (PDF/Excel)
- [ ] 批量操作功能完善
- [ ] 移动端适配优化

### 🎯 第三阶段: 高级特性 (规划中)

- [ ] 知识图谱构建
- [ ] 个性化学习路径
- [ ] 多语言国际化
- [ ] 性能优化升级

## 🔐 环境配置

### 后端环境变量 (.env)

```bash
# AI服务配置
QWEN_API_KEY=your_qwen_api_key
KIMI_API_KEY=your_kimi_api_key

# OCR服务配置
OCR_ENGINE=paddleocr

# 服务配置
DEBUG=true
LOG_LEVEL=INFO
```

### 前端环境变量 (.env.local)

```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK=false
```

## 🧪 测试策略

- **前端测试**: 组件单元测试 + E2E测试
- **后端测试**: API接口测试 + 业务逻辑测试
- **集成测试**: 前后端联调测试
- **性能测试**: 并发压力测试

## 🤝 贡献指南

1. **Fork** 本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 **Pull Request**

### 提交信息规范

```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具链更新
```

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。

## 🏆 项目成果

### 开发成果总结

- ✅ **8个完整功能模块** - 覆盖学习管理全流程
- ✅ **35+ API接口** - 完整后端服务体系
- ✅ **零编译错误** - 高质量代码标准
- ✅ **现代化UI设计** - 专业用户界面
- ✅ **TypeScript全覆盖** - 类型安全保证

### 技术亮点

- 🚀 **现代化技术栈** - Vue 3 + FastAPI最佳实践
- 🤖 **AI深度集成** - 多模型智能服务
- 📱 **响应式设计** - 多设备完美适配
- 🎨 **用户体验优秀** - 直观易用的交互设计
- 🔧 **高可维护性** - 清晰架构和代码规范

---

**⭐ 如果这个项目对你有帮助，请给个Star支持！**

**📧 联系方式**: [项目Issue](https://github.com/your-repo/ai-tutor/issues)

**🔗 在线演示**: [Demo地址](http://your-demo-url.com)

---

_最后更新: 2024年12月_
_项目状态: 核心功能完成，正在功能增强阶段_
