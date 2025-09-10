"""
作业批改核心服务
"""
import time
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO

from ...core.logger import LoggerMixin
from ..ocr import get_ocr_service
from ..llm import get_llm_service
from ..llm.prompts import MathGradingPrompts, PhysicsGradingPrompts, PromptVersion


# 科目提示词映射
SUBJECT_PROMPTS_MAP = {
    "math": MathGradingPrompts(),
    "physics": PhysicsGradingPrompts(),
}

SUBJECT_CN_MAP = {
    "math": "数学",
    "english": "英语",
    "physics": "物理",
}


class HomeworkService(LoggerMixin):
    """将 OCR 与 LLM 串联的批改服务"""

    def __init__(self, provider: str = "qwen"):
        self.ocr = get_ocr_service()
        self.llm = get_llm_service(provider)
        self.provider = provider

    async def grade_homework(
        self,
        image: Image.Image,
        subject: str = "math",
        student_answer_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """端到端批改流程：OCR -> LLM评阅 -> 结构化结果"""
        t0 = time.time()
        # 1) OCR
        ocr_text = await self.ocr.extract_text(image)

        # 2) 获取提示词模板并组织Prompt
        subject_lower = subject.lower()
        if subject_lower in SUBJECT_PROMPTS_MAP:
            # 使用专门的科目提示词
            prompt_provider = SUBJECT_PROMPTS_MAP[subject_lower]
            prompt_template = prompt_provider.get_grading_prompt(PromptVersion.V1_0)
            format_example = prompt_provider.get_format_example() if hasattr(prompt_provider, 'get_format_example') else ""
            prompt = prompt_template.format(ocr_text=ocr_text, format_example=format_example)
        else:
            # 回退到通用提示词
            subject_cn = SUBJECT_CN_MAP.get(subject_lower, subject)
            prompt = f"""你是一个严格且有耐心的中学{subject_cn}老师，请对以下作业进行批改。
要求：严格输出JSON格式的批改结果。
作业OCR文本如下：
---
{ocr_text}
---
请直接返回JSON。"""
        
        llm_response = await self.llm.generate(prompt, max_tokens=1800, temperature=0.2)

        # 3) 使用增强的JSON解析方法
        parsed: Dict[str, Any] = self.llm.safe_json_parse(
            llm_response, 
            fallback_parser=self._create_homework_fallback_parser(ocr_text)
        )

        elapsed = time.time() - t0
        result = {
            "provider": self.provider,
            "ocr_text": ocr_text,
            "correction": parsed,
            "processing_time": round(elapsed, 2),
        }
        self.log_event("批改完成", provider=self.provider, processing_time=elapsed)
        return result
    
    def _create_homework_fallback_parser(self, ocr_text: str) -> callable:
        """创建作业批改的降级解析器"""
        def homework_fallback_parser(text: str) -> Dict[str, Any]:
            """作业批改的特定降级解析器"""
            import re
            
            result = {
                "questions": [],
                "overall_score": 0,
                "total_score": 0,
                "accuracy_rate": 0.0,
                "overall_suggestions": "解析AI回答失败，但尝试提取了部分信息。",
                "weak_knowledge_points": [],
                "study_recommendations": [],
                "parsing_fallback": True
            }
            
            # 尝试提取分数信息
            score_patterns = [
                r'(?:总分|得分|总体得分|overall_score)[:\s]*([0-9.]+)',
                r'score[:\s]*([0-9.]+)',
                r'(分数)[:\s]*([0-9.]+)',
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        score = float(match.group(1) if len(match.groups()) == 1 else match.group(2))
                        result["overall_score"] = score
                        break
                    except ValueError:
                        continue
            
            # 尝试提取题目信息
            question_patterns = [
                r'(题目|question)\s*([0-9]+)',
                r'([0-9]+)\s*[\.\)]\s*(.{1,100})',
            ]
            
            questions_found = []
            for pattern in question_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(questions_found) < 10:  # 限制数量
                        question_data = {
                            "question_number": len(questions_found) + 1,
                            "question_text": match.group(0)[:100],  # 截取前100字符
                            "student_answer": "未能识别",
                            "is_correct": None,
                            "score": 0,
                            "max_score": 10,
                            "correct_answer": "未能解析",
                            "error_analysis": "解析失败",
                            "solution_steps": [],
                            "knowledge_points": [],
                            "difficulty_level": 3
                        }
                        questions_found.append(question_data)
            
            result["questions"] = questions_found
            
            # 尝试提取建议
            suggestion_patterns = [
                r'(?:建议|总结|suggestion|summary)[:\s]*(.{20,300})',
                r'(?:需要改进|学习建议)[:\s]*(.{20,200})',
            ]
            
            for pattern in suggestion_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    suggestion = match.group(1).strip()
                    if len(suggestion) > 15:  # 确保有意义
                        result["overall_suggestions"] = suggestion[:300]  # 限制长度
                        break
            
            return result
        
        return homework_fallback_parser

