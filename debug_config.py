#!/usr/bin/env python3
"""
配置调试脚本

用于诊断 AI Tutor 后端服务的配置问题，特别是环境变量加载问题。
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_env_loading():
    """检查环境变量加载情况"""
    print("🔧 配置调试工具")
    print("=" * 50)

    # 检查 .env 文件
    env_file = Path('.env')
    print(f"📁 .env 文件状态:")
    print(f"   存在: {'✅' if env_file.exists() else '❌'}")
    if env_file.exists():
        print(f"   大小: {env_file.stat().st_size} 字节")
        print(f"   修改时间: {env_file.stat().st_mtime}")

    print()

    # 手动加载环境变量
    print("🔄 手动加载 .env 文件...")
    load_dotenv(override=True)

    # 检查关键环境变量
    print("🔑 环境变量检查:")

    env_vars = {
        'QWEN_API_KEY': os.getenv('QWEN_API_KEY', ''),
        'KIMI_API_KEY': os.getenv('KIMI_API_KEY', ''),
        'DEBUG': os.getenv('DEBUG', ''),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', ''),
        'DATABASE_URL': os.getenv('DATABASE_URL', ''),
    }

    for key, value in env_vars.items():
        if value:
            if 'API_KEY' in key:
                # 隐藏敏感信息
                display_value = f"{value[:10]}...({len(value)} chars)" if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"   ✅ {key}: {display_value}")
        else:
            print(f"   ❌ {key}: 未设置")

    print()

    return env_vars

def check_backend_config():
    """检查后端配置加载"""
    print("⚙️  检查后端配置...")

    try:
        # 导入后端配置
        sys.path.insert(0, str(Path.cwd() / 'src'))
        from ai_tutor.core.config import settings

        print("✅ 后端配置模块加载成功")
        print(f"   QWEN_API_KEY: {'已配置' if settings.QWEN_API_KEY else '未配置'}")
        print(f"   KIMI_API_KEY: {'已配置' if settings.KIMI_API_KEY else '未配置'}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")

        return True

    except Exception as e:
        print(f"❌ 后端配置加载失败: {e}")
        return False

def test_ai_service():
    """测试 AI 服务初始化"""
    print("\n🤖 测试 AI 服务初始化...")

    try:
        sys.path.insert(0, str(Path.cwd() / 'src'))
        from ai_tutor.services.llm import get_llm_service

        # 测试 Qwen 服务
        try:
            qwen_service = get_llm_service("qwen")
            print("✅ Qwen 服务初始化成功")
        except Exception as e:
            print(f"❌ Qwen 服务初始化失败: {e}")

        # 测试 Kimi 服务
        try:
            kimi_service = get_llm_service("kimi")
            print("✅ Kimi 服务初始化成功")
        except Exception as e:
            print(f"❌ Kimi 服务初始化失败: {e}")

    except Exception as e:
        print(f"❌ AI 服务模块加载失败: {e}")

def generate_fix_suggestions(env_vars, backend_ok):
    """生成修复建议"""
    print("\n💡 问题诊断和修复建议:")
    print("=" * 50)

    # 检查 API 密钥问题
    if not env_vars.get('QWEN_API_KEY'):
        print("🔴 QWEN_API_KEY 未配置")
        print("   解决方案:")
        print("   1. 编辑 .env 文件，添加: QWEN_API_KEY=sk-your-key-here")
        print("   2. 确保 .env 文件在项目根目录")
        print()

    if not backend_ok:
        print("🔴 后端配置加载问题")
        print("   解决方案:")
        print("   1. 重启后端服务:")
        print("      - 停止当前服务 (Ctrl+C)")
        print("      - 重新运行: make dev")
        print("   2. 检查项目结构和依赖")
        print()

    # 如果环境变量正常但后端异常
    if env_vars.get('QWEN_API_KEY') and not backend_ok:
        print("🟡 环境变量正常但后端异常")
        print("   可能原因:")
        print("   1. 后端服务缓存了旧配置")
        print("   2. 配置文件路径问题")
        print("   3. 依赖版本冲突")
        print()
        print("   建议操作:")
        print("   1. 完全重启后端服务")
        print("   2. 运行: make clean && make install")
        print("   3. 确认 .env 文件在正确位置")
        print()

def main():
    """主函数"""
    print("开始配置诊断...\n")

    # 检查环境变量
    env_vars = check_env_loading()

    # 检查后端配置
    backend_ok = check_backend_config()

    # 测试 AI 服务
    test_ai_service()

    # 生成修复建议
    generate_fix_suggestions(env_vars, backend_ok)

    # 总结
    print("📋 诊断总结:")
    print("=" * 50)

    has_qwen = bool(env_vars.get('QWEN_API_KEY'))
    has_kimi = bool(env_vars.get('KIMI_API_KEY'))

    if has_qwen and has_kimi and backend_ok:
        print("🟢 配置完全正常!")
        print("   如果仍有问题，请重启后端服务")
    elif has_qwen or has_kimi:
        print("🟡 部分配置正常")
        print("   建议重启后端服务并重新测试")
    else:
        print("🔴 配置存在问题")
        print("   请按照上述建议修复配置")

    print("\n下一步:")
    print("1. 根据建议修复问题")
    print("2. 重启后端服务: make dev")
    print("3. 重新测试: python test_homework_api.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n诊断被用户中断")
    except Exception as e:
        print(f"\n诊断执行出错: {e}")
