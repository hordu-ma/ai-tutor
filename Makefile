.PHONY: install dev test lint format clean docker-up docker-down help

# 默认目标
help:
	@echo "AI Tutor - 学情管理AI助教"
	@echo ""
	@echo "可用命令:"
	@echo "  install       - 安装项目依赖"
	@echo "  dev          - 启动开发服务器"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码质量检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理缓存文件"
	@echo "  docker-up    - 启动Docker服务"
	@echo "  docker-down  - 停止Docker服务"

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	uv sync

# 启动开发服务器
dev:
	@echo "🚀 启动开发服务器..."
	uv run uvicorn src.ai_tutor.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
test:
	@echo "🧪 运行测试..."
	uv run pytest -v

# 运行测试覆盖率
test-cov:
	@echo "📊 运行测试覆盖率..."
	uv run pytest --cov=src/ai_tutor --cov-report=html --cov-report=term

# 代码质量检查
lint:
	@echo "🔍 代码质量检查..."
	uv run flake8 src/ tests/
	uv run mypy src/

# 代码格式化
format:
	@echo "✨ 代码格式化..."
	uv run black src/ tests/

# 格式检查（不修改文件）
format-check:
	@echo "✅ 检查代码格式..."
	uv run black --check src/ tests/

# 清理缓存文件
clean:
	@echo "🧹 清理缓存文件..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache

# 启动Docker服务
docker-up:
	@echo "🐳 启动Docker服务..."
	docker-compose up -d

# 停止Docker服务
docker-down:
	@echo "🛑 停止Docker服务..."
	docker-compose down

# 重启Docker服务
docker-restart:
	@echo "🔄 重启Docker服务..."
	docker-compose down
	docker-compose up -d

# 查看Docker日志
docker-logs:
	@echo "📜 查看服务日志..."
	docker-compose logs -f

# 健康检查
health:
	@echo "💚 检查服务健康状态..."
	@curl -s http://localhost:8000/health || echo "❌ 服务未启动"
	@curl -s http://localhost:8000/api/v1/health || echo "❌ API服务未启动"
	@curl -s http://localhost:8000/api/v1/ocr/health || echo "❌ OCR服务未启动"

# 一键设置开发环境
setup-dev:
	@echo "🛠️  设置开发环境..."
	cp .env.example .env
	@echo "✅ 已创建 .env 文件，请编辑配置您的API密钥"
	$(MAKE) install
	@echo "🎉 开发环境设置完成！运行 'make dev' 启动服务"

# 生产构建
build:
	@echo "🏗️  构建生产镜像..."
	docker build -t ai-tutor:latest .

# 运行生产环境
prod:
	@echo "🚀 启动生产环境..."
	docker run -p 8000:8000 --env-file .env ai-tutor:latest

# 测试服务
test-services:
	@echo "🧪 测试核心服务..."
	uv run python -c "from src.ai_tutor.services.student import HomeworkService; from src.ai_tutor.services.llm import get_llm_service; from src.ai_tutor.services.ocr import get_ocr_service; print('✅ 所有服务正常')"

# 启动开发服务器（特定端口）
dev-test:
	@echo "🧪 启动测试开发服务器（端口8001）..."
	uv run uvicorn src.ai_tutor.main:app --reload --host 0.0.0.0 --port 8001

# API快速测试
api-test:
	@echo "🔗 测试API端点..."
	@echo "健康检查:"
	@curl -s http://localhost:8000/health | jq . || echo "❌ 服务未启动"
	@echo "\nOCR服务检查:"
	@curl -s http://localhost:8000/api/v1/ocr/health | jq . || echo "❌ OCR服务异常"
	@echo "\n作业批改服务检查:"
	@curl -s http://localhost:8000/api/v1/homework/health | jq . || echo "❌ 批改服务异常"
