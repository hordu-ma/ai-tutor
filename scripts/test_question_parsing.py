#!/usr/bin/env python3
"""
题目解析功能测试脚本
"""
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai_tutor.services.parsing import QuestionParser, TextAnalyzer
from src.ai_tutor.core.logger import get_logger

logger = get_logger(__name__)


def test_question_parser():
    """测试题目解析器"""
    logger.info("🔍 测试题目解析器...")
    
    parser = QuestionParser()
    
    # 测试用例1：标准数学题
    test_text_1 = """
    数学作业
    
    1. 计算 3 + 5 = ?
    学生答：8
    
    2. 求解方程 2x + 3 = 7
    学生答：x = 2
    
    3. 判断：√9 = 3 是否正确？
    学生答：正确
    """
    
    parsed_questions = parser.parse_questions(test_text_1)
    logger.info("测试用例1解析结果", questions_count=len(parsed_questions))
    
    for i, q in enumerate(parsed_questions, 1):
        logger.info(f"题目 {i}:", 
                   number=q.question_number,
                   type=q.question_type.value,
                   text=q.question_text[:50] + "...",
                   student_answer=q.student_answer,
                   confidence=q.confidence)
    
    # 测试用例2：选择题
    test_text_2 = """
    （1）下列哪个是正确的？
    A. 2+2=5  B. 3×4=12  C. 5÷2=3  D. 6-1=4
    学生答案：B
    
    （2）圆的面积公式是？
    A. πr  B. πr²  C. 2πr  D. πd
    答案：B
    """
    
    parsed_questions_2 = parser.parse_questions(test_text_2)
    logger.info("测试用例2解析结果", questions_count=len(parsed_questions_2))
    
    for i, q in enumerate(parsed_questions_2, 1):
        logger.info(f"选择题 {i}:", 
                   number=q.question_number,
                   type=q.question_type.value,
                   answer=q.student_answer)
    
    return len(parsed_questions) > 0 and len(parsed_questions_2) > 0


def test_text_analyzer():
    """测试文本分析器"""
    logger.info("📊 测试文本分析器...")
    
    analyzer = TextAnalyzer()
    
    test_text = """
    1. 计算 25 + 37 = ?
    学生答：62
    
    2. 解方程 3x - 6 = 15
    学生答：x = 7
    
    3. 求圆的周长，已知半径 r = 5cm
    学生答：C = 2πr = 10π ≈ 31.4cm
    """
    
    analysis = analyzer.extract_key_features(test_text)
    
    logger.info("文本分析结果:", 
               length=analysis["length"],
               complexity=analysis["complexity_score"],
               grade_level=analysis["grade_level_estimate"],
               has_math=analysis["mathematical_content"]["has_arithmetic"],
               subject_indicators=analysis["subject_indicators"],
               question_patterns=analysis["question_patterns"])
    
    return analysis["complexity_score"] > 0


async def test_integration():
    """测试解析功能集成"""
    logger.info("🔗 测试解析功能集成...")
    
    from src.ai_tutor.services.student import HomeworkService
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建包含多种题型的测试图片
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    test_content = [
        "数学练习题",
        "",
        "1. 计算题：15 + 28 = ?",
        "   学生答案：43",
        "",
        "2. 选择题：下列哪个是偶数？",
        "   A. 3   B. 7   C. 8   D. 9",
        "   学生答案：C",
        "",
        "3. 填空题：√16 = ___",
        "   学生答案：4",
        "",
        "4. 应用题：小明买了3支笔，每支2元，",
        "   一共花了多少钱？",
        "   学生答案：6元"
    ]
    
    y_offset = 30
    for line in test_content:
        draw.text((50, y_offset), line, fill='black', font=font)
        y_offset += 35
    
    # 使用HomeworkService进行完整测试
    service = HomeworkService("qwen")
    
    try:
        result = await service.grade_homework(img, "math")
        
        logger.info("集成测试结果:", 
                   parsed_questions_count=len(result.get("parsed_questions", [])),
                   text_analysis_available=bool(result.get("text_analysis")),
                   quality_score=result.get("text_analysis", {}).get("quality_score", 0),
                   complexity_score=result.get("text_analysis", {}).get("complexity_score", 0))
        
        if result.get("parsed_questions"):
            logger.info("解析的题目类型:", 
                       types=[q["question_type"] for q in result["parsed_questions"]])
        
        return len(result.get("parsed_questions", [])) > 0
        
    except Exception as e:
        logger.error("集成测试失败", error=str(e))
        return False


async def main():
    """主测试函数"""
    logger.info("🚀 开始题目解析功能测试...")
    
    test_results = {
        "question_parser": False,
        "text_analyzer": False,
        "integration": False
    }
    
    # 1. 测试题目解析器
    test_results["question_parser"] = test_question_parser()
    
    # 2. 测试文本分析器
    test_results["text_analyzer"] = test_text_analyzer()
    
    # 3. 测试集成功能
    test_results["integration"] = await test_integration()
    
    # 输出测试总结
    logger.info("=" * 50)
    logger.info("📊 题目解析测试结果总结:")
    
    for test_name, passed in test_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
    
    all_passed = all(test_results.values())
    if all_passed:
        logger.info("🎉 所有题目解析功能测试通过！")
    else:
        logger.warning("⚠️ 部分测试失败，需要进一步优化")
    
    return all_passed


if __name__ == "__main__":
    import asyncio
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error("测试脚本异常", error=str(e))
        sys.exit(1)
