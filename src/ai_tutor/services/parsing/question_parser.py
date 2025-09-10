"""
题目解析器 - 处理题目识别和结构化解析
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from ...core.logger import LoggerMixin


class QuestionType(Enum):
    """题目类型枚举"""
    MULTIPLE_CHOICE = "multiple_choice"    # 选择题
    FILL_IN_BLANK = "fill_in_blank"       # 填空题
    TRUE_FALSE = "true_false"             # 判断题
    SHORT_ANSWER = "short_answer"         # 简答题
    CALCULATION = "calculation"           # 计算题
    PROOF = "proof"                       # 证明题
    UNKNOWN = "unknown"                   # 未知类型


@dataclass
class AnswerRegion:
    """答案区域数据结构"""
    start_pos: int
    end_pos: int
    content: str
    confidence: float
    answer_type: str  # "handwritten", "printed", "mixed"


@dataclass
class ParsedQuestion:
    """解析后的题目数据结构"""
    question_number: int
    question_text: str
    question_type: QuestionType
    answer_regions: List[AnswerRegion]
    student_answer: str
    raw_text: str
    confidence: float
    metadata: Dict[str, Any]


class QuestionParser(LoggerMixin):
    """题目解析器 - 识别和结构化解析题目"""
    
    def __init__(self):
        # 题目编号识别模式
        self.question_number_patterns = [
            r'(\d+)\s*[\.。]',                    # 1. 2. 3.
            r'(\d+)\s*[、,]',                    # 1、2、3、
            r'\((\d+)\)',                        # (1) (2) (3)
            r'（(\d+)）',                        # （1）（2）（3）
            r'第\s*([一二三四五六七八九十\d]+)\s*[题道]',  # 第一题 第二道
            r'([一二三四五六七八九十]+)[、.]',      # 一、二、三、
            r'([ABCD])\s*[\.。]',                # A. B. C. D.
            r'题目\s*(\d+)',                     # 题目1 题目2
        ]
        
        # 题目类型识别模式
        self.question_type_patterns = {
            QuestionType.MULTIPLE_CHOICE: [
                r'[ABCD][.、）)].*?[ABCD][.、）)]',
                r'选择.*?答案',
                r'下列.*?正确.*?是',
                r'以下.*?选项'
            ],
            QuestionType.FILL_IN_BLANK: [
                r'___+',
                r'填空',
                r'括号内',
                r'\(\s*\)',
                r'空白处'
            ],
            QuestionType.TRUE_FALSE: [
                r'判断.*?对错',
                r'正确.*?错误',
                r'对.*?错',
                r'√.*?×'
            ],
            QuestionType.CALCULATION: [
                r'计算',
                r'求.*?值',
                r'解.*?方程',
                r'=.*?\?',
                r'\d+\s*[+\-×÷]\s*\d+'
            ],
            QuestionType.PROOF: [
                r'证明',
                r'求证',
                r'试证',
                r'证：'
            ]
        }
        
        # 答案区域识别模式
        self.answer_region_patterns = [
            r'答案?[:：]\s*(.{1,100})',
            r'解[:：]\s*(.{1,200})',
            r'[学生]答[:：]?\s*(.{1,100})',
            r'答题[:：]?\s*(.{1,100})',
            r'[手写|笔迹|学生字迹][:：]?\s*(.{1,100})',
        ]
    
    def parse_questions(self, text: str) -> List[ParsedQuestion]:
        """解析OCR文本中的所有题目"""
        self.log_event("开始解析题目", text_length=len(text))
        
        # 预处理文本
        cleaned_text = self._preprocess_text(text)
        
        # 分割题目
        question_segments = self._segment_questions(cleaned_text)
        
        parsed_questions = []
        for i, segment in enumerate(question_segments):
            try:
                question = self._parse_single_question(segment, i + 1)
                if question:
                    parsed_questions.append(question)
            except Exception as e:
                self.log_warning(f"解析第{i+1}题失败", error=str(e), segment=segment[:100])
                continue
        
        self.log_event("题目解析完成", total_questions=len(parsed_questions))
        return parsed_questions
    
    def _preprocess_text(self, text: str) -> str:
        """预处理OCR文本"""
        # 统一换行符
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # 清理连续的空白字符
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 修复常见OCR错误
        ocr_fixes = {
            '0': 'O',  # 数字0误识别为字母O的情况
            'o': '0',  # 字母o误识别为数字0的情况
            '1': 'l',  # 数字1误识别为字母l的情况
            '5': 'S',  # 数字5误识别为字母S的情况
        }
        
        # 应用OCR修复（谨慎使用，避免误修复）
        # 这里只修复明显的模式
        text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)  # 数字中间的O修复为0
        text = re.sub(r'(?<=题目)\s*[Oo]', '0', text)    # 题目O修复为0
        
        return text.strip()
    
    def _segment_questions(self, text: str) -> List[str]:
        """将文本分割为独立的题目段落"""
        segments = []
        
        # 尝试按题目编号分割
        question_splits = []
        for pattern in self.question_number_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                question_splits.append((match.start(), match.group(0), match.group(1)))
        
        # 按位置排序
        question_splits.sort(key=lambda x: x[0])
        
        if not question_splits:
            # 没有找到明确的题目编号，按段落分割
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            return paragraphs[:5]  # 最多返回5个段落
        
        # 根据题目分割点提取内容
        for i, (start_pos, marker, number) in enumerate(question_splits):
            if i + 1 < len(question_splits):
                end_pos = question_splits[i + 1][0]
                segment = text[start_pos:end_pos].strip()
            else:
                segment = text[start_pos:].strip()
            
            if len(segment) > 10:  # 过滤太短的段落
                segments.append(segment)
        
        return segments
    
    def _parse_single_question(self, segment: str, default_number: int) -> Optional[ParsedQuestion]:
        """解析单个题目"""
        # 提取题目编号
        question_number = self._extract_question_number(segment) or default_number
        
        # 识别题目类型
        question_type = self._identify_question_type(segment)
        
        # 提取题目文本（去掉编号部分）
        question_text = self._extract_question_text(segment)
        
        # 识别答案区域
        answer_regions = self._identify_answer_regions(segment)
        
        # 提取学生答案
        student_answer = self._extract_student_answer(segment, answer_regions)
        
        # 计算解析置信度
        confidence = self._calculate_confidence(segment, question_type, answer_regions)
        
        return ParsedQuestion(
            question_number=question_number,
            question_text=question_text,
            question_type=question_type,
            answer_regions=answer_regions,
            student_answer=student_answer,
            raw_text=segment,
            confidence=confidence,
            metadata={
                "segment_length": len(segment),
                "answer_regions_count": len(answer_regions),
                "type_detection_method": "pattern_matching"
            }
        )
    
    def _extract_question_number(self, text: str) -> Optional[int]:
        """提取题目编号"""
        for pattern in self.question_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number_str = match.group(1)
                try:
                    # 处理中文数字
                    if number_str in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
                        chinese_numbers = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                                         '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                        return chinese_numbers.get(number_str)
                    else:
                        return int(number_str)
                except ValueError:
                    continue
        return None
    
    def _identify_question_type(self, text: str) -> QuestionType:
        """识别题目类型"""
        text_lower = text.lower()
        
        # 计算每种类型的匹配分数
        type_scores = {}
        for q_type, patterns in self.question_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            type_scores[q_type] = score
        
        # 返回得分最高的类型
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            if best_type[1] > 0:
                return best_type[0]
        
        # 基于内容特征的启发式判断
        if '?' in text or '？' in text:
            if any(op in text for op in ['+', '-', '×', '÷', '=', '²', '³']):
                return QuestionType.CALCULATION
            else:
                return QuestionType.SHORT_ANSWER
        
        return QuestionType.UNKNOWN
    
    def _extract_question_text(self, segment: str) -> str:
        """提取题目文本（移除编号和答案部分）"""
        text = segment
        
        # 移除题目编号
        for pattern in self.question_number_patterns:
            text = re.sub(pattern, '', text, count=1)
        
        # 移除答案部分
        for pattern in self.answer_region_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 限制长度
        if len(text) > 300:
            text = text[:300] + "..."
        
        return text
    
    def _identify_answer_regions(self, text: str) -> List[AnswerRegion]:
        """识别答案区域"""
        regions = []
        
        for pattern in self.answer_region_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start_pos = match.start(1)  # 答案内容的开始位置
                end_pos = match.end(1)      # 答案内容的结束位置
                content = match.group(1).strip()
                
                if len(content) > 0:
                    # 估算置信度
                    confidence = self._calculate_answer_confidence(content)
                    
                    # 判断答案类型
                    answer_type = self._classify_answer_type(content)
                    
                    region = AnswerRegion(
                        start_pos=start_pos,
                        end_pos=end_pos,
                        content=content,
                        confidence=confidence,
                        answer_type=answer_type
                    )
                    regions.append(region)
        
        return regions
    
    def _extract_student_answer(self, text: str, answer_regions: List[AnswerRegion]) -> str:
        """提取学生答案"""
        if answer_regions:
            # 选择置信度最高的答案区域
            best_region = max(answer_regions, key=lambda r: r.confidence)
            return best_region.content
        
        # 如果没有识别到明确的答案区域，尝试从文本中提取可能的答案
        possible_answers = []
        
        # 查找数字答案
        number_matches = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if number_matches:
            possible_answers.extend(number_matches[-2:])  # 取最后几个数字
        
        # 查找字母答案（选择题）
        letter_matches = re.findall(r'\b[ABCD]\b', text)
        if letter_matches:
            possible_answers.extend(letter_matches)
        
        return ', '.join(possible_answers[:3]) if possible_answers else "未识别到答案"
    
    def _calculate_confidence(self, segment: str, question_type: QuestionType, 
                           answer_regions: List[AnswerRegion]) -> float:
        """计算解析置信度"""
        confidence = 0.5  # 基础置信度
        
        # 题目类型识别加分
        if question_type != QuestionType.UNKNOWN:
            confidence += 0.2
        
        # 答案区域加分
        if answer_regions:
            avg_answer_confidence = sum(r.confidence for r in answer_regions) / len(answer_regions)
            confidence += avg_answer_confidence * 0.3
        
        # 文本长度合理性加分
        if 20 <= len(segment) <= 500:
            confidence += 0.1
        
        # 包含关键词加分
        key_indicators = ['题', '问', '求', '计算', '?', '？', '=']
        if any(indicator in segment for indicator in key_indicators):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_answer_confidence(self, content: str) -> float:
        """计算答案内容的置信度"""
        confidence = 0.3
        
        # 长度合理性
        if 1 <= len(content) <= 50:
            confidence += 0.3
        elif len(content) > 50:
            confidence -= 0.2
        
        # 包含数字或字母
        if re.search(r'[0-9A-Za-z]', content):
            confidence += 0.2
        
        # 避免过长的描述性文本
        if len(content.split()) > 10:
            confidence -= 0.3
        
        return max(0.1, min(confidence, 1.0))
    
    def _classify_answer_type(self, content: str) -> str:
        """分类答案类型"""
        if re.match(r'^[0-9\.\+\-\×\÷\=\s]+$', content):
            return "mathematical"
        elif re.match(r'^[A-Za-z]+$', content):
            return "alphabetic"
        elif len(content) < 10 and not ' ' in content:
            return "short_answer"
        else:
            return "descriptive"


# 便捷函数
def parse_homework_text(text: str) -> List[ParsedQuestion]:
    """便捷函数：解析作业文本"""
    parser = QuestionParser()
    return parser.parse_questions(text)
