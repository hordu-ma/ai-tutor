"""
English-related schemas for the AI Tutor system.

This module defines Pydantic models and enums specific to English questions,
grammar analysis, vocabulary assessment, and writing evaluation.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EnglishCategory(str, Enum):
    """
    Enumeration of English knowledge categories.
    """
    GRAMMAR = "语法"
    VOCABULARY = "词汇"
    READING_COMPREHENSION = "阅读理解"
    WRITING = "写作"
    LISTENING = "听力"
    SPEAKING = "口语"


class EnglishQuestionType(str, Enum):
    """
    Enumeration of English question types.
    """
    MULTIPLE_CHOICE = "选择题"
    FILL_IN_BLANK = "填空题"
    CLOZE_TEST = "完形填空"
    READING_COMPREHENSION = "阅读理解"
    TRANSLATION = "翻译题"
    WRITING = "写作题"
    GRAMMAR_CORRECTION = "改错题"
    VOCABULARY_EXERCISE = "词汇题"


class GrammarPointType(str, Enum):
    """
    Enumeration of grammar knowledge points.
    """
    # 时态类
    SIMPLE_PRESENT = "一般现在时"
    SIMPLE_PAST = "一般过去时"
    SIMPLE_FUTURE = "一般将来时"
    PRESENT_CONTINUOUS = "现在进行时"
    PAST_CONTINUOUS = "过去进行时"
    PRESENT_PERFECT = "现在完成时"
    PAST_PERFECT = "过去完成时"
    
    # 句型结构
    DECLARATIVE_SENTENCE = "陈述句"
    INTERROGATIVE_SENTENCE = "疑问句"
    IMPERATIVE_SENTENCE = "祈使句"
    EXCLAMATORY_SENTENCE = "感叹句"
    ATTRIBUTIVE_CLAUSE = "定语从句"
    ADVERBIAL_CLAUSE = "状语从句"
    OBJECT_CLAUSE = "宾语从句"
    SUBJECT_CLAUSE = "主语从句"
    
    # 词性语法
    NOUN_USAGE = "名词用法"
    PRONOUN_USAGE = "代词用法"
    VERB_USAGE = "动词用法"
    ADJECTIVE_USAGE = "形容词用法"
    ADVERB_USAGE = "副词用法"
    PREPOSITION_USAGE = "介词用法"
    CONJUNCTION_USAGE = "连词用法"
    ARTICLE_USAGE = "冠词用法"
    
    # 语态
    ACTIVE_VOICE = "主动语态"
    PASSIVE_VOICE = "被动语态"
    
    # 其他语法点
    SUBJUNCTIVE_MOOD = "虚拟语气"
    COMPARATIVE_DEGREE = "比较级"
    SUPERLATIVE_DEGREE = "最高级"
    INFINITIVE = "不定式"
    GERUND = "动名词"
    PARTICIPLE = "分词"


class VocabularyLevel(str, Enum):
    """
    Enumeration of vocabulary difficulty levels.
    """
    BASIC = "基础"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    ACADEMIC = "学术"


class WritingType(str, Enum):
    """
    Enumeration of writing types.
    """
    NARRATIVE = "记叙文"
    DESCRIPTIVE = "说明文"
    ARGUMENTATIVE = "议论文"
    PRACTICAL = "应用文"
    CREATIVE = "创意写作"
    DIARY = "日记"
    LETTER = "书信"
    EMAIL = "邮件"
    REPORT = "报告"
    ESSAY = "议论文"


class ErrorType(str, Enum):
    """
    Enumeration of common English errors.
    """
    # 语法错误
    TENSE_ERROR = "时态错误"
    VOICE_ERROR = "语态错误"
    SUBJECT_VERB_AGREEMENT = "主谓一致错误"
    SENTENCE_STRUCTURE = "句子结构错误"
    WORD_ORDER = "词序错误"
    
    # 词汇错误
    WORD_CHOICE = "词汇选择错误"
    COLLOCATION_ERROR = "搭配错误"
    SPELLING_ERROR = "拼写错误"
    
    # 语篇错误
    COHERENCE_ERROR = "连贯性错误"
    COHESION_ERROR = "衔接错误"
    LOGIC_ERROR = "逻辑错误"
    
    # 格式错误
    PUNCTUATION_ERROR = "标点符号错误"
    CAPITALIZATION_ERROR = "大小写错误"
    FORMAT_ERROR = "格式错误"


class GrammarError(BaseModel):
    """
    Schema for grammar error analysis.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    error_type: ErrorType = Field(..., description="错误类型")
    error_text: str = Field(..., description="错误文本片段")
    correct_text: str = Field(..., description="正确的表达方式")
    explanation: str = Field(..., description="错误解释")
    grammar_point: GrammarPointType = Field(..., description="相关语法点")
    severity: int = Field(..., ge=1, le=3, description="错误严重程度 (1-轻微, 2-中等, 3-严重)")


class VocabularyAssessment(BaseModel):
    """
    Schema for vocabulary usage assessment.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    word: str = Field(..., description="词汇")
    level: VocabularyLevel = Field(..., description="词汇难度等级")
    appropriateness: float = Field(..., ge=0, le=1, description="使用恰当性 (0-1)")
    alternatives: List[str] = Field(default_factory=list, description="替代词汇建议")
    context_score: float = Field(..., ge=0, le=1, description="语境适配度 (0-1)")


class WritingQuality(BaseModel):
    """
    Schema for writing quality assessment.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    content_score: float = Field(..., ge=0, le=1, description="内容得分 (0-1)")
    organization_score: float = Field(..., ge=0, le=1, description="组织结构得分 (0-1)")
    language_score: float = Field(..., ge=0, le=1, description="语言表达得分 (0-1)")
    mechanics_score: float = Field(..., ge=0, le=1, description="语言规范得分 (0-1)")
    creativity_score: Optional[float] = Field(None, ge=0, le=1, description="创意得分 (0-1)")
    
    strengths: List[str] = Field(default_factory=list, description="写作优势")
    weaknesses: List[str] = Field(default_factory=list, description="需要改进的地方")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")


class LanguageFeatures(BaseModel):
    """
    Schema for language feature analysis.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    sentence_count: int = Field(..., ge=0, description="句子数量")
    avg_sentence_length: float = Field(..., ge=0, description="平均句长")
    vocabulary_diversity: float = Field(..., ge=0, le=1, description="词汇多样性 (0-1)")
    grammar_complexity: float = Field(..., ge=0, le=1, description="语法复杂度 (0-1)")
    readability_score: float = Field(..., ge=0, le=1, description="可读性得分 (0-1)")
    
    tense_usage: Dict[str, int] = Field(default_factory=dict, description="时态使用统计")
    sentence_types: Dict[str, int] = Field(default_factory=dict, description="句型类型统计")
    error_patterns: Dict[str, int] = Field(default_factory=dict, description="错误模式统计")


class EnglishQuestion(BaseModel):
    """
    Schema for an English question.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    text: str = Field(..., description="题目文本内容")
    question_type: EnglishQuestionType = Field(..., description="题目类型")
    category: EnglishCategory = Field(..., description="英语分类")
    grammar_points: List[GrammarPointType] = Field(
        default_factory=list, description="涉及的语法点"
    )
    vocabulary_level: VocabularyLevel = Field(..., description="词汇难度等级")
    difficulty_level: Optional[int] = Field(
        None, ge=1, le=5, description="难度等级 (1-5)"
    )
    answer: Optional[str] = Field(None, description="参考答案")
    explanation: Optional[str] = Field(None, description="解题思路")
    materials: Optional[Dict[str, Any]] = Field(None, description="相关材料（如阅读材料）")


class EnglishGradingResult(BaseModel):
    """
    Schema for English question grading results.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    question: EnglishQuestion = Field(..., description="题目信息")
    student_answer: str = Field(..., description="学生答案")
    is_correct: bool = Field(..., description="是否正确")
    score: float = Field(..., ge=0, le=100, description="得分 (0-100)")
    
    # 语法分析
    grammar_accuracy: float = Field(..., ge=0, le=1, description="语法准确性 (0-1)")
    grammar_errors: List[GrammarError] = Field(default_factory=list, description="语法错误详情")
    
    # 词汇评估
    vocabulary_appropriateness: float = Field(..., ge=0, le=1, description="词汇恰当性 (0-1)")
    vocabulary_assessment: List[VocabularyAssessment] = Field(
        default_factory=list, description="词汇使用评估"
    )
    
    # 写作质量（适用于写作题）
    writing_quality: Optional[WritingQuality] = Field(None, description="写作质量评估")
    
    # 语言特征分析
    language_features: Optional[LanguageFeatures] = Field(None, description="语言特征分析")
    
    # 整体评价
    fluency_score: float = Field(..., ge=0, le=1, description="流畅性得分 (0-1)")
    coherence_score: float = Field(..., ge=0, le=1, description="连贯性得分 (0-1)")
    
    feedback: str = Field(..., description="批改反馈")
    improvement_suggestions: List[str] = Field(
        default_factory=list, description="改进建议"
    )
    knowledge_gaps: List[GrammarPointType] = Field(
        default_factory=list, description="知识薄弱点"
    )


class EnglishHomeworkSession(BaseModel):
    """
    Schema for an English homework grading session.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    session_id: str = Field(..., description="批改会话ID")
    student_id: Optional[str] = Field(None, description="学生ID")
    questions: List[EnglishGradingResult] = Field(
        default_factory=list, description="题目批改结果"
    )
    overall_score: float = Field(..., ge=0, le=100, description="总体得分")
    completion_time: Optional[float] = Field(
        None, description="完成时间（分钟）"
    )
    
    # 整体语言能力评估
    overall_grammar_accuracy: float = Field(..., ge=0, le=1, description="整体语法准确性")
    overall_vocabulary_level: VocabularyLevel = Field(..., description="整体词汇水平")
    overall_fluency: float = Field(..., ge=0, le=1, description="整体流畅性")
    overall_coherence: float = Field(..., ge=0, le=1, description="整体连贯性")
    
    # 薄弱环节分析
    weak_grammar_points: List[GrammarPointType] = Field(
        default_factory=list, description="薄弱语法点"
    )
    weak_categories: List[EnglishCategory] = Field(
        default_factory=list, description="薄弱知识领域"
    )
    common_error_types: List[ErrorType] = Field(
        default_factory=list, description="常见错误类型"
    )
    
    # 学习建议
    recommendations: List[str] = Field(
        default_factory=list, description="学习建议"
    )
    study_focus: List[str] = Field(
        default_factory=list, description="学习重点"
    )
    practice_suggestions: List[str] = Field(
        default_factory=list, description="练习建议"
    )


class EnglishLearningReport(BaseModel):
    """
    Schema for comprehensive English learning report.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    student_id: str = Field(..., description="学生ID")
    report_period: str = Field(..., description="报告周期")
    total_sessions: int = Field(..., ge=0, description="总作业次数")
    
    # 进步追踪
    grammar_progress: Dict[str, float] = Field(default_factory=dict, description="语法进步追踪")
    vocabulary_progress: Dict[str, float] = Field(default_factory=dict, description="词汇进步追踪")
    writing_progress: Dict[str, float] = Field(default_factory=dict, description="写作进步追踪")
    
    # 强项和弱项
    strengths: List[str] = Field(default_factory=list, description="学习优势")
    challenges: List[str] = Field(default_factory=list, description="学习挑战")
    
    # 个性化建议
    personalized_recommendations: List[str] = Field(
        default_factory=list, description="个性化学习建议"
    )
    next_learning_goals: List[str] = Field(
        default_factory=list, description="下阶段学习目标"
    )


# Knowledge point mapping for easy lookup
ENGLISH_KNOWLEDGE_MAPPING = {
    EnglishCategory.GRAMMAR: [
        GrammarPointType.SIMPLE_PRESENT,
        GrammarPointType.SIMPLE_PAST,
        GrammarPointType.SIMPLE_FUTURE,
        GrammarPointType.PRESENT_CONTINUOUS,
        GrammarPointType.PAST_CONTINUOUS,
        GrammarPointType.PRESENT_PERFECT,
        GrammarPointType.PAST_PERFECT,
        GrammarPointType.ACTIVE_VOICE,
        GrammarPointType.PASSIVE_VOICE,
        GrammarPointType.SUBJUNCTIVE_MOOD,
    ],
    EnglishCategory.VOCABULARY: [
        # 词汇相关的语法点
        GrammarPointType.NOUN_USAGE,
        GrammarPointType.PRONOUN_USAGE,
        GrammarPointType.VERB_USAGE,
        GrammarPointType.ADJECTIVE_USAGE,
        GrammarPointType.ADVERB_USAGE,
        GrammarPointType.PREPOSITION_USAGE,
        GrammarPointType.CONJUNCTION_USAGE,
        GrammarPointType.ARTICLE_USAGE,
    ],
    EnglishCategory.WRITING: [
        GrammarPointType.DECLARATIVE_SENTENCE,
        GrammarPointType.INTERROGATIVE_SENTENCE,
        GrammarPointType.IMPERATIVE_SENTENCE,
        GrammarPointType.EXCLAMATORY_SENTENCE,
        GrammarPointType.ATTRIBUTIVE_CLAUSE,
        GrammarPointType.ADVERBIAL_CLAUSE,
        GrammarPointType.OBJECT_CLAUSE,
        GrammarPointType.SUBJECT_CLAUSE,
    ],
    EnglishCategory.READING_COMPREHENSION: [
        # 阅读理解相关的语法点
        GrammarPointType.ATTRIBUTIVE_CLAUSE,
        GrammarPointType.ADVERBIAL_CLAUSE,
        GrammarPointType.INFINITIVE,
        GrammarPointType.GERUND,
        GrammarPointType.PARTICIPLE,
    ],
}


# Common error patterns for analysis
COMMON_ERROR_PATTERNS = {
    ErrorType.TENSE_ERROR: [
        "动词时态与时间状语不符",
        "时态前后不一致",
        "情态动词后时态错误"
    ],
    ErrorType.SUBJECT_VERB_AGREEMENT: [
        "主语为第三人称单数时动词形式错误",
        "主语为复数时动词形式错误",
        "倒装句中主谓一致错误"
    ],
    ErrorType.WORD_CHOICE: [
        "近义词使用错误",
        "词性选择错误",
        "语域不当"
    ],
    ErrorType.SENTENCE_STRUCTURE: [
        "缺少主语或谓语",
        "句子成分残缺",
        "句式杂糅"
    ]
}
