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
        """检测科目指示符 - 增强英语识别能力"""
        subjects = []
        
        # 增强的科目关键词，特别加强英语识别
        subject_keywords = {
            '数学': {
                'primary': [r'计算', r'方程', r'几何', r'代数', r'函数', r'求解', r'证明'],
                'symbols': [r'[+\-×÷=]', r'\d+/\d+', r'\d+²', r'\d+³'],
                'concepts': [r'三角形', r'圆', r'面积', r'周长', r'角度', r'直线', r'平面']
            },
            '语文': {
                'primary': [r'阅读', r'作文', r'古诗', r'文言文', r'成语', r'诗歌'],
                'symbols': [r'[。，！？；：]', r'""', r"''"],
                'concepts': [r'修辞', r'比喻', r'拟人', r'排比', r'对偶', r'段落', r'中心思想']
            },
            '英语': {
                'primary': [r'grammar', r'vocabulary', r'reading', r'writing', r'listening'],
                'words': [r'\b[A-Za-z]{4,}\b', r'\b(the|and|that|have|for|not|with|you|this|but|his|from|they)\b'],
                'patterns': [r'[A-Z][a-z]+\s+[A-Z][a-z]+', r'\b[A-Za-z]+ed\b', r'\b[A-Za-z]+ing\b'],
                'structures': [r'\bWhat\s+(is|are|do|does)', r'\bHow\s+(many|much|long|old)', r'\bWhere\s+(is|are)'],
                'chinese_english': [r'英语', r'单词', r'语法', r'时态', r'句型', r'阅读理解', r'完形填空', r'英文']
            },
            '物理': {
                'primary': [r'力学', r'电学', r'光学', r'热学', r'声学', r'运动学'],
                'symbols': [r'\bF\s*=', r'\bv\s*=', r'\bs\s*=', r'牛顿', r'焦耳'],
                'concepts': [r'速度', r'加速度', r'质量', r'重力', r'摩擦力', r'电流', r'电压', r'电阻']
            },
            '化学': {
                'primary': [r'化学', r'反应', r'元素', r'分子', r'原子', r'离子'],
                'symbols': [r'[A-Z][a-z]?\d*', r'→', r'↑', r'↓', r'△'],
                'concepts': [r'氧化', r'还原', r'酸碱', r'盐', r'化合价', r'摩尔', r'溶液']
            },
            '生物': {
                'primary': [r'细胞', r'基因', r'DNA', r'RNA', r'蛋白质', r'酶'],
                'symbols': [r'ATP', r'CO₂', r'O₂', r'H₂O'],
                'concepts': [r'植物', r'动物', r'生态', r'进化', r'遗传', r'光合作用', r'呼吸作用']
            }
        }
        
        # 计算每个科目的匹配得分
        subject_scores = {}
        
        for subject, categories in subject_keywords.items():
            score = 0
            for category, keywords in categories.items():
                for keyword in keywords:
                    matches = len(re.findall(keyword, text, re.IGNORECASE))
                    if category == 'primary':
                        score += matches * 3  # 主要关键词权重更高
                    elif category == 'symbols':
                        score += matches * 2  # 符号类权重中等
                    else:
                        score += matches * 1  # 概念类基础权重
            subject_scores[subject] = score
        
        # 特殊的英语检测逻辑
        english_score = self._calculate_english_score(text)
        subject_scores['英语'] += english_score
        
        # 根据得分确定科目，允许多科目
        for subject, score in subject_scores.items():
            if score >= 2:  # 降低阈值，允许更敏感的检测
                subjects.append(subject)
        
        # 如果没有明确的科目指示，基于文本特征进行推断
        if not subjects:
            subjects = self._fallback_subject_detection(text)
        
        return subjects
    
    def _calculate_english_score(self, text: str) -> int:
        """专门计算英语内容得分"""
        score = 0
        
        # 英文单词密度
        english_words = re.findall(r'\b[A-Za-z]{2,}\b', text)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.replace(' ', ''))
        
        if total_chars > 0:
            english_ratio = len(''.join(english_words)) / total_chars
            if english_ratio > 0.3:  # 30%以上英文内容
                score += 5
            elif english_ratio > 0.1:  # 10-30%英文内容
                score += 3
        
        # 常见英语教学内容模式
        english_patterns = [
            r'\b(What|Where|When|Why|How)\b',  # 疑问词
            r'\b(is|are|was|were|am)\b',       # be动词
            r'\b(do|does|did|don\'t|doesn\'t|didn\'t)\b',  # 助动词
            r'\b(have|has|had)\b',             # have动词
            r'\b(will|would|can|could|should|may|might)\b',  # 情态动词
            r'\b[A-Z][a-z]+\b',                # 首字母大写的单词
            r'\b\w+ed\b',                      # 过去式
            r'\b\w+ing\b',                     # 现在分词
            r'\b(a|an|the)\b',                 # 冠词
        ]
        
        for pattern in english_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches
        
        # 中英混合教学内容
        mixed_patterns = [
            r'英语|English|英文',
            r'单词|word|词汇|vocabulary',
            r'语法|grammar',
            r'时态|tense',
            r'句型|sentence pattern',
            r'阅读理解|reading comprehension',
            r'完形填空|cloze test',
            r'选择题.*[ABCD]',  # 英语选择题模式
            r'翻译|translation|translate'
        ]
        
        for pattern in mixed_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 2
        
        return score
    
    def _fallback_subject_detection(self, text: str) -> List[str]:
        """后备科目检测方法"""
        subjects = []
        
        # 基于文本统计特征进行推断
        english_ratio = len(re.findall(r'[A-Za-z]', text)) / max(len(text), 1)
        digit_ratio = len(re.findall(r'\d', text)) / max(len(text), 1)
        chinese_ratio = len(re.findall(r'[\u4e00-\u9fff]', text)) / max(len(text), 1)
        
        # 如果英文字符比例较高
        if english_ratio > 0.2:
            subjects.append('英语')
        
        # 如果数字和符号较多
        if digit_ratio > 0.1 and any(op in text for op in ['+', '-', '×', '÷', '=']):
            subjects.append('数学')
        
        # 如果纯中文且包含文学性词汇
        if chinese_ratio > 0.8 and any(word in text for word in ['文章', '段落', '句子', '词语']):
            subjects.append('语文')
        
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
