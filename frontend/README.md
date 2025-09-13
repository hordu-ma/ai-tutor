# AI Tutor Frontend - 学情管理AI助教前端

基于 Vue 3 + TypeScript + Element Plus 构建的现代化学情管理系统前端应用。

## 🎯 项目概述

这是 AI Tutor 学情管理系统的前端部分，提供了一个直观、易用的学习分析仪表盘。学生可以通过该界面：

- 📊 查看个人学习进度和知识点掌握情况
- ⚡ 进行单题快速分析
- 📈 了解错误模式和学习趋势
- 📋 查看作业批改历史
- 🎯 获得个性化学习改进建议

## ✨ 核心功能

### 🏠 学习仪表盘

- **知识点掌握情况**: 可视化展示各科目知识点掌握度
- **错误模式分析**: 智能识别学习中的常见错误类型
- **个性化改进计划**: 基于 AI 分析的学习建议
- **学习统计**: 作业完成数量、平均分等关键指标

### ⚡ 单题快速分析

- **实时分析**: 输入题目和答案，获得即时 AI 分析
- **错误分类**: 智能识别错误类型和严重程度
- **改进建议**: 提供具体的学习改进建议
- **相关概念**: 关联相关知识点和概念

### 📚 批改历史

- **历史记录**: 完整的作业提交和批改历史
- **智能过滤**: 按科目、状态、时间等条件筛选
- **详细报告**: 查看每次作业的详细分析报告

## 🛠️ 技术栈

- **框架**: Vue 3.5+ (Composition API)
- **语言**: TypeScript 5.8+
- **构建工具**: Vite 7.1+
- **UI组件库**: Element Plus 2.11+
- **图标库**: @element-plus/icons-vue
- **HTTP客户端**: Axios 1.12+
- **路由**: Vue Router 4.5+
- **包管理器**: npm

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/         # 可复用组件
│   │   └── ImprovementPlan.vue
│   ├── layouts/           # 布局组件
│   │   └── DefaultLayout.vue
│   ├── views/             # 页面组件
│   │   ├── DashboardView.vue      # 仪表盘
│   │   ├── QuickAnalysisView.vue  # 单题分析
│   │   └── HistoryView.vue        # 历史记录
│   ├── services/          # API服务
│   │   ├── api.ts         # 主API服务
│   │   └── mockData.ts    # 模拟数据服务
│   ├── router/            # 路由配置
│   │   └── index.ts
│   ├── types/             # TypeScript类型定义
│   │   ├── auto-imports.d.ts
│   │   └── components.d.ts
│   ├── env.d.ts          # 环境类型声明
│   ├── main.ts           # 应用入口
│   └── App.vue           # 根组件
├── public/               # 静态资源
├── .env.development     # 开发环境配置
├── .env.production      # 生产环境配置
├── vite.config.ts       # Vite配置
├── tsconfig.app.json    # TypeScript配置
└── package.json         # 项目依赖
```

## 🚀 快速开始

### 环境要求

- Node.js 18.0+
- npm 9.0+

### 安装与运行

```bash
# 进入前端目录
cd ai-tutor/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问应用
# 开发环境: http://localhost:6173
```

### 构建部署

```bash
# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🔧 开发配置

### 环境变量

在 `.env.development` 中配置开发环境变量：

```bash
# API 配置
VITE_API_BASE_URL=/api
VITE_USE_MOCK=false

# 应用配置
VITE_APP_TITLE=AI Tutor - 学情管理AI助教
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development

# 开发功能
VITE_DEV_TOOLS=true
VITE_DEBUG_MODE=true
VITE_ENABLE_MOCK_FALLBACK=true
```

### 模拟数据模式

当后端 API 不可用时，系统会自动切换到模拟数据模式，确保前端功能正常展示。

要手动启用模拟数据模式，请设置：

```bash
VITE_USE_MOCK=true
```

### 代理配置

开发服务器已配置 API 代理，所有 `/api` 开头的请求会被转发到后端服务（默认 `http://127.0.0.1:8000`）。

## 🎨 UI 设计规范

### 色彩系统

- **主色**: #409EFF (Element Plus 蓝)
- **成功色**: #67C23A (绿色)
- **警告色**: #E6A23C (橙色)
- **危险色**: #F56C6C (红色)
- **信息色**: #909399 (灰色)

### 组件规范

- 使用 Element Plus 组件库确保界面一致性
- 响应式设计，支持移动端和桌面端
- 中文界面，符合国内用户习惯
- 图标统一使用 Element Plus Icons

## 📊 功能特性

### 🔄 自动刷新与实时性

- 数据自动刷新机制
- 实时错误提示和成功反馈
- 加载状态和进度指示

### 🎯 智能交互

- 表单验证和用户引导
- 快速示例和模板
- 智能搜索和过滤

### 📱 响应式设计

- 移动端优先的设计理念
- 桌面端增强体验
- 灵活的栅格布局系统

## 🔌 API 集成

### 接口规范

所有 API 请求都通过统一的 `apiService` 进行管理，支持：

- 自动错误处理和重试
- 请求/响应拦截
- 模拟数据降级
- TypeScript 类型安全

### 主要接口

- `GET /api/v1/students/{id}/progress/knowledge-points` - 获取知识点掌握情况
- `POST /api/v1/error-analysis/analyze-question` - 单题错误分析
- `GET /api/v1/error-analysis/students/{id}/patterns/{subject}` - 错误模式分析
- `GET /api/v1/students/{id}/homework` - 作业历史记录

## 🧪 开发与测试

### 代码质量

- **TypeScript**: 严格类型检查
- **ESLint**: 代码质量检查
- **Prettier**: 代码格式化
- **Vue SFC**: 单文件组件规范

### 性能优化

- **按需加载**: 路由和组件懒加载
- **Tree Shaking**: 自动移除未使用代码
- **代码分割**: Vite 自动优化打包
- **缓存策略**: 静态资源缓存

## 🚧 路线图

### ✅ 第一阶段完成 (当前版本)

- [x] 基础框架搭建 (Vue 3 + TypeScript)
- [x] 核心页面开发 (仪表盘、单题分析、历史记录)
- [x] Element Plus UI 集成
- [x] 响应式布局设计
- [x] API 服务层封装
- [x] 模拟数据支持
- [x] 中文界面本地化

### 🎯 第二阶段规划

- [ ] 数据可视化增强 (图表库集成)
- [ ] 知识图谱可视化
- [ ] 多轮对话式批改界面
- [ ] PWA 支持 (离线使用)
- [ ] 主题切换功能

### 🚀 第三阶段规划

- [ ] 多角色支持 (教师、家长视图)
- [ ] PDF 报告生成和下载
- [ ] 实时通知系统
- [ ] 移动端 App 开发

## 📝 许可证

MIT License

---

**开发团队**: AI Tutor 项目组
**技术支持**: 如有问题请查看项目文档或联系开发团队
**更新时间**: 2024年1月
