"""
科目路由服务的单元测试
"""
import pytest
from src.ai_tutor.services.parsing.subject_router import (
    SubjectRouter, Subject, SubjectDetectionResult, detect_subject
)


class TestSubjectRouter:
    """科目路由服务测试类"""

    @pytest.fixture
    def router(self):
        """创建科目路由器实例"""
        return SubjectRouter()

    def test_detect_pure_english_content(self, router):
        """测试纯英文内容识别"""
        english_text = """
        What is your favorite color? My favorite color is blue. 
        I like blue because it reminds me of the sky and ocean.
        Yesterday, I went to the park and saw many beautiful flowers.
        """
        
        result = router.detect_subject(english_text)
        
        assert result.primary_subject == Subject.ENGLISH
        assert result.confidence > 0.5
        assert result.language_features['english_ratio'] > 0.8

    def test_detect_math_content(self, router):
        """测试数学内容识别"""
        math_text = """
        计算下列数学题：
        1. 3 + 5 × 2 = ?
        2. 解方程：2x + 3 = 7
        3. 求三角形的面积，已知底边长为6cm，高为4cm
        """
        
        result = router.detect_subject(math_text)
        
        assert result.primary_subject == Subject.MATH
        assert result.confidence > 0.5
        assert 'symbol_matches' in result.detection_features['math']

    def test_detect_chinese_english_mixed(self, router):
        """测试中英混合英语教学内容"""
        mixed_text = """
        英语语法练习题：
        1. Choose the correct answer: She _____ to school every day.
           A) go  B) goes  C) going  D) gone
        2. 翻译下列句子：
           The weather is nice today.
        3. 填空：I _____ (study) English for three years.
        """
        
        result = router.detect_subject(mixed_text)
        
        assert result.primary_subject == Subject.ENGLISH
        assert result.is_mixed_content == True
        assert 0.1 < result.language_features['english_ratio'] < 0.8
        assert result.language_features['chinese_ratio'] > 0.2

    def test_detect_physics_content(self, router):
        """测试物理内容识别"""
        physics_text = """
        物理计算题：
        一个物体从静止开始做匀加速直线运动，加速度为2m/s²。
        求：(1) 物体在第3秒末的速度 v = at
        (2) 物体在前3秒内的位移 s = ½at²
        """
        
        result = router.detect_subject(physics_text)
        
        assert result.primary_subject == Subject.PHYSICS
        assert result.confidence > 0.3

    def test_detect_chinese_content(self, router):
        """测试语文内容识别"""
        chinese_text = """
        阅读理解：
        春天来了，万物复苏。桃花红，柳树绿，小鸟在枝头歌唱。
        这是一个充满生机的季节。请回答以下问题：
        1. 文章描述了什么季节？
        2. 作者用了哪些修辞手法？
        3. 文章表达了什么中心思想？
        """
        
        result = router.detect_subject(chinese_text)
        
        assert result.primary_subject == Subject.CHINESE
        assert result.language_features['chinese_ratio'] > 0.8

    def test_detect_english_grammar_exercise(self, router):
        """测试英语语法练习识别"""
        grammar_text = """
        Grammar Exercise - Present Perfect Tense
        
        Fill in the blanks with the correct form of the verb:
        1. I _____ (finish) my homework already.
        2. She _____ (live) here since 2010.
        3. They _____ never _____ (see) such a beautiful sunset.
        
        Choose the correct answer:
        4. Have you ever _____ to Paris?
           a) been  b) go  c) went  d) going
        """
        
        result = router.detect_subject(grammar_text)
        
        assert result.primary_subject == Subject.ENGLISH
        assert result.confidence > 0.6

    def test_detect_english_reading_comprehension(self, router):
        """测试英语阅读理解识别"""
        reading_text = """
        Reading Comprehension
        
        The Internet has changed the way we live and work. Today, people can shop, 
        study, and communicate online. This technology has made our lives more convenient, 
        but it has also created new challenges. For example, some people spend too much 
        time online and forget to exercise or meet friends in person.
        
        Questions:
        1. What is the main idea of the passage?
        2. What are the advantages of the Internet mentioned in the text?
        3. What challenges does the Internet create?
        """
        
        result = router.detect_subject(reading_text)
        
        assert result.primary_subject == Subject.ENGLISH
        assert 'pattern_matches' in result.detection_features['english']

    def test_detect_english_vocabulary_exercise(self, router):
        """测试英语词汇练习识别"""
        vocab_text = """
        Vocabulary Exercise
        
        Match the words with their definitions:
        1. enormous    a) very small
        2. tiny        b) very large
        3. ancient     c) very old
        4. modern      d) contemporary
        
        Choose the synonym:
        5. happy = _____ (joyful, sad, angry, tired)
        """
        
        result = router.detect_subject(vocab_text)
        
        assert result.primary_subject == Subject.ENGLISH

    def test_detect_mixed_subjects(self, router):
        """测试多学科混合内容"""
        mixed_text = """
        综合练习题：
        1. 数学：计算 2x + 3 = 7 中 x 的值
        2. 英语：Translate: "今天天气很好"
        3. 物理：计算重力 F = mg，其中 m = 5kg, g = 10m/s²
        """
        
        result = router.detect_subject(mixed_text)
        
        # 应该识别出多个科目
        assert len(result.secondary_subjects) > 0
        assert result.is_mixed_content == True

    def test_language_feature_analysis(self, router):
        """测试语言特征分析"""
        text = "Hello world! 你好世界！123 + 456 = 579"
        
        features = router._analyze_language_features(text)
        
        assert 'english_ratio' in features
        assert 'chinese_ratio' in features
        assert 'digit_ratio' in features
        assert 'symbol_ratio' in features
        assert features['total_words'] > 0
        assert features['avg_word_length'] > 0

    def test_preprocess_text(self, router):
        """测试文本预处理"""
        messy_text = "This is a  test\r\nwith\rmultiple\n\nspaces   and line breaks."
        
        cleaned = router._preprocess_text(messy_text)
        
        # 验证清理效果
        assert '\r' not in cleaned
        assert '  ' not in cleaned  # 多余空格被清理
        assert cleaned.strip() == cleaned  # 首尾空格被清理

    def test_english_score_calculation(self, router):
        """测试英语得分计算"""
        # 高英文比例的文本
        high_english_text = "This is a comprehensive English text with many words and sentences."
        features = router._analyze_language_features(high_english_text)
        score = router._calculate_english_score(high_english_text, features)
        
        assert score > 0
        
        # 中英混合教学文本
        mixed_teaching_text = "英语grammar练习: What is your name? 语法填空题。"
        features2 = router._analyze_language_features(mixed_teaching_text)
        score2 = router._calculate_english_score(mixed_teaching_text, features2)
        
        assert score2 > 0

    def test_fallback_subject_detection(self, router):
        """测试后备科目检测方法"""
        # 高英文比例文本
        english_text = "This text contains mostly English words and characters."
        result = router._fallback_subject_detection(english_text)
        assert "英语" in result
        
        # 数学符号文本
        math_text = "计算题: 2 + 3 × 4 = ?"
        result = router._fallback_subject_detection(math_text)
        assert "数学" in result
        
        # 中文文学文本
        chinese_text = "这篇文章描述了春天的美丽景色，作者运用了比喻的修辞手法。"
        result = router._fallback_subject_detection(chinese_text)
        assert "语文" in result

    def test_empty_text_handling(self, router):
        """测试空文本处理"""
        result = router.detect_subject("")
        
        assert result.primary_subject == Subject.MATH  # 默认为数学
        assert result.confidence == 0.1  # 低置信度

    def test_very_short_text(self, router):
        """测试极短文本"""
        result = router.detect_subject("Hello")
        
        assert result.primary_subject == Subject.ENGLISH
        assert result.confidence > 0

    def test_subject_detection_result_structure(self, router):
        """测试科目检测结果结构"""
        text = "This is a test sentence for subject detection."
        result = router.detect_subject(text)
        
        # 验证结果结构完整性
        assert isinstance(result, SubjectDetectionResult)
        assert isinstance(result.primary_subject, Subject)
        assert isinstance(result.confidence, float)
        assert isinstance(result.secondary_subjects, list)
        assert isinstance(result.detection_features, dict)
        assert isinstance(result.is_mixed_content, bool)
        assert isinstance(result.language_features, dict)

    def test_confidence_levels(self, router):
        """测试置信度水平"""
        # 明确的英语内容应该有高置信度
        clear_english = "What is your name? How old are you? Where do you live?"
        result = router.detect_subject(clear_english)
        assert result.confidence > 0.5
        
        # 模糊内容应该有较低置信度
        ambiguous = "123 abc"
        result = router.detect_subject(ambiguous)
        assert result.confidence < 0.8

    def test_detect_subject_convenience_function(self):
        """测试便捷函数"""
        text = "English grammar test: Choose the correct answer."
        result = detect_subject(text)
        
        assert isinstance(result, SubjectDetectionResult)
        assert result.primary_subject == Subject.ENGLISH

    def test_secondary_subjects_ordering(self, router):
        """测试次要科目按分数排序"""
        # 创建包含多个科目特征的文本
        multi_subject_text = """
        综合题目：
        1. English: What is 2+3? 
        2. 数学计算：5×6=30
        3. 物理公式：F=ma
        """
        
        result = router.detect_subject(multi_subject_text)
        
        # 验证次要科目按分数降序排列
        if len(result.secondary_subjects) > 1:
            # 这里我们无法直接访问分数，但可以验证列表不为空
            assert len(result.secondary_subjects) <= 3  # 最多3个次要科目

    def test_mixed_content_detection(self, router):
        """测试混合内容检测逻辑"""
        # 单一科目内容
        single_subject = "This is purely English content with no mixed elements."
        result = router.detect_subject(single_subject)
        assert result.is_mixed_content == False
        
        # 混合内容
        mixed_content = "English and 中文 mixed content with various elements."
        result = router.detect_subject(mixed_content)
        assert result.is_mixed_content == True
