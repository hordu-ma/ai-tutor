#!/bin/bash

# AI Tutor 服务启动脚本
# 优雅地启动前端和后端服务

set -e

# 配置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=6173

# 日志目录
LOGS_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOGS_DIR}"

# 日志文件
BACKEND_LOG="${LOGS_DIR}/backend.log"
FRONTEND_LOG="${LOGS_DIR}/frontend.log"

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2

    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 $port 已被占用 ($service_name)${NC}"
        echo -e "${BLUE}🔍 正在检查占用进程...${NC}"
        lsof -i :$port
        echo
        read -p "是否要终止占用进程并继续？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}🔄 正在终止端口 $port 上的进程...${NC}"
            lsof -ti :$port | xargs kill -9 2>/dev/null || true
            sleep 2
        else
            echo -e "${RED}❌ 启动取消${NC}"
            exit 1
        fi
    fi
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 检查依赖...${NC}"

    # 检查 uv
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv 未安装，请先安装 uv${NC}"
        exit 1
    fi

    # 检查 node 和 npm
    if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ Node.js 或 npm 未安装${NC}"
        exit 1
    fi

    # 检查前端依赖
    if [ ! -d "${FRONTEND_DIR}/node_modules" ]; then
        echo -e "${YELLOW}⚠️  前端依赖未安装，正在安装...${NC}"
        cd "${FRONTEND_DIR}"
        npm install
    fi

    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 检查并启动PostgreSQL
check_postgresql() {
    echo -e "${BLUE}🔍 检查PostgreSQL服务...${NC}"

    # 检查PostgreSQL是否安装
    if ! command -v /opt/homebrew/opt/postgresql@15/bin/psql &> /dev/null; then
        echo -e "${YELLOW}⚠️  PostgreSQL未安装，正在安装...${NC}"
        brew install postgresql@15
    fi

    # 检查PostgreSQL服务是否运行
    if ! brew services list | grep postgresql@15 | grep -q started; then
        echo -e "${BLUE}🚀 启动PostgreSQL服务...${NC}"
        brew services start postgresql@15
        sleep 3
    fi

    # 测试数据库连接
    export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
    if ! psql -U user -d ai_tutor -c "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  数据库连接失败，可能需要初始化...${NC}"
        echo -e "${BLUE}📋 创建数据库用户和数据库...${NC}"

        # 创建用户和数据库（如果不存在）
        createuser -s user 2>/dev/null || true
        createdb -O user ai_tutor 2>/dev/null || true
        psql -U user ai_tutor -c "ALTER USER \"user\" WITH PASSWORD 'pass';" 2>/dev/null || true

        # 运行数据库初始化
        echo -e "${BLUE}🔧 初始化数据库...${NC}"
        cd "${PROJECT_ROOT}"
        python scripts/init_db.py
    fi

    echo -e "${GREEN}✅ PostgreSQL服务正常${NC}"
}

# 启动后端服务
start_backend() {
    echo -e "${PURPLE}🚀 启动后端服务...${NC}"

    cd "${PROJECT_ROOT}"

    # 检查环境配置
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env 文件不存在，正在从 .env.example 复制...${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${YELLOW}⚠️  请编辑 .env 文件配置您的API密钥${NC}"
        else
            echo -e "${RED}❌ .env.example 文件不存在${NC}"
            exit 1
        fi
    fi

    # 启动后端（后台运行）
    echo -e "${BLUE}📝 后端日志: ${BACKEND_LOG}${NC}"
    nohup make dev > "${BACKEND_LOG}" 2>&1 &
    BACKEND_PID=$!

    # 等待后端启动
    echo -e "${BLUE}⏳ 等待后端启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
            echo -e "${GREEN}📍 后端地址: http://localhost:${BACKEND_PORT}${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
    done

    echo -e "\n${RED}❌ 后端启动超时${NC}"
    echo -e "${BLUE}📜 查看日志: tail -f ${BACKEND_LOG}${NC}"
    exit 1
}

# 启动前端服务
start_frontend() {
    echo -e "${PURPLE}🚀 启动前端服务...${NC}"

    cd "${FRONTEND_DIR}"

    # 启动前端（后台运行）
    echo -e "${BLUE}📝 前端日志: ${FRONTEND_LOG}${NC}"
    nohup npm run dev > "${FRONTEND_LOG}" 2>&1 &
    FRONTEND_PID=$!

    # 等待前端启动
    echo -e "${BLUE}⏳ 等待前端启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:${FRONTEND_PORT} >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
            echo -e "${GREEN}📍 前端地址: http://localhost:${FRONTEND_PORT}${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
    done

    echo -e "\n${RED}❌ 前端启动超时${NC}"
    echo -e "${BLUE}📜 查看日志: tail -f ${FRONTEND_LOG}${NC}"
    exit 1
}

# 保存进程ID
save_pids() {
    echo "${BACKEND_PID}" > "${LOGS_DIR}/backend.pid"
    echo "${FRONTEND_PID}" > "${LOGS_DIR}/frontend.pid"
    echo -e "${BLUE}💾 进程ID已保存到 ${LOGS_DIR}/${NC}"
}

# 显示服务状态
show_status() {
    echo -e "\n${GREEN}🎉 所有服务启动完成！${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📍 前端: http://localhost:${FRONTEND_PORT}${NC}"
    echo -e "${GREEN}📍 后端: http://localhost:${BACKEND_PORT}${NC}"
    echo -e "${GREEN}📍 API文档: http://localhost:${BACKEND_PORT}/docs${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📜 查看后端日志: tail -f ${BACKEND_LOG}${NC}"
    echo -e "${BLUE}📜 查看前端日志: tail -f ${FRONTEND_LOG}${NC}"
    echo -e "${BLUE}🛑 停止服务: ./scripts/stop-services.sh${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 主函数
main() {
    echo -e "${PURPLE}🏠 AI Tutor - 服务启动脚本${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # 检查端口
    check_port $BACKEND_PORT "后端服务"
    check_port $FRONTEND_PORT "前端服务"

    # 检查依赖
    check_dependencies

    # 检查PostgreSQL
    check_postgresql

    # 启动服务
    start_backend
    start_frontend

    # 保存进程ID
    save_pids

    # 显示状态
    show_status
}

# 捕获退出信号，清理资源
cleanup() {
    echo -e "\n${YELLOW}⚠️  接收到退出信号，正在清理...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 1
}

trap cleanup INT TERM

# 运行主函数
main "$@"
