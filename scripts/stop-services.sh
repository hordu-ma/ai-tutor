#!/bin/bash

# AI Tutor 服务停止脚本
# 优雅地停止前端和后端服务

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

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=6173

# 日志目录
LOGS_DIR="${PROJECT_ROOT}/logs"

# PID文件
BACKEND_PID_FILE="${LOGS_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOGS_DIR}/frontend.pid"

# 通过端口查找并终止进程
kill_by_port() {
    local port=$1
    local service_name=$2

    echo -e "${BLUE}🔍 检查端口 $port ($service_name)...${NC}"

    local pids=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}⏳ 正在停止 $service_name (端口 $port)...${NC}"
        for pid in $pids; do
            echo -e "${BLUE}   终止进程 $pid${NC}"
            kill -TERM $pid 2>/dev/null || true
        done

        # 等待进程优雅退出
        sleep 3

        # 检查是否还有进程存在
        local remaining_pids=$(lsof -ti :$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo -e "${YELLOW}⚠️  强制终止残留进程...${NC}"
            for pid in $remaining_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi

        echo -e "${GREEN}✅ $service_name 已停止${NC}"
    else
        echo -e "${BLUE}ℹ️  $service_name 未运行${NC}"
    fi
}

# 通过PID文件停止服务
kill_by_pid() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}⏳ 停止 $service_name (PID: $pid)...${NC}"
            kill -TERM "$pid" 2>/dev/null || true

            # 等待进程退出
            for i in {1..10}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    echo -e "${GREEN}✅ $service_name 已优雅停止${NC}"
                    break
                fi
                sleep 1
            done

            # 如果进程仍然存在，强制终止
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  强制终止 $service_name...${NC}"
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi

        # 删除PID文件
        rm -f "$pid_file"
    fi
}

# 停止后端服务
stop_backend() {
    echo -e "${PURPLE}🛑 停止后端服务...${NC}"

    # 先尝试通过PID文件停止
    kill_by_pid "$BACKEND_PID_FILE" "后端服务"

    # 再通过端口检查并清理
    kill_by_port $BACKEND_PORT "后端服务"

    # 停止相关的uvicorn进程
    local uvicorn_pids=$(pgrep -f "uvicorn.*ai_tutor" 2>/dev/null || true)
    if [ -n "$uvicorn_pids" ]; then
        echo -e "${YELLOW}⏳ 停止uvicorn进程...${NC}"
        for pid in $uvicorn_pids; do
            kill -TERM $pid 2>/dev/null || true
        done
        sleep 2
        # 检查是否还有残留
        local remaining_uvicorn=$(pgrep -f "uvicorn.*ai_tutor" 2>/dev/null || true)
        if [ -n "$remaining_uvicorn" ]; then
            for pid in $remaining_uvicorn; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
    fi
}

# 停止前端服务
stop_frontend() {
    echo -e "${PURPLE}🛑 停止前端服务...${NC}"

    # 先尝试通过PID文件停止
    kill_by_pid "$FRONTEND_PID_FILE" "前端服务"

    # 再通过端口检查并清理
    kill_by_port $FRONTEND_PORT "前端服务"

    # 停止相关的node/npm/vite进程
    local node_pids=$(pgrep -f "node.*vite" 2>/dev/null || true)
    if [ -n "$node_pids" ]; then
        echo -e "${YELLOW}⏳ 停止vite进程...${NC}"
        for pid in $node_pids; do
            # 检查进程是否与当前项目相关
            if ps -p $pid -o args= | grep -q "${PROJECT_ROOT}/frontend" 2>/dev/null; then
                kill -TERM $pid 2>/dev/null || true
            fi
        done
        sleep 2
    fi

    # 停止npm进程
    local npm_pids=$(pgrep -f "npm.*dev" 2>/dev/null || true)
    if [ -n "$npm_pids" ]; then
        echo -e "${YELLOW}⏳ 停止npm进程...${NC}"
        for pid in $npm_pids; do
            if ps -p $pid -o args= | grep -q "frontend" 2>/dev/null; then
                kill -TERM $pid 2>/dev/null || true
            fi
        done
    fi
}

# 清理临时文件
cleanup_files() {
    echo -e "${BLUE}🧹 清理临时文件...${NC}"

    # 清理PID文件
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"

    # 清理旧的日志文件（可选）
    if [ "$1" = "--clean-logs" ]; then
        echo -e "${YELLOW}🗑️  清理日志文件...${NC}"
        rm -f "${LOGS_DIR}/backend.log" "${LOGS_DIR}/frontend.log"
    fi

    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 验证服务已停止
verify_stopped() {
    echo -e "${BLUE}🔍 验证服务状态...${NC}"

    local backend_running=false
    local frontend_running=false

    # 检查后端端口
    if lsof -i :$BACKEND_PORT >/dev/null 2>&1; then
        echo -e "${RED}❌ 后端服务仍在运行 (端口 $BACKEND_PORT)${NC}"
        backend_running=true
    else
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    fi

    # 检查前端端口
    if lsof -i :$FRONTEND_PORT >/dev/null 2>&1; then
        echo -e "${RED}❌ 前端服务仍在运行 (端口 $FRONTEND_PORT)${NC}"
        frontend_running=true
    else
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    fi

    if [ "$backend_running" = true ] || [ "$frontend_running" = true ]; then
        echo -e "${YELLOW}⚠️  部分服务可能未完全停止，请手动检查${NC}"
        return 1
    fi

    return 0
}

# 显示帮助信息
show_help() {
    echo -e "${PURPLE}🏠 AI Tutor - 服务停止脚本${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --clean-logs    同时清理日志文件"
    echo "  --force         强制停止所有相关进程"
    echo "  --stop-db       同时停止PostgreSQL数据库"
    echo "  --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                # 正常停止服务"
    echo "  $0 --clean-logs   # 停止服务并清理日志"
    echo "  $0 --force        # 强制停止所有进程"
    echo "  $0 --stop-db      # 停止服务并停止数据库"
}

# 停止PostgreSQL数据库
stop_postgresql() {
    echo -e "${PURPLE}🛑 停止PostgreSQL数据库...${NC}"

    if brew services list | grep postgresql@15 | grep -q started; then
        echo -e "${YELLOW}⏳ 正在停止PostgreSQL服务...${NC}"
        brew services stop postgresql@15
        echo -e "${GREEN}✅ PostgreSQL服务已停止${NC}"
    else
        echo -e "${BLUE}ℹ️  PostgreSQL服务未运行${NC}"
    fi
}

# 强制停止模式
force_stop() {
    echo -e "${RED}⚠️  强制停止模式${NC}"

    # 强制终止所有相关进程
    pkill -9 -f "uvicorn.*ai_tutor" 2>/dev/null || true
    pkill -9 -f "npm.*dev" 2>/dev/null || true
    pkill -9 -f "node.*vite" 2>/dev/null || true

    # 通过端口强制清理
    lsof -ti :$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    lsof -ti :$FRONTEND_PORT | xargs kill -9 2>/dev/null || true

    # 检查是否需要停止数据库
    for arg in "$@"; do
        if [ "$arg" = "--stop-db" ]; then
            stop_postgresql
            break
        fi
    done

    cleanup_files "$@"

    echo -e "${GREEN}✅ 强制停止完成${NC}"
}

# 主函数
main() {
    # 解析命令行参数
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --force)
            force_stop "$@"
            exit 0
            ;;
    esac

    echo -e "${PURPLE}🏠 AI Tutor - 服务停止脚本${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # 停止服务
    stop_backend
    stop_frontend

    # 检查是否需要停止数据库
    for arg in "$@"; do
        if [ "$arg" = "--stop-db" ]; then
            stop_postgresql
            break
        fi
    done

    # 清理文件
    cleanup_files "$@"

    # 验证停止状态
    if verify_stopped; then
        echo -e "\n${GREEN}🎉 所有服务已成功停止！${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}🚀 重新启动服务: ./scripts/start-services.sh${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        echo -e "\n${YELLOW}⚠️  请检查进程状态并手动清理残留进程${NC}"
        echo -e "${BLUE}💡 使用 --force 参数强制停止: $0 --force${NC}"
        exit 1
    fi
}

# 运行主函数
main "$@"
