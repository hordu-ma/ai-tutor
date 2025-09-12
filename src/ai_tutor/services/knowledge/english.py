from typing import List, Dict, Any

from ai_tutor.core.logger import get_logger
from .extractor import KnowledgeExtractor, register_extractor

logger = get_logger(__name__)

# 英语知识点结构化分类
ENGLISH_KNOWLEDGE_MAP = {
    "语法": {
        "时态": ["一般现在时", "一般过去时", "一般将来时", "现在进行时", "过去进行时", "现在完成时", "过去完成时"],
        "句型结构": ["陈述句", "疑问句", "祈使句", "感叹句", "定语从句", "状语从句", "宾语从句", "主语从句"],
        "词性语法": ["名词", "代词", "动词", "形容词", "副词", "介词", "连词", "冠词"],
        "语态": ["主动语态", "被动语态"],
        "虚拟语气": ["虚拟条件句", "虚拟语气在宾语从句中的应用"],
        "比较等级": ["原级", "比较级", "最高级"]
    },
    "词汇": {
        "基础词汇": ["日常生活", "学校教育", "家庭成员", "颜色数字", "食物饮料"],
        "中级词汇": ["工作职业", "交通出行", "健康医疗", "购物消费", "娱乐休闲"],
        "高级词汇": ["科技环保", "社会文化", "经济政治", "学术词汇", "抽象概念"],
        "词汇技巧": ["词根词缀", "同义词辨析", "反义词", "习语搭配", "短语动词"]
    },
    "阅读理解": {
        "阅读技巧": ["略读", "扫读", "细读", "推理判断", "主旨大意"],
        "文章类型": ["记叙文", "说明文", "议论文", "应用文", "新闻报道"],
        "语篇理解": ["段落结构", "逻辑关系", "文章脉络", "作者态度", "隐含意义"]
    },
    "写作": {
        "写作技巧": ["段落写作", "句式变化", "连接词使用", "论证方法", "修辞手法"],
        "文体写作": ["记叙文写作", "说明文写作", "议论文写作", "书信写作", "日记写作"],
        "写作规范": ["标点符号", "大小写", "段落格式", "词汇选择", "语法准确性"]
    },
    "听说交际": {
        "口语表达": ["日常对话", "情景交际", "话题讨论", "演讲表达", "辩论技巧"],
        "听力技巧": ["关键词捕捉", "语音识别", "语调理解", "对话理解", "独白理解"]
    }
}


@register_extractor
class EnglishKnowledgeExtractor(KnowledgeExtractor):
    """
    英语学科知识点提取器。

    支持对英语学习内容进行知识点识别和分类，包括：
    - 语法规则和结构
    - 词汇分类和难度
    - 阅读理解技巧
    - 写作技巧和文体
    - 听说交际能力
    """

    @classmethod
    def get_subject(cls) -> str:
        return "english"

    async def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        从给定的英语学习文本中提取知识点。

        Args:
            text: 英语题目或学习材料的文本内容

        Returns:
            识别出的知识点列表，包含名称、分类、类型等信息
        """
        logger.info(f"开始英语知识点提取，文本长度: {len(text)}")

        prompt = self._build_prompt(text)

        try:
            response_text = await self.llm_service.generate(prompt)
            parsed_json = self.llm_service.safe_json_parse(response_text)
            knowledge_points = self._format_response(parsed_json)

            logger.info(f"成功提取到 {len(knowledge_points)} 个英语知识点")
            return knowledge_points
        except Exception as e:
            logger.error(
                "英语知识点提取失败",
                error=str(e),
                text=text[:200]
            )
            return []

    def _build_prompt(self, text: str) -> str:
        """构建用于LLM的知识点提取提示词"""

        # 创建扁平化的知识点列表
        knowledge_list = []
        category_map = {}

        for main_category, subcategories in ENGLISH_KNOWLEDGE_MAP.items():
            for subcategory, points in subcategories.items():
                for point in points:
                    knowledge_list.append(point)
                    category_map[point] = {
                        "main_category": main_category,
                        "subcategory": subcategory
                    }

        prompt = f"""
        你是一位专业的英语教师，具有丰富的英语教学经验。你的任务是从给定的英语学习内容中识别出所有相关的知识点。

        请仔细分析文本内容，从以下知识点中进行选择。如果内容涉及多个知识点，请全部列出：

        可选知识点列表:
        {', '.join(knowledge_list)}

        分析要求:
        1. 准确识别语法结构、词汇难度、阅读技巧等
        2. 注意识别中英混合内容的特点
        3. 考虑题目类型对知识点的影响
        4. 评估内容的难度级别

        请严格按照以下JSON格式返回结果，不要添加任何额外的解释或说明：
        {{
          "knowledge_points": [
            {{
              "name": "知识点名称",
              "category": "主要分类",
              "subcategory": "子分类",
              "difficulty_level": "基础/中等/高级",
              "confidence": 0.95
            }}
          ]
        }}

        待分析的英语内容：
        ---
        {text}
        ---
        """
        return prompt.strip()

    def _format_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化LLM响应为标准输出结构"""
        points = response.get("knowledge_points", [])

        for point in points:
            # 添加学科标识
            point["subject"] = self.get_subject()

            # 设置默认值
            if "difficulty_level" not in point:
                point["difficulty_level"] = "中等"
            if "confidence" not in point:
                point["confidence"] = 0.8

            # 验证并补充分类信息
            point_name = point.get("name", "")
            if point_name in self._get_category_map():
                category_info = self._get_category_map()[point_name]
                point["main_category"] = category_info["main_category"]
                point["subcategory"] = category_info["subcategory"]

        return points

    def _get_category_map(self) -> Dict[str, Dict[str, str]]:
        """获取知识点到分类的映射"""
        category_map = {}
        for main_category, subcategories in ENGLISH_KNOWLEDGE_MAP.items():
            for subcategory, points in subcategories.items():
                for point in points:
                    category_map[point] = {
                        "main_category": main_category,
                        "subcategory": subcategory
                    }
        return category_map

    def get_supported_knowledge_points(self) -> Dict[str, Any]:
        """获取支持的知识点结构"""
        return ENGLISH_KNOWLEDGE_MAP

    def get_difficulty_assessment(self, knowledge_points: List[Dict[str, Any]]) -> str:
        """
        基于识别的知识点评估整体难度

        Args:
            knowledge_points: 识别出的知识点列表

        Returns:
            整体难度评估: 基础/中等/高级
        """
        if not knowledge_points:
            return "基础"

        difficulty_scores = []
        for point in knowledge_points:
            difficulty = point.get("difficulty_level", "中等")
            if difficulty == "基础":
                difficulty_scores.append(1)
            elif difficulty == "中等":
                difficulty_scores.append(2)
            else:  # 高级
                difficulty_scores.append(3)

        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)

        if avg_difficulty <= 1.3:
            return "基础"
        elif avg_difficulty <= 2.3:
            return "中等"
        else:
            return "高级"
