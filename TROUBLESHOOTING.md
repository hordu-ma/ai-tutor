# AI Tutor 问题解决指南 🔧

本文档提供常见问题的快速解决方案。

## 🚀 快速启动

### 正常启动
```bash
make dev
```

### 如果启动失败，尝试稳定模式
```bash
make dev-stable
```

### 调试模式启动
```bash
make dev-debug
```

## 🛠️ 常见问题及解决方案

### 1. 服务器启动失败

**症状**：`make dev` 命令无响应或启动失败

**解决方案**：
```bash
# 方案1：使用稳定模式
make dev-stable

# 方案2：手动清理进程
pkill -f uvicorn
make dev

# 方案3：检查端口占用
lsof -ti:8000
# 如果有进程占用，杀掉进程
kill -9 $(lsof -ti:8000)
```

### 2. 作业批改失败 (HTTP 500错误)

**症状**：前端显示"作业批改失败"，控制台显示500错误

**可能原因及解决方案**：

#### A. API密钥问题
```bash
# 检查配置
uv run python -c "from src.ai_tutor.core.config import settings; print('QWEN_API_KEY:', 'YES' if settings.QWEN_API_KEY else 'NO')"

# 如果显示NO，请在.env文件中配置API密钥
```

#### B. 服务依赖问题
```bash
# 运行诊断脚本
uv run python diagnose_error.py

# 测试API连接
uv run python test_api_upload.py --quick
```

#### C. 代码错误
查看服务器日志，通常会显示具体错误信息

### 3. OCR识别失败

**症状**：上传图片后OCR文本为空

**解决方案**：
```bash
# 检查tesseract安装
tesseract --version

# macOS重新安装
brew reinstall tesseract tesseract-lang

# Ubuntu/Debian重新安装
sudo apt-get install --reinstall tesseract-ocr tesseract-ocr-chi-sim
```

### 4. 文件上传失败

**症状**：文件选择后无法上传或提示文件格式错误

**检查清单**：
- [ ] 文件格式是否为 JPG、PNG、WEBP
- [ ] 文件大小是否小于10MB
- [ ] 网络连接是否正常

### 5. 前端页面无法访问

**症状**：浏览器显示"无法访问此网站"

**解决方案**：
```bash
# 检查服务器状态
curl http://localhost:8000/health

# 如果失败，重启服务器
pkill -f uvicorn
make dev-stable
```

## 🔍 调试工具

### 1. 健康检查
```bash
# 基础健康检查
curl http://localhost:8000/health

# 作业批改服务检查
curl http://localhost:8000/api/v1/homework/health
```

### 2. 完整诊断
```bash
# 运行完整诊断
uv run python diagnose_error.py

# API功能测试
uv run python test_api_upload.py --comprehensive
```

### 3. 日志查看
服务器运行时，注意查看终端输出的日志信息，通常包含：
- 请求处理信息
- 错误详情
- 处理时间统计

## 📞 获取帮助

### 查看详细错误信息
1. 打开浏览器开发者工具（F12）
2. 查看Console标签页的错误信息
3. 查看Network标签页的网络请求状态

### 常用调试命令
```bash
# 检查依赖
uv sync

# 检查代码语法
uv run python -m py_compile src/ai_tutor/main.py

# 重新安装依赖
rm uv.lock
uv sync
```

## 🔄 重置系统

如果问题持续存在，可以尝试完全重置：

```bash
# 1. 停止所有相关进程
pkill -f uvicorn
pkill -f "ai_tutor"

# 2. 清理缓存
make clean

# 3. 重新安装依赖
uv sync

# 4. 重新启动
make dev-stable
```

## 📋 报告问题

如果问题仍未解决，请提供以下信息：

1. **错误现象**：详细描述问题表现
2. **浏览器控制台错误**：F12 → Console中的错误信息
3. **服务器日志**：终端中显示的错误信息
4. **环境信息**：
   ```bash
   python --version
   uv --version
   tesseract --version
   ```
5. **重现步骤**：如何一步步触发问题

## 💡 预防措施

### 定期维护
```bash
# 每周运行一次
uv sync                    # 更新依赖
make test                  # 运行测试
make clean                 # 清理缓存
```

### 监控资源
- 确保磁盘空间充足（至少1GB可用）
- 确保内存可用（推荐4GB以上）
- 确保网络连接稳定（AI API调用需要）

---

**最后更新**：2025-09-11
**版本**：v1.0
