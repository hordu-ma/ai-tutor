"""
英语学科完整批改流程的集成测试
"""
import pytest
from unittest.mock import Mock, patch
from src.ai_tutor.services.knowledge.english import EnglishKnowledgeExtractor
from src.ai_tutor.services.parsing.subject_router import SubjectRouter, Subject
from src.ai_tutor.services.llm.prompts.english_grading import english_prompts
from src.ai_tutor.schemas.english_schemas import (
    EnglishQuestion, EnglishQuestionType, EnglishCategory, VocabularyLevel,
    GrammarPointType, EnglishGradingResult
)


class TestEnglishGradingFlow:
    """英语批改流程集成测试"""

    @pytest.fixture
    def mock_llm_service(self):
        """模拟LLM服务"""
        mock_service = Mock()
        return mock_service

    @pytest.fixture
    def subject_router(self):
        """科目路由器"""
        return SubjectRouter()

    @pytest.fixture
    def knowledge_extractor(self, mock_llm_service):
        """英语知识点提取器"""
        return EnglishKnowledgeExtractor(llm_service=mock_llm_service)

    def test_english_content_detection_flow(self, subject_router):
        """测试英语内容检测流程"""
        # 测试多种英语内容类型
        test_cases = [
            {
                'text': 'Choose the correct answer: I _____ (go) to school every day.',
                'expected_subject': Subject.ENGLISH,
                'description': '英语语法填空题'
            },
            {
                'text': '''Reading Comprehension
                The weather is beautiful today. The sun is shining and birds are singing.
                Question: What is the weather like?''',
                'expected_subject': Subject.ENGLISH,
                'description': '英语阅读理解题'
            },
            {
                'text': '''英语词汇练习：
                1. big = _____ (large, small, red, fast)
                2. happy的反义词是什么？''',
                'expected_subject': Subject.ENGLISH,
                'description': '中英混合词汇练习'
            }
        ]

        for case in test_cases:
            result = subject_router.detect_subject(case['text'])
            assert result.primary_subject == case['expected_subject'], \
                f"Failed for {case['description']}: expected {case['expected_subject']}, got {result.primary_subject}"

    @pytest.mark.asyncio
    async def test_knowledge_extraction_flow(self, knowledge_extractor, mock_llm_service):
        """测试知识点提取流程"""
        # 模拟不同类型的英语内容
        test_cases = [
            {
                'text': 'She goes to school every day. Does she like English?',
                'mock_response': {
                    "knowledge_points": [
                        {
                            "name": "一般现在时",
                            "category": "语法",
                            "subcategory": "时态",
                            "difficulty_level": "基础",
                            "confidence": 0.9
                        }
                    ]
                },
                'expected_points': ["一般现在时"]
            },
            {
                'text': '''Read the passage and choose the best title.
                Environmental protection is everyone's responsibility.''',
                'mock_response': {
                    "knowledge_points": [
                        {
                            "name": "阅读理解",
                            "category": "阅读理解",
                            "subcategory": "阅读技巧",
                            "difficulty_level": "中等",
                            "confidence": 0.85
                        },
                        {
                            "name": "主旨大意",
                            "category": "阅读理解",
                            "subcategory": "阅读技巧",
                            "difficulty_level": "中等",
                            "confidence": 0.8
                        }
                    ]
                },
                'expected_points': ["阅读理解", "主旨大意"]
            }
        ]

        for case in test_cases:
            # 设置模拟响应
            # 设置异步方法的模拟返回值
            async def mock_generate(prompt):
                return str(case['mock_response'])
            mock_llm_service.generate = mock_generate
            mock_llm_service.safe_json_parse.return_value = case['mock_response']

            # 执行知识点提取
            result = await knowledge_extractor.extract(case['text'])

            # 验证结果
            assert len(result) == len(case['expected_points'])
            extracted_names = [point['name'] for point in result]
            for expected_point in case['expected_points']:
                assert expected_point in extracted_names

    def test_prompt_generation_flow(self):
        """测试提示词生成流程"""
        from src.ai_tutor.services.llm.prompts.base import PromptVersion

        # 测试不同版本的英语批改提示词
        versions = [PromptVersion.V1_0, PromptVersion.V1_1, PromptVersion.V2_0]

        for version in versions:
            prompt_template = english_prompts.get_grading_prompt(version)

            # 验证提示词结构
            assert prompt_template.template is not None
            assert prompt_template.version == version
            assert 'ocr_text' in prompt_template.parameters
            assert '英语' in prompt_template.description or 'English' in prompt_template.description

            # 验证提示词内容包含关键要素
            if version == PromptVersion.V1_0:
                assert '语法准确性' in prompt_template.template
                assert '词汇使用' in prompt_template.template
            elif version == PromptVersion.V1_1:
                assert '语言准确性' in prompt_template.template
                assert '交际有效性' in prompt_template.template
            elif version == PromptVersion.V2_0:
                assert '英语核心素养' in prompt_template.template
                assert '个性化指导' in prompt_template.template

    def test_schema_validation_flow(self):
        """测试数据模型验证流程"""
        # 测试英语题目模型
        question_data = {
            'text': 'Choose the correct answer: I _____ to school yesterday.',
            'question_type': EnglishQuestionType.FILL_IN_BLANK,
            'category': EnglishCategory.GRAMMAR,
            'grammar_points': [GrammarPointType.SIMPLE_PAST],
            'vocabulary_level': VocabularyLevel.BASIC,
            'difficulty_level': 2,
            'answer': 'went',
            'explanation': '这里需要用一般过去时，因为有yesterday这个过去时间标志词。'
        }

        # 验证可以成功创建模型
        question = EnglishQuestion(**question_data)
        assert question.text == question_data['text']
        assert question.question_type == EnglishQuestionType.FILL_IN_BLANK
        assert question.category == EnglishCategory.GRAMMAR
        assert GrammarPointType.SIMPLE_PAST in question.grammar_points

    @pytest.mark.asyncio
    async def test_error_handling_flow(self, knowledge_extractor, mock_llm_service):
        """测试错误处理流程"""
        # 测试LLM服务异步异常处理
        async def mock_generate_error(prompt):
            raise Exception("API调用失败")
        mock_llm_service.generate = mock_generate_error

        # 应该优雅处理异常，返回空结果
        result = await knowledge_extractor.extract("Some English text")
        # 验证异常被捕获并返回空列表
        assert result == []

    @pytest.mark.asyncio
    async def test_complete_english_grading_simulation(self, subject_router, knowledge_extractor, mock_llm_service):
        """测试完整的英语批改流程模拟"""
        # 模拟一个完整的英语作业文本
        homework_text = """
        English Grammar Exercise

        1. Fill in the blanks with correct form:
           I _____ (study) English for three years.
           She _____ (go) to London last summer.

        2. Choose the correct answer:
           _____ you ever been to Paris?
           A) Have  B) Do  C) Are  D) Were

        3. Translate the following sentence:
           "今天天气很好。"
        """

        # 第一步：科目检测
        detection_result = subject_router.detect_subject(homework_text)
        assert detection_result.primary_subject == Subject.ENGLISH
        assert detection_result.is_mixed_content == True  # 包含中文

        # 第二步：知识点提取
        mock_response = {
            "knowledge_points": [
                {
                    "name": "现在完成时",
                    "category": "语法",
                    "subcategory": "时态",
                    "difficulty_level": "中等",
                    "confidence": 0.9
                },
                {
                    "name": "一般过去时",
                    "category": "语法",
                    "subcategory": "时态",
                    "difficulty_level": "基础",
                    "confidence": 0.85
                },
                {
                    "name": "翻译",
                    "category": "写作",
                    "subcategory": "写作技巧",
                    "difficulty_level": "中等",
                    "confidence": 0.8
                }
            ]
        }

        async def mock_generate_homework(prompt):
            return str(mock_response)
        mock_llm_service.generate = mock_generate_homework
        mock_llm_service.safe_json_parse.return_value = mock_response

        knowledge_points = await knowledge_extractor.extract(homework_text)

        # 验证知识点提取结果
        assert len(knowledge_points) == 3
        point_names = [point['name'] for point in knowledge_points]
        assert "现在完成时" in point_names
        assert "一般过去时" in point_names
        assert "翻译" in point_names

        # 第三步：难度评估
        difficulty = knowledge_extractor.get_difficulty_assessment(knowledge_points)
        assert difficulty in ["基础", "中等", "高级"]

    def test_english_prompt_format_consistency(self):
        """测试英语提示词格式一致性"""
        from src.ai_tutor.services.llm.prompts.base import PromptVersion

        # 获取格式示例
        format_example = english_prompts.get_format_example()

        # 验证JSON格式有效性
        import json
        try:
            parsed_example = json.loads(format_example)
            assert 'questions' in parsed_example
            assert 'overall_score' in parsed_example

            # 验证英语特定字段
            if parsed_example['questions']:
                first_question = parsed_example['questions'][0]
                assert 'grammar_accuracy' in first_question
                assert 'vocabulary_appropriateness' in first_question
                assert 'fluency_score' in first_question

        except json.JSONDecodeError:
            pytest.fail("英语批改格式示例不是有效的JSON格式")

    def test_multilingual_content_handling(self, subject_router):
        """测试多语言内容处理"""
        # 测试各种多语言组合
        test_cases = [
            {
                'text': '英语练习：What is your name? 请用英语回答。',
                'expected_mixed': True,
                'expected_primary': Subject.ENGLISH
            },
            {
                'text': 'Grammar: 选择正确答案 Choose the right answer.',
                'expected_mixed': True,
                'expected_primary': Subject.ENGLISH
            },
            {
                'text': '这是一道英语语法题：She _____ to school every day.',
                'expected_mixed': True,
                'expected_primary': Subject.ENGLISH
            }
        ]

        for case in test_cases:
            result = subject_router.detect_subject(case['text'])
            assert result.is_mixed_content == case['expected_mixed'], \
                f"Mixed content detection failed for: {case['text']}"
            assert result.primary_subject == case['expected_primary'], \
                f"Primary subject detection failed for: {case['text']}"

    @pytest.mark.asyncio
    async def test_knowledge_point_confidence_scoring(self, knowledge_extractor, mock_llm_service):
        """测试知识点置信度评分"""
        # 测试不同置信度的知识点提取
        test_text = "She has been studying English for five years."

        mock_response = {
            "knowledge_points": [
                {
                    "name": "现在完成进行时",
                    "category": "语法",
                    "confidence": 0.95  # 高置信度
                },
                {
                    "name": "时间表达",
                    "category": "语法",
                    "confidence": 0.7   # 中等置信度
                }
            ]
        }

        async def mock_generate_confidence(prompt):
            return str(mock_response)
        mock_llm_service.generate = mock_generate_confidence
        mock_llm_service.safe_json_parse.return_value = mock_response

        result = await knowledge_extractor.extract(test_text)

        # 验证置信度被正确保留
        confidence_scores = [point['confidence'] for point in result]
        assert 0.95 in confidence_scores
        assert 0.7 in confidence_scores

        # 验证所有置信度在有效范围内
        for score in confidence_scores:
            assert 0 <= score <= 1

    def test_performance_with_large_text(self, subject_router):
        """测试大文本处理性能"""
        # 生成较大的英语文本
        large_text = """
        English Grammar and Vocabulary Test

        Part I: Grammar (50 points)
        """ + "Fill in the blanks with the correct form of the verb. " * 50 + """

        Part II: Reading Comprehension (30 points)
        """ + "Read the passage and answer the questions. " * 30 + """

        Part III: Writing (20 points)
        """ + "Write an essay about your favorite hobby. " * 20

        # 执行检测（应该在合理时间内完成）
        import time
        start_time = time.time()
        result = subject_router.detect_subject(large_text)
        end_time = time.time()

        # 验证结果正确性
        assert result.primary_subject == Subject.ENGLISH
        assert result.confidence > 0.5

        # 验证性能（应该在几秒内完成）
        processing_time = end_time - start_time
        assert processing_time < 10, f"处理时间过长: {processing_time:.2f}秒"
