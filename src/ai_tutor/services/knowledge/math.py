from typing import List, Dict, Any

from ai_tutor.core.logger import get_logger
from .extractor import KnowledgeExtractor, register_extractor

logger = get_logger(__name__)

# This is a placeholder for the math knowledge point structure.
# In a real scenario, this might come from a database or a more complex config file.
MATH_KNOWLEDGE_MAP = {
    "初中数学": {
        "代数": ["一元一次方程", "函数", "不等式"],
        "几何": ["三角形", "圆", "相似与全等"],
    },
    "高中数学": {
        "集合与函数": ["集合", "常用逻辑用语", "函数概念与基本初等函数"],
        "立体几何": ["空间几何体", "点、直线、平面之间的位置关系"],
        "解析几何": ["直线与方程", "圆与方程", "圆锥曲线与方程"],
        "算法初步": ["算法初步"],
        "统计与概率": ["统计", "概率", "随机变量及其分布"],
        "导数及其应用": ["导数", "导数应用"],
    },
}


@register_extractor
class MathKnowledgeExtractor(KnowledgeExtractor):
    """
    Knowledge point extractor for the 'math' subject.
    """

    @classmethod
    def get_subject(cls) -> str:
        return "math"

    async def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts math knowledge points from the given text using an LLM.

        Args:
            text: The text content of the math question.

        Returns:
            A list of identified knowledge points.
        """
        logger.info(f"Starting math knowledge point extraction for text: {text[:100]}...")

        prompt = self._build_prompt(text)

        try:
            response_text = await self.llm_service.generate(prompt)
            parsed_json = self.llm_service.safe_json_parse(response_text)
            knowledge_points = self._format_response(parsed_json)

            logger.info(f"Successfully extracted {len(knowledge_points)} knowledge points.")
            return knowledge_points
        except Exception as e:
            logger.error(
                "Failed to extract knowledge points from LLM",
                error=str(e),
                text=text[:200]
            )
            return []

    def _build_prompt(self, text: str) -> str:
        """Builds the prompt for the LLM to extract knowledge points."""

        knowledge_list = []
        for grade, subjects in MATH_KNOWLEDGE_MAP.items():
            for subject, points in subjects.items():
                knowledge_list.extend(points)

        prompt = f"""
        你是一个专业的数学老师，你的任务是从给定的数学题目中识别出所有相关的知识点。

        请从以下知识点列表中进行选择。如果题目中包含多个知识点，请全部列出。
        知识点列表: {', '.join(knowledge_list)}

        请严格按照以下JSON格式返回结果，不要添加任何额外的解释或说明。
        {{
          "knowledge_points": [
            {{"name": "知识点名称", "category": "知识点分类"}},
            ...
          ]
        }}

        题目内容如下:
        ---
        {text}
        ---
        """
        return prompt.strip()

    def _format_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Formats the LLM response into the desired output structure."""
        points = response.get("knowledge_points", [])
        for point in points:
            point["subject"] = self.get_subject()
        return points
