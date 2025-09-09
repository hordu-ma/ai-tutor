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


GRADE_PROMPT_TEMPLATE = """
你是一个严格且有耐心的中学{subject_cn}老师，请对以下作业进行批改。
要求：
1) 对每道题给出：是否正确(is_correct: true/false)、得分(score)、满分(max_score)、正确答案(correct_answer)、错误分析(error_analysis)、必要时给出分步讲解(solution_steps)
2) 提取涉及的知识点(knowledge_points: ["..."]), 并估计每题难度(1-5)和本题掌握程度(0.0-1.0)
3) 给出总体得分(overall_score)与总体建议(overall_suggestions)
4) 严格输出JSON，字段：
{{
  "questions": [
    {{
      "question_number": 1,
      "question_text": "...",
      "student_answer": "...",
      "is_correct": true,
      "score": 5,
      "max_score": 5,
      "correct_answer": "...",
      "error_analysis": "...",
      "solution_steps": ["...", "..."],
      "knowledge_points": ["..."],
      "difficulty_level": 3
    }}
  ],
  "overall_score": 87.5,
  "overall_suggestions": "..."
}}

科目：{subject_cn}
作业OCR文本如下：
---
{ocr_text}
---
请直接返回JSON，不要包含任何额外解释。
"""


SUBJECT_CN_MAP = {
    "math": "数学",
    "english": "英语",
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

        # 2) 组织Prompt并调用LLM
        subject_cn = SUBJECT_CN_MAP.get(subject.lower(), subject)
        prompt = GRADE_PROMPT_TEMPLATE.format(subject_cn=subject_cn, ocr_text=ocr_text)
        llm_response = await self.llm.generate(prompt, max_tokens=1800, temperature=0.2)

        # 3) 尝试解析为JSON
        import json
        import re

        parsed: Dict[str, Any]
        try:
            parsed = json.loads(llm_response)
        except Exception as e:
            # 容错：若返回非严格JSON，尽力清洗
            self.log_warning("大模型返回非严格JSON，尝试清洗", original_error=str(e))
            
            # 多种清洗策略
            cleaned = llm_response.strip()
            
            # 移除代码块标记
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            # 移除前后空格和特殊字符
            cleaned = cleaned.strip().strip('` "\'')
            
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
            
            try:
                parsed = json.loads(cleaned)
            except Exception as e2:
                # 最后的容错机制：返回默认结构
                self.log_error("无法解析AI返回的JSON", 
                             original_response=llm_response[:200], 
                             cleaned_response=cleaned[:200], 
                             error=str(e2))
                parsed = {
                    "questions": [],
                    "overall_score": 0,
                    "overall_suggestions": "解析AI回答失败，请检查图片清晰度或重新提交。"
                }

        elapsed = time.time() - t0
        result = {
            "provider": self.provider,
            "ocr_text": ocr_text,
            "correction": parsed,
            "processing_time": round(elapsed, 2),
        }
        self.log_event("批改完成", provider=self.provider, processing_time=elapsed)
        return result

