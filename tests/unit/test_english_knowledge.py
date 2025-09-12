"""
英语知识点提取器的单元测试
"""
import pytest
from unittest.mock import Mock, patch
from src.ai_tutor.services.knowledge.english import EnglishKnowledgeExtractor, ENGLISH_KNOWLEDGE_MAP
from src.ai_tutor.services.llm.base import LLMService


class TestEnglishKnowledgeExtractor:
    """英语知识点提取器测试类"""

    @pytest.fixture
    def mock_llm_service(self):
        """模拟LLM服务"""
        mock_service = Mock(spec=LLMService)
        return mock_service

    @pytest.fixture
    def extractor(self, mock_llm_service):
        """创建英语知识点提取器实例"""
        return EnglishKnowledgeExtractor(llm_service=mock_llm_service)

    def test_get_subject(self, extractor):
        """测试获取学科名称"""
        assert extractor.get_subject() == "english"

    @pytest.mark.asyncio
    async def test_extract_grammar_content(self, extractor, mock_llm_service):
        """测试语法内容的知识点提取"""
        # 模拟AI返回的知识点提取结果
        mock_response = '{"knowledge_points": [{"name": "一般现在时", "category": "语法", "subcategory": "时态", "difficulty_level": "基础", "confidence": 0.9}]}'
        mock_llm_service.generate.return_value = mock_response
        mock_llm_service.safe_json_parse.return_value = {
            "knowledge_points": [{
                "name": "一般现在时",
                "category": "语法", 
                "subcategory": "时态",
                "difficulty_level": "基础",
                "confidence": 0.9
            }]
        }

        # 测试语法内容
        grammar_text = "She goes to school every day. He doesn't like apples."
        result = await extractor.extract(grammar_text)

        # 验证结果
        assert len(result) == 1
        assert result[0]["name"] == "一般现在时"
        assert result[0]["subject"] == "english"
        assert result[0]["difficulty_level"] == "基础"
        assert result[0]["confidence"] == 0.9

        # 验证LLM服务被正确调用
        mock_llm_service.generate.assert_called_once()
        mock_llm_service.safe_json_parse.assert_called_once_with(mock_response)

    @pytest.mark.asyncio
    async def test_extract_reading_comprehension(self, extractor, mock_llm_service):
        """测试阅读理解内容的知识点提取"""
        mock_response = '{"knowledge_points": [{"name": "主旨大意", "category": "阅读理解", "subcategory": "阅读技巧", "difficulty_level": "中等", "confidence": 0.85}]}'
        mock_llm_service.generate.return_value = mock_response
        mock_llm_service.safe_json_parse.return_value = {
            "knowledge_points": [{
                "name": "主旨大意",
                "category": "阅读理解",
                "subcategory": "阅读技巧", 
                "difficulty_level": "中等",
                "confidence": 0.85
            }]
        }

        reading_text = """
        Read the passage and answer the questions.
        The main idea of this article is about environmental protection.
        What is the central theme of the passage?
        """
        result = await extractor.extract(reading_text)

        assert len(result) == 1
        assert result[0]["name"] == "主旨大意"
        assert result[0]["main_category"] == "阅读理解"

    @pytest.mark.asyncio
    async def test_extract_vocabulary_content(self, extractor, mock_llm_service):
        """测试词汇内容的知识点提取"""
        mock_response = '{"knowledge_points": [{"name": "同义词辨析", "category": "词汇", "subcategory": "词汇技巧", "difficulty_level": "中等", "confidence": 0.8}]}'
        mock_llm_service.generate.return_value = mock_response
        mock_llm_service.safe_json_parse.return_value = {
            "knowledge_points": [{
                "name": "同义词辨析",
                "category": "词汇",
                "subcategory": "词汇技巧",
                "difficulty_level": "中等", 
                "confidence": 0.8
            }]
        }

        vocab_text = "Choose the word that best fits the context: big, large, huge, enormous"
        result = await extractor.extract(vocab_text)

        assert len(result) == 1
        assert result[0]["name"] == "同义词辨析"

    @pytest.mark.asyncio
    async def test_extract_writing_content(self, extractor, mock_llm_service):
        """测试写作内容的知识点提取"""
        mock_response = '{"knowledge_points": [{"name": "段落写作", "category": "写作", "subcategory": "写作技巧", "difficulty_level": "中等", "confidence": 0.9}]}'
        mock_llm_service.generate.return_value = mock_response
        mock_llm_service.safe_json_parse.return_value = {
            "knowledge_points": [{
                "name": "段落写作",
                "category": "写作",
                "subcategory": "写作技巧",
                "difficulty_level": "中等",
                "confidence": 0.9
            }]
        }

        writing_text = "Write a paragraph about your favorite hobby. Make sure to include topic sentence, supporting details, and conclusion."
        result = await extractor.extract(writing_text)

        assert len(result) == 1
        assert result[0]["name"] == "段落写作"

    @pytest.mark.asyncio  
    async def test_extract_mixed_content(self, extractor, mock_llm_service):
        """测试中英混合内容的知识点提取"""
        mock_response = '{"knowledge_points": [{"name": "时态", "category": "语法", "subcategory": "时态", "difficulty_level": "基础", "confidence": 0.8}, {"name": "阅读理解", "category": "阅读理解", "subcategory": "阅读技巧", "difficulty_level": "中等", "confidence": 0.7}]}'
        mock_llm_service.generate.return_value = mock_response
        mock_llm_service.safe_json_parse.return_value = {
            "knowledge_points": [
                {
                    "name": "时态",
                    "category": "语法",
                    "subcategory": "时态",
                    "difficulty_level": "基础",
                    "confidence": 0.8
                },
                {
                    "name": "阅读理解", 
                    "category": "阅读理解",
                    "subcategory": "阅读技巧",
                    "difficulty_level": "中等",
                    "confidence": 0.7
                }
            ]
        }

        mixed_text = """
        英语时态练习题：
        1. She _____ (go) to school yesterday.
        2. They _____ (study) English for three years.
        阅读下面短文并回答问题。
        """
        result = await extractor.extract(mixed_text)

        assert len(result) == 2
        subjects = [point["subject"] for point in result]
        assert all(subject == "english" for subject in subjects)

    @pytest.mark.asyncio
    async def test_extract_error_handling(self, extractor, mock_llm_service):
        """测试错误处理"""
        # 模拟LLM服务抛出异常
        mock_llm_service.generate.side_effect = Exception("API调用失败")

        result = await extractor.extract("Some English text")

        # 验证错误处理：返回空列表
        assert result == []

    @pytest.mark.asyncio
    async def test_extract_invalid_json_response(self, extractor, mock_llm_service):
        """测试无效JSON响应的处理"""
        mock_llm_service.generate.return_value = "invalid json response"
        mock_llm_service.safe_json_parse.return_value = {}  # 空字典表示解析失败

        result = await extractor.extract("English test text")

        assert result == []

    def test_build_prompt_contains_knowledge_points(self, extractor):
        """测试提示词构建包含知识点列表"""
        text = "Test English content"
        prompt = extractor._build_prompt(text)

        # 验证提示词包含知识点
        assert "一般现在时" in prompt
        assert "阅读理解" in prompt
        assert "语法" in prompt
        assert "词汇" in prompt
        assert text in prompt

    def test_format_response_adds_subject(self, extractor):
        """测试响应格式化添加学科标识"""
        raw_response = {
            "knowledge_points": [
                {"name": "一般现在时", "category": "语法"},
                {"name": "词汇运用", "category": "词汇"}
            ]
        }

        result = extractor._format_response(raw_response)

        # 验证每个知识点都添加了学科标识
        for point in result:
            assert point["subject"] == "english"

    def test_format_response_sets_defaults(self, extractor):
        """测试响应格式化设置默认值"""
        raw_response = {
            "knowledge_points": [
                {"name": "语法点", "category": "语法"}
            ]
        }

        result = extractor._format_response(raw_response)

        # 验证设置了默认值
        assert result[0]["difficulty_level"] == "中等"
        assert result[0]["confidence"] == 0.8

    def test_get_supported_knowledge_points(self, extractor):
        """测试获取支持的知识点结构"""
        knowledge_points = extractor.get_supported_knowledge_points()
        
        assert knowledge_points == ENGLISH_KNOWLEDGE_MAP
        assert "语法" in knowledge_points
        assert "词汇" in knowledge_points
        assert "阅读理解" in knowledge_points

    def test_get_difficulty_assessment_basic(self, extractor):
        """测试基础难度评估"""
        knowledge_points = [
            {"difficulty_level": "基础", "confidence": 0.9},
            {"difficulty_level": "基础", "confidence": 0.8}
        ]
        
        difficulty = extractor.get_difficulty_assessment(knowledge_points)
        assert difficulty == "基础"

    def test_get_difficulty_assessment_intermediate(self, extractor):
        """测试中等难度评估"""
        knowledge_points = [
            {"difficulty_level": "基础", "confidence": 0.9},
            {"difficulty_level": "中等", "confidence": 0.8},
            {"difficulty_level": "中等", "confidence": 0.7}
        ]
        
        difficulty = extractor.get_difficulty_assessment(knowledge_points)
        assert difficulty == "中等"

    def test_get_difficulty_assessment_advanced(self, extractor):
        """测试高级难度评估"""
        knowledge_points = [
            {"difficulty_level": "高级", "confidence": 0.9},
            {"difficulty_level": "高级", "confidence": 0.8}
        ]
        
        difficulty = extractor.get_difficulty_assessment(knowledge_points)
        assert difficulty == "高级"

    def test_get_difficulty_assessment_empty(self, extractor):
        """测试空知识点列表的难度评估"""
        difficulty = extractor.get_difficulty_assessment([])
        assert difficulty == "基础"

    def test_category_map_completeness(self, extractor):
        """测试分类映射的完整性"""
        category_map = extractor._get_category_map()
        
        # 验证所有知识点都在映射中
        for main_category, subcategories in ENGLISH_KNOWLEDGE_MAP.items():
            for subcategory, points in subcategories.items():
                for point in points:
                    assert point in category_map
                    assert category_map[point]["main_category"] == main_category
                    assert category_map[point]["subcategory"] == subcategory

    @pytest.mark.asyncio
    async def test_confidence_scores(self, extractor, mock_llm_service):
        """测试置信度分数的处理"""
        mock_response = '{"knowledge_points": [{"name": "语法点", "category": "语法", "confidence": 0.95}]}'
        mock_llm_service.generate.return_value = mock_response
        mock_llm_service.safe_json_parse.return_value = {
            "knowledge_points": [{
                "name": "语法点",
                "category": "语法",
                "confidence": 0.95
            }]
        }

        result = await extractor.extract("Test text")
        
        assert len(result) == 1
        assert result[0]["confidence"] == 0.95
