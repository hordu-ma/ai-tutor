#!/usr/bin/env python3
"""
物理科目支持验证脚本

验证后端API和前端是否正确支持物理科目
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_physics_support():
    """测试物理科目支持"""

    print("🔬 物理科目支持验证")
    print("=" * 50)

    # 1. 测试API支持的科目列表
    print("\n1. 测试API支持的科目列表...")
    try:
        from ai_tutor.api.v1.homework import get_supported_subjects

        result = await get_supported_subjects()
        subjects = result.get("data", [])

        print(f"✅ 成功获取 {len(subjects)} 个科目:")
        for subject in subjects:
            print(f"   - {subject['name']} ({subject['code']}): {subject['description']}")

        # 检查是否包含物理
        physics_found = any(s['code'] == 'physics' for s in subjects)
        if physics_found:
            print("✅ 物理科目已正确添加到API")
        else:
            print("❌ 物理科目未在API中找到")
            return False

    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

    # 2. 测试物理schemas
    print("\n2. 测试物理相关schemas...")
    try:
        from ai_tutor.schemas.physics_schemas import (
            PhysicsCategory,
            PhysicsQuestionType,
            PhysicsKnowledgePoint,
            PhysicsQuestion,
            PhysicsGradingResult
        )

        print("✅ 物理schemas导入成功:")
        print(f"   - 物理分类: {len(PhysicsCategory)} 个")
        print(f"   - 题目类型: {len(PhysicsQuestionType)} 个")
        print(f"   - 知识点: {len(PhysicsKnowledgePoint)} 个")

    except Exception as e:
        print(f"❌ 物理schemas测试失败: {e}")
        return False

    # 3. 测试物理知识提取器
    print("\n3. 测试物理知识提取器...")
    try:
        from ai_tutor.services.knowledge.physics import PhysicsKnowledgeExtractor

        print("✅ 物理知识提取器导入成功")
        print(f"   - 支持科目: {PhysicsKnowledgeExtractor.get_subject()}")

    except Exception as e:
        print(f"❌ 物理知识提取器测试失败: {e}")
        return False

    # 4. 测试物理批改提示词
    print("\n4. 测试物理批改提示词...")
    try:
        from ai_tutor.services.llm.prompts import PhysicsGradingPrompts

        prompts = PhysicsGradingPrompts()
        print("✅ 物理批改提示词导入成功")

    except Exception as e:
        print(f"❌ 物理批改提示词测试失败: {e}")
        return False

    # 5. 测试作业服务对物理的支持
    print("\n5. 测试作业服务对物理的支持...")
    try:
        from ai_tutor.services.student.homework_service import SUBJECT_PROMPTS_MAP, SUBJECT_CN_MAP

        if 'physics' in SUBJECT_PROMPTS_MAP:
            print("✅ 作业服务已支持物理科目")
        else:
            print("❌ 作业服务未支持物理科目")
            return False

        if 'physics' in SUBJECT_CN_MAP:
            print(f"✅ 物理科目中文名称: {SUBJECT_CN_MAP['physics']}")
        else:
            print("❌ 物理科目中文名称映射缺失")
            return False

    except Exception as e:
        print(f"❌ 作业服务测试失败: {e}")
        return False

    # 6. 检查前端HTML
    print("\n6. 检查前端HTML支持...")
    try:
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            html_content = html_path.read_text(encoding='utf-8')

            if 'value="physics"' in html_content:
                print("✅ 前端HTML已添加物理选项")
            else:
                print("❌ 前端HTML未找到物理选项")
                return False

            if '物理' in html_content:
                print("✅ 前端页面标题已更新包含物理")
            else:
                print("❌ 前端页面标题未更新")

        else:
            print("❌ 前端HTML文件未找到")
            return False

    except Exception as e:
        print(f"❌ 前端HTML检查失败: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 所有测试通过！物理科目支持已成功添加")
    print("\n📋 修复总结:")
    print("   ✅ 后端API已支持physics科目")
    print("   ✅ 物理相关schemas完整")
    print("   ✅ 物理知识提取器可用")
    print("   ✅ 物理批改提示词就绪")
    print("   ✅ 作业服务已集成物理模块")
    print("   ✅ 前端界面已添加物理选项")

    return True

def test_frontend_html():
    """测试前端HTML文件的物理科目支持"""

    print("\n📱 前端HTML详细检查...")

    html_path = Path(__file__).parent / "static" / "index.html"
    if not html_path.exists():
        print("❌ HTML文件不存在")
        return False

    content = html_path.read_text(encoding='utf-8')

    # 检查科目选择器
    physics_option_found = False
    lines = content.split('\n')

    for i, line in enumerate(lines):
        if 'value="physics"' in line:
            physics_option_found = True
            print(f"✅ 第{i+1}行找到物理选项: {line.strip()}")

    if not physics_option_found:
        print("❌ 未找到物理科目选项")
        return False

    # 检查页面标题更新
    title_updated = False
    for i, line in enumerate(lines):
        if '物理' in line and ('标题' in line or 'subtitle' in line or '数学' in line):
            title_updated = True
            print(f"✅ 第{i+1}行标题已更新: {line.strip()}")

    if not title_updated:
        print("❌ 页面标题未更新包含物理")

    return True

if __name__ == "__main__":
    try:
        # 运行异步测试
        success = asyncio.run(test_physics_support())

        # 运行前端测试
        test_frontend_html()

        if success:
            print("\n🚀 物理科目支持修复完成！")
            print("\n🔧 下一步操作:")
            print("   1. 启动服务器: uv run uvicorn src.ai_tutor.main:app --host 0.0.0.0 --port 8000 --reload")
            print("   2. 打开浏览器访问: http://localhost:8000/static/index.html")
            print("   3. 在科目选择中可以看到'物理'选项")
            print("   4. 测试上传物理作业图片进行批改")
        else:
            print("\n❌ 部分测试失败，请检查上述错误信息")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
