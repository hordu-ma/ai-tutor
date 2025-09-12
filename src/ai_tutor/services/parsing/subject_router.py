"""
科目路由服务 - 智能科目检测和路由功能
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from ...core.logger import get_logger

logger = get_logger(__name__)


class Subject(Enum):
    """支持的学科枚举"""
    MATH = "math"
    ENGLISH = "english" 
    CHINESE = "chinese"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"


@dataclass
class SubjectDetectionResult:
    """科目检测结果"""
    primary_subject: Subject
    confidence: float
    secondary_subjects: List[Subject]
    detection_features: Dict[str, Any]
    is_mixed_content: bool
    language_features: Dict[str, float]


class SubjectRouter:
    """
    科目路由服务 - 提供智能的科目检测和内容路由功能
    
    特别针对英语内容的识别进行了优化，支持：
    - 纯英文内容识别
    - 中英混合内容识别
    - 英语教学材料识别
    - 多科目内容识别
    """

    def __init__(self):
        self.subject_detectors = {
            Subject.MATH: self._detect_math_content,
            Subject.ENGLISH: self._detect_english_content,
            Subject.CHINESE: self._detect_chinese_content,
            Subject.PHYSICS: self._detect_physics_content,
            Subject.CHEMISTRY: self._detect_chemistry_content,
            Subject.BIOLOGY: self._detect_biology_content,
        }

    def detect_subject(self, text: str) -> SubjectDetectionResult:
        """
        检测文本的主要学科
        
        Args:
            text: 要分析的文本内容
            
        Returns:
            包含检测结果的SubjectDetectionResult对象
        """
        logger.info("开始科目检测", text_length=len(text))
        
        # 预处理文本
        cleaned_text = self._preprocess_text(text)
        
        # 分析语言特征
        language_features = self._analyze_language_features(cleaned_text)
        
        # 运行所有科目检测器
        subject_scores = {}
        detection_details = {}
        
        for subject, detector in self.subject_detectors.items():
            try:
                score, features = detector(cleaned_text, language_features)
                subject_scores[subject] = score
                detection_details[subject.value] = features
            except Exception as e:
                logger.warning(f"科目检测器异常: {subject.value}", error=str(e))
                subject_scores[subject] = 0.0
                detection_details[subject.value] = {}
        
        # 确定主要科目和次要科目
        primary_subject, confidence = self._determine_primary_subject(subject_scores)
        secondary_subjects = self._get_secondary_subjects(subject_scores, primary_subject, threshold=0.3)
        
        # 检测是否为混合内容
        is_mixed = self._is_mixed_content(subject_scores, language_features)
        
        result = SubjectDetectionResult(
            primary_subject=primary_subject,
            confidence=confidence,
            secondary_subjects=secondary_subjects,
            detection_features=detection_details,
            is_mixed_content=is_mixed,
            language_features=language_features
        )
        
        logger.info("科目检测完成", 
                   primary_subject=primary_subject.value,
                   confidence=confidence,
                   secondary_subjects=[s.value for s in secondary_subjects],
                   is_mixed=is_mixed)
        
        return result

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 统一换行符
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # 清理多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 修复常见OCR错误
        text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)  # 数字中的O修复为0
        text = re.sub(r'(?<=[A-Za-z])[0](?=[A-Za-z])', 'O', text)  # 字母中的0修复为O
        
        return text.strip()

    def _analyze_language_features(self, text: str) -> Dict[str, float]:
        """分析文本的语言特征"""
        total_chars = len(text.replace(' ', ''))
        if total_chars == 0:
            return {
                'english_ratio': 0.0,
                'chinese_ratio': 0.0,
                'digit_ratio': 0.0,
                'symbol_ratio': 0.0,
                'punctuation_ratio': 0.0
            }
        
        english_chars = len(re.findall(r'[A-Za-z]', text))
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        digit_chars = len(re.findall(r'\d', text))
        symbol_chars = len(re.findall(r'[+\-×÷=<>≤≥≠∞∑∏∫∂∇]', text))
        punctuation_chars = len(re.findall(r'[。，！？；：、""''（）【】〈〉《》]', text))
        
        return {
            'english_ratio': english_chars / total_chars,
            'chinese_ratio': chinese_chars / total_chars,
            'digit_ratio': digit_chars / total_chars,
            'symbol_ratio': symbol_chars / total_chars,
            'punctuation_ratio': punctuation_chars / total_chars,
            'total_words': len(text.split()),
            'avg_word_length': sum(len(word) for word in text.split()) / max(len(text.split()), 1)
        }

    def _detect_english_content(self, text: str, lang_features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """检测英语内容"""
        score = 0.0
        features = {}
        
        # 基础英语特征
        english_ratio = lang_features['english_ratio']
        
        # 英文字符比例得分
        if english_ratio > 0.5:
            score += 40  # 大量英文内容
        elif english_ratio > 0.3:
            score += 30  # 中等英文内容
        elif english_ratio > 0.1:
            score += 20  # 少量英文内容
        
        features['english_ratio'] = english_ratio
        
        # 英语语言模式检测
        english_patterns = {
            'question_words': r'\b(what|where|when|why|how|which|who|whose)\b',
            'be_verbs': r'\b(is|are|was|were|am|be|being|been)\b',
            'auxiliary_verbs': r'\b(do|does|did|don\'t|doesn\'t|didn\'t|have|has|had|haven\'t|hasn\'t|hadn\'t)\b',
            'modal_verbs': r'\b(will|would|can|could|should|shall|may|might|must)\b',
            'articles': r'\b(a|an|the)\b',
            'prepositions': r'\b(in|on|at|by|for|with|from|to|of|about|under|over)\b',
            'pronouns': r'\b(i|you|he|she|it|we|they|me|him|her|us|them|my|your|his|her|its|our|their)\b',
            'past_tense': r'\b\w+ed\b',
            'present_participle': r'\b\w+ing\b',
            'comparative': r'\b\w+er\b|\bmore\s+\w+\b',
            'superlative': r'\b\w+est\b|\bmost\s+\w+\b'
        }
        
        pattern_matches = {}
        for pattern_name, pattern in english_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            pattern_matches[pattern_name] = matches
            if matches > 0:
                score += min(matches * 2, 10)  # 每个模式最多贡献10分
        
        features['pattern_matches'] = pattern_matches
        
        # 英语教学内容特征
        teaching_patterns = {
            'chinese_english_terms': [
                r'英语|English|英文',
                r'单词|word|词汇|vocabulary',
                r'语法|grammar',
                r'时态|tense',
                r'句型|sentence\s+pattern',
                r'阅读理解|reading\s+comprehension',
                r'完形填空|cloze\s+test',
                r'听力|listening',
                r'口语|speaking|oral',
                r'写作|writing|composition'
            ],
            'exercise_patterns': [
                r'选择题.*[ABCD]',
                r'Choose\s+the\s+(correct|right|best)',
                r'Fill\s+in\s+the\s+blank',
                r'Complete\s+the\s+sentence',
                r'Translate\s+the\s+following',
                r'翻译.*下列.*句子'
            ]
        }
        
        teaching_score = 0
        for category, patterns in teaching_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    teaching_score += 5
            features[f'{category}_matches'] = matches
        
        score += min(teaching_score, 25)  # 教学内容最多贡献25分
        
        # 英语文本结构特征
        structure_features = {
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            'capital_words': len(re.findall(r'\b[A-Z][a-z]+\b', text)),
            'quotation_marks': len(re.findall(r'["\'"]', text)),
            'contractions': len(re.findall(r'\b\w+\'[a-z]+\b', text, re.IGNORECASE))
        }
        
        features['structure_features'] = structure_features
        
        # 结构特征加分
        if structure_features['capital_words'] > 2:
            score += 5
        if structure_features['contractions'] > 0:
            score += 3
        
        # 中英混合内容特别处理
        if 0.1 <= english_ratio <= 0.8 and lang_features['chinese_ratio'] > 0.2:
            # 可能是英语教学材料
            mixed_patterns = [
                r'第.*题.*[A-Za-z]',  # 中文题目编号+英文内容
                r'[A-Za-z].*的.*意思',  # 英文单词的中文解释
                r'用英语.*表达',      # 英语表达练习
                r'把.*翻译成.*英语'   # 翻译练习
            ]
            
            for pattern in mixed_patterns:
                if re.search(pattern, text):
                    score += 8
        
        features['final_score'] = score
        return min(score / 100, 1.0), features  # 归一化到0-1

    def _detect_math_content(self, text: str, lang_features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """检测数学内容"""
        score = 0.0
        features = {}
        
        # 数学符号
        math_symbols = r'[+\-×÷=<>≤≥≠∞∑∏∫∂∇π√]'
        symbol_matches = len(re.findall(math_symbols, text))
        score += min(symbol_matches * 5, 30)
        features['symbol_matches'] = symbol_matches
        
        # 数学关键词
        math_keywords = [
            r'计算|求解|解方程|求值',
            r'几何|三角形|圆|正方形|长方形',
            r'代数|函数|变量|未知数',
            r'概率|统计|平均数|中位数',
            r'面积|周长|体积|表面积',
            r'角度|弧度|正弦|余弦|正切'
        ]
        
        keyword_matches = 0
        for keyword in math_keywords:
            if re.search(keyword, text):
                keyword_matches += 1
                score += 8
        features['keyword_matches'] = keyword_matches
        
        # 数学表达式模式
        math_expressions = [
            r'\d+\s*[+\-×÷]\s*\d+\s*=',  # 算式
            r'\w+\s*=\s*\d+',            # 赋值表达式
            r'\d+/\d+',                   # 分数
            r'\d+²|\d+³',                 # 幂次
            r'\(\s*\d+\s*,\s*\d+\s*\)'   # 坐标
        ]
        
        expr_matches = 0
        for expr in math_expressions:
            matches = len(re.findall(expr, text))
            expr_matches += matches
            score += matches * 3
        features['expression_matches'] = expr_matches
        
        return min(score / 100, 1.0), features

    def _detect_chinese_content(self, text: str, lang_features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """检测语文内容"""
        score = 0.0
        features = {}
        
        chinese_ratio = lang_features['chinese_ratio']
        if chinese_ratio > 0.8:
            score += 40
        elif chinese_ratio > 0.6:
            score += 30
        
        # 语文关键词
        chinese_keywords = [
            r'阅读理解|文章理解|语文',
            r'古诗|诗歌|文言文|现代文',
            r'作文|写作|议论文|记叙文|说明文',
            r'成语|词语|句子|段落',
            r'修辞手法|比喻|拟人|排比',
            r'中心思想|主题思想|段意'
        ]
        
        for keyword in chinese_keywords:
            if re.search(keyword, text):
                score += 10
        
        # 中文标点符号
        chinese_punct = len(re.findall(r'[。，！？；：、""''（）【】]', text))
        score += min(chinese_punct, 20)
        features['chinese_punctuation'] = chinese_punct
        
        return min(score / 100, 1.0), features

    def _detect_physics_content(self, text: str, lang_features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """检测物理内容"""
        score = 0.0
        features = {}
        
        physics_keywords = [
            r'力学|电学|光学|热学|声学',
            r'速度|加速度|位移|时间',
            r'电流|电压|电阻|功率',
            r'牛顿|焦耳|瓦特|安培',
            r'重力|摩擦力|弹力|压力',
            r'波长|频率|振幅|周期'
        ]
        
        for keyword in physics_keywords:
            if re.search(keyword, text):
                score += 12
        
        # 物理公式模式
        physics_formulas = [
            r'F\s*=\s*m\s*a',
            r'v\s*=\s*s\s*/\s*t',
            r'P\s*=\s*U\s*I',
            r'E\s*=\s*m\s*c²'
        ]
        
        for formula in physics_formulas:
            if re.search(formula, text, re.IGNORECASE):
                score += 15
        
        return min(score / 100, 1.0), features

    def _detect_chemistry_content(self, text: str, lang_features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """检测化学内容"""
        score = 0.0
        features = {}
        
        chemistry_keywords = [
            r'化学|反应|元素|分子|原子',
            r'氧化|还原|酸碱|中和',
            r'溶液|浓度|摩尔|离子',
            r'有机|无机|催化剂|化合价'
        ]
        
        for keyword in chemistry_keywords:
            if re.search(keyword, text):
                score += 12
        
        # 化学式模式
        chemical_formulas = r'[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*'
        formula_matches = len(re.findall(chemical_formulas, text))
        score += min(formula_matches * 3, 20)
        features['formula_matches'] = formula_matches
        
        return min(score / 100, 1.0), features

    def _detect_biology_content(self, text: str, lang_features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """检测生物内容"""
        score = 0.0
        features = {}
        
        biology_keywords = [
            r'细胞|基因|DNA|RNA|蛋白质',
            r'植物|动物|生态系统|进化',
            r'光合作用|呼吸作用|新陈代谢',
            r'遗传|变异|自然选择|适应'
        ]
        
        for keyword in biology_keywords:
            if re.search(keyword, text):
                score += 12
        
        return min(score / 100, 1.0), features

    def _determine_primary_subject(self, subject_scores: Dict[Subject, float]) -> Tuple[Subject, float]:
        """确定主要科目"""
        if not subject_scores:
            return Subject.MATH, 0.0  # 默认为数学
        
        sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
        primary_subject, confidence = sorted_subjects[0]
        
        # 如果最高分太低，降低置信度
        if confidence < 0.1:
            confidence = 0.1
        
        return primary_subject, confidence

    def _get_secondary_subjects(self, subject_scores: Dict[Subject, float], 
                              primary_subject: Subject, threshold: float) -> List[Subject]:
        """获取次要科目"""
        secondary = []
        for subject, score in subject_scores.items():
            if subject != primary_subject and score >= threshold:
                secondary.append(subject)
        
        # 按分数排序
        secondary.sort(key=lambda s: subject_scores[s], reverse=True)
        return secondary[:3]  # 最多返回3个次要科目

    def _is_mixed_content(self, subject_scores: Dict[Subject, float], 
                         lang_features: Dict[str, float]) -> bool:
        """判断是否为混合内容"""
        # 如果多个科目得分都较高
        high_score_subjects = sum(1 for score in subject_scores.values() if score >= 0.3)
        if high_score_subjects >= 2:
            return True
        
        # 如果语言特征显示多种语言混合
        english_ratio = lang_features.get('english_ratio', 0)
        chinese_ratio = lang_features.get('chinese_ratio', 0)
        
        if 0.2 <= english_ratio <= 0.8 and chinese_ratio >= 0.2:
            return True
        
        return False


# 便捷函数
def detect_subject(text: str) -> SubjectDetectionResult:
    """便捷函数：检测文本科目"""
    router = SubjectRouter()
    return router.detect_subject(text)
