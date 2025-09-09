#!/usr/bin/env python3
"""
端到端测试脚本 - 测试完整的作业批改流程
"""
import sys
import os
import asyncio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai_tutor.services.student import HomeworkService
from src.ai_tutor.services.ocr import get_ocr_service
from src.ai_tutor.services.llm import get_llm_service
from src.ai_tutor.core.logger import get_logger

logger = get_logger(__name__)


def create_test_image() -> Image.Image:
    """创建一个测试数学题图片"""
    # 创建白色背景
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，否则使用默认字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 添加数学题文本
    text_lines = [
        "数学作业 - 第1题",
        "",
        "计算下列各题：",
        "1. 3 + 5 = ?",
        "   学生答案：8",
        "",
        "2. 12 ÷ 3 = ?", 
        "   学生答案：4",
        "",
        "3. 7 × 8 = ?",
        "   学生答案：56"
    ]
    
    y_offset = 30
    for line in text_lines:
        if line.strip():
            if line.startswith("数学作业"):
                draw.text((50, y_offset), line, fill='black', font=font)
            elif line.startswith(("1.", "2.", "3.")):
                draw.text((80, y_offset), line, fill='blue', font=font)
            elif "学生答案" in line:
                draw.text((120, y_offset), line, fill='red', font=small_font)
            else:
                draw.text((80, y_offset), line, fill='black', font=small_font)
        y_offset += 30
    
    return img


async def test_ocr_service():
    """测试OCR服务"""
    logger.info("🔍 测试OCR服务...")
    
    try:
        ocr_service = get_ocr_service()
        test_image = create_test_image()
        
        text = await ocr_service.extract_text(test_image)
        
        logger.info("OCR识别结果:", text=text[:100] + "..." if len(text) > 100 else text)
        
        # 验证是否识别到关键内容
        if any(keyword in text for keyword in ["3", "5", "8", "数学", "计算"]):
            logger.info("✅ OCR服务测试通过")
            return True
        else:
            logger.warning("⚠️ OCR未识别到预期内容")
            return False
            
    except Exception as e:
        logger.error("❌ OCR服务测试失败", error=str(e))
        return False


async def test_ai_service():
    """测试AI服务"""
    logger.info("🤖 测试AI服务...")
    
    try:
        ai_service = get_llm_service("qwen")
        
        # 简单测试
        response = await ai_service.generate("请说'Hello AI'", max_tokens=50)
        
        logger.info("AI响应:", response=response)
        
        if response and len(response.strip()) > 0:
            logger.info("✅ AI服务测试通过")
            return True
        else:
            logger.warning("⚠️ AI服务响应为空")
            return False
            
    except Exception as e:
        logger.error("❌ AI服务测试失败", error=str(e))
        return False


async def test_homework_service():
    """测试完整的作业批改流程"""
    logger.info("📝 测试作业批改服务...")
    
    try:
        homework_service = HomeworkService("qwen")
        test_image = create_test_image()
        
        logger.info("开始批改测试作业...")
        result = await homework_service.grade_homework(
            image=test_image,
            subject="math"
        )
        
        logger.info("批改完成", processing_time=result["processing_time"])
        
        # 验证结果结构
        if (
            "ocr_text" in result and 
            "correction" in result and 
            "processing_time" in result
        ):
            logger.info("✅ 作业批改服务测试通过")
            logger.info("批改结果结构完整")
            
            # 显示部分结果
            if "overall_score" in result["correction"]:
                logger.info("总体得分:", score=result["correction"]["overall_score"])
            
            if "questions" in result["correction"]:
                logger.info("识别题目数量:", count=len(result["correction"]["questions"]))
            
            return True
        else:
            logger.warning("⚠️ 批改结果结构不完整")
            return False
            
    except Exception as e:
        logger.error("❌ 作业批改服务测试失败", error=str(e))
        return False


async def main():
    """主测试函数"""
    logger.info("🚀 开始端到端测试...")
    
    test_results = {
        "ocr_service": False,
        "ai_service": False,
        "homework_service": False
    }
    
    # 1. 测试OCR服务
    test_results["ocr_service"] = await test_ocr_service()
    
    # 2. 测试AI服务
    test_results["ai_service"] = await test_ai_service()
    
    # 3. 测试完整批改流程
    if test_results["ocr_service"] and test_results["ai_service"]:
        test_results["homework_service"] = await test_homework_service()
    else:
        logger.warning("⚠️ 由于OCR或AI服务测试失败，跳过完整流程测试")
    
    # 输出测试总结
    logger.info("=" * 50)
    logger.info("📊 测试结果总结:")
    
    for service, passed in test_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"  {service}: {status}")
    
    all_passed = all(test_results.values())
    if all_passed:
        logger.info("🎉 所有测试通过！系统MVP功能完整可用！")
    else:
        logger.warning("⚠️ 部分测试失败，请检查配置和网络连接")
    
    return all_passed


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error("测试脚本异常", error=str(e))
        sys.exit(1)
