from typing import List, Dict, Any

from ai_tutor.core.logger import get_logger
from .extractor import KnowledgeExtractor, register_extractor

logger = get_logger(__name__)

# Placeholder for physics knowledge points.
PHYSICS_KNOWLEDGE_MAP = {
    "力学": ["牛顿运动定律", "动量守恒", "机械能守恒"],
    "电磁学": ["电场", "磁场", "电磁感应"],
    "热学": ["热力学第一定律", "理想气体状态方程"],
    "光学": ["几何光学", "物理光学"],
}


@register_extractor
class PhysicsKnowledgeExtractor(KnowledgeExtractor):
    """
    Knowledge point extractor for the 'physics' subject.
    """

    @classmethod
    def get_subject(cls) -> str:
        return "physics"

    async def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts physics knowledge points from the given text using an LLM.

        Args:
            text: The text content of the physics question.

        Returns:
            A list of identified knowledge points.
        """
        logger.info(f"Starting physics knowledge point extraction for text: {text[:100]}...")

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
        for category, points in PHYSICS_KNOWLEDGE_MAP.items():
            knowledge_list.extend(points)

        prompt = f"""
        你是一位专业的物理老师，你的任务是从给定的物理题目中识别出所有相关的知识点。

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
