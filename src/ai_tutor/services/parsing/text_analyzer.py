"""
文本分析器 - 提供OCR文本的深度分析功能
"""
import re
from typing import Dict, List, Any, Tuple
from ...core.logger import LoggerMixin


class TextAnalyzer(LoggerMixin):
    """文本分析器 - 分析OCR文本的质量、结构和特征"""
    
    def analyze_text_quality(self, text: str) -> Dict[str, Any]:
        """分析文本质量"""
        return {
            "length": len(text),
            "char_count": len(text.replace(' ', '')),
            "word_count": len(text.split()),
            "line_count": text.count('\n') + 1,
            "chinese_char_ratio": self._calculate_chinese_ratio(text),
            "digit_ratio": self._calculate_digit_ratio(text),
            "special_char_count": self._count_special_chars(text),
            "ocr_confidence": self._estimate_ocr_confidence(text),
            "readability_score": self._calculate_readability(text)
        }
    
    def detect_text_structure(self, text: str) -> Dict[str, Any]:
        """检测文本结构"""
        return {
            "has_question_numbers": self._has_question_numbers(text),
            "question_patterns": self._detect_question_patterns(text),
            "answer_patterns": self._detect_answer_patterns(text),
            "mathematical_content": self._detect_mathematical_content(text),
            "table_like_structure": self._detect_table_structure(text),
            "handwriting_indicators": self._detect_handwriting_indicators(text)
        }
    
    def extract_key_features(self, text: str) -> Dict[str, Any]:
        """提取关键特征"""
        quality = self.analyze_text_quality(text)
        structure = self.detect_text_structure(text)
        
        return {
            **quality,
            **structure,
            "complexity_score": self._calculate_complexity(text),
            "subject_indicators": self._detect_subject_indicators(text),
            "grade_level_estimate": self._estimate_grade_level(text)
        }
    
    def _calculate_chinese_ratio(self, text: str) -> float:
        """计算中文字符比例"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.replace(' ', ''))
        return chinese_chars / max(total_chars, 1)
    
    def _calculate_digit_ratio(self, text: str) -> float:
        """计算数字字符比例"""
        digit_chars = len(re.findall(r'\d', text))
        total_chars = len(text.replace(' ', ''))
        return digit_chars / max(total_chars, 1)
    
    def _count_special_chars(self, text: str) -> int:
        """计算特殊字符数量"""
        special_chars = re.findall(r'[^\w\s\u4e00-\u9fff]', text)
        return len(special_chars)
    
    def _estimate_ocr_confidence(self, text: str) -> float:
        """估算OCR识别置信度"""
        confidence = 0.5
        
        # 基于文本特征的启发式评估
        
        # 连续字符异常
        if re.search(r'[a-zA-Z]{10,}', text):  # 异常长的字母序列
            confidence -= 0.2
        
        # 数字字母混乱
        confusion_patterns = [
            r'[0O]{3,}',   # 连续的0和O
            r'[1lI]{3,}',  # 连续的1、l、I
            r'[5S]{2,}',   # 连续的5和S
        ]
        for pattern in confusion_patterns:
            if re.search(pattern, text):
                confidence -= 0.1
        
        # 合理的标点符号使用
        if re.search(r'[。，！？；：]', text):
            confidence += 0.1
        
        # 数学符号的合理性
        if re.search(r'[+\-×÷=]', text) and re.search(r'\d', text):
            confidence += 0.1
        
        return max(0.1, min(confidence, 1.0))
    
    def _calculate_readability(self, text: str) -> float:
        """计算可读性分数"""
        if not text.strip():
            return 0.0
        
        words = text.split()
        sentences = re.split(r'[。！？\.\!\?]', text)
        sentences = [s for s in sentences if s.strip()]
        
        if not words or not sentences:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words)
        
        # 简化的可读性评分
        readability = 100 - (avg_words_per_sentence * 2 + avg_chars_per_word * 5)
        return max(0.0, min(100.0, readability)) / 100
    
    def _has_question_numbers(self, text: str) -> bool:
        """检测是否包含题目编号"""
        number_patterns = [
            r'\d+\s*[\.。]',
            r'\d+\s*[、,]',
            r'\(\d+\)',
            r'（\d+）',
            r'第\s*\d+\s*[题道]'
        ]
        return any(re.search(pattern, text) for pattern in number_patterns)
    
    def _detect_question_patterns(self, text: str) -> List[str]:
        """检测题目模式"""
        patterns = []
        
        question_indicators = [
            (r'选择.*?题', '选择题'),
            (r'填空.*?题', '填空题'),
            (r'计算.*?题', '计算题'),
            (r'判断.*?题', '判断题'),
            (r'解答.*?题', '解答题'),
            (r'[?？]', '问题标记'),
            (r'求.*?值', '求值题'),
            (r'证明', '证明题')
        ]
        
        for pattern, name in question_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append(name)
        
        return patterns
    
    def _detect_answer_patterns(self, text: str) -> List[str]:
        """检测答案模式"""
        patterns = []
        
        answer_indicators = [
            (r'答案?[:：]', '标准答案标记'),
            (r'解[:：]', '解答标记'),
            (r'学生答', '学生答案标记'),
            (r'[ABCD](?:\s|$)', '选择题答案'),
            (r'正确|错误|对|错', '判断题答案'),
            (r'√|×', '判断符号')
        ]
        
        for pattern, name in answer_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append(name)
        
        return patterns
    
    def _detect_mathematical_content(self, text: str) -> Dict[str, bool]:
        """检测数学内容"""
        return {
            "has_arithmetic": bool(re.search(r'[+\-×÷]', text)),
            "has_equations": bool(re.search(r'=', text)),
            "has_fractions": bool(re.search(r'\d+/\d+', text)),
            "has_powers": bool(re.search(r'\d+\s*[²³⁴⁵⁶⁷⁸⁹⁰]', text)),
            "has_geometry": bool(re.search(r'三角形|圆|正方形|长方形|面积|周长', text)),
            "has_algebra": bool(re.search(r'[xyz]|未知数|方程', text))
        }
    
    def _detect_table_structure(self, text: str) -> bool:
        """检测表格结构"""
        # 简单的表格结构检测
        lines = text.split('\n')
        aligned_lines = 0
        
        for line in lines:
            if len(re.findall(r'\s{3,}', line)) >= 2:  # 多个大空格，可能是表格
                aligned_lines += 1
        
        return aligned_lines >= 2
    
    def _detect_handwriting_indicators(self, text: str) -> List[str]:
        """检测手写体指示符"""
        indicators = []
        
        # OCR常见的手写体识别错误
        handwriting_errors = [
            (r'[oO0]{3,}', '可能的手写数字混淆'),
            (r'[Il1]{3,}', '可能的手写字母数字混淆'),
            (r'[。，]{2,}', '重复标点可能来自手写'),
            (r'\s{5,}', '大空白可能是手写空间')
        ]
        
        for pattern, desc in handwriting_errors:
            if re.search(pattern, text):
                indicators.append(desc)
        
        return indicators
    
    def _calculate_complexity(self, text: str) -> float:
        """计算文本复杂度"""
        complexity = 0.0
        
        # 基于多个因素计算复杂度
        factors = [
            (len(text), 0.0001),  # 长度因子
            (len(set(text)), 0.001),  # 字符多样性
            (text.count('(') + text.count('['), 0.05),  # 括号复杂性
            (len(re.findall(r'[+\-×÷=]', text)), 0.1),  # 数学复杂性
        ]
        
        for value, weight in factors:
            complexity += value * weight
        
        return min(complexity, 1.0)
    
    def _detect_subject_indicators(self, text: str) -> List[str]:
        """检测科目指示符"""
        subjects = []
        
        subject_keywords = {
            '数学': [r'计算', r'方程', r'几何', r'代数', r'[+\-×÷=]', r'函数'],
            '语文': [r'阅读', r'作文', r'古诗', r'文言文', r'成语'],
            '英语': [r'[A-Za-z]{5,}', r'grammar', r'vocabulary', r'reading'],
            '物理': [r'力', r'电', r'光', r'热', r'声', r'运动'],
            '化学': [r'化学', r'反应', r'元素', r'分子', r'原子'],
            '生物': [r'细胞', r'基因', r'植物', r'动物', r'生物']
        }
        
        for subject, keywords in subject_keywords.items():
            if any(re.search(keyword, text, re.IGNORECASE) for keyword in keywords):
                subjects.append(subject)
        
        return subjects
    
    def _estimate_grade_level(self, text: str) -> str:
        """估算年级水平"""
        complexity = self._calculate_complexity(text)
        
        if complexity < 0.2:
            return "小学"
        elif complexity < 0.5:
            return "初中"
        else:
            return "高中"


# 便捷函数
def analyze_homework_text(text: str) -> Dict[str, Any]:
    """便捷函数：分析作业文本"""
    analyzer = TextAnalyzer()
    return analyzer.extract_key_features(text)
