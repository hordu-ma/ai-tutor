"""
错误分析相关的数据模型和枚举
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ErrorTypeEnum(str, Enum):
    """错误类型枚举"""
    # 数学错误类型
    CALCULATION_ERROR = "calculation_error"        # 计算错误
    CONCEPT_CONFUSION = "concept_confusion"        # 概念混淆
    FORMULA_MISUSE = "formula_misuse"             # 公式误用
    STEP_OMISSION = "step_omission"               # 步骤遗漏
    LOGICAL_ERROR = "logical_error"               # 逻辑错误

    # 物理错误类型
    UNIT_ERROR = "unit_error"                     # 单位错误
    PHYSICAL_PRINCIPLE = "physical_principle"      # 物理原理错误
    DIAGRAM_ANALYSIS = "diagram_analysis"          # 图像分析错误

    # 英语错误类型
    GRAMMAR_ERROR = "grammar_error"               # 语法错误
    VOCABULARY_ERROR = "vocabulary_error"         # 词汇错误
    SPELLING_ERROR = "spelling_error"             # 拼写错误
    EXPRESSION_ERROR = "expression_error"         # 表达错误

    # 通用错误类型
    READING_COMPREHENSION = "reading_comprehension"  # 理解错误
    CARELESS_MISTAKE = "careless_mistake"            # 粗心错误
    KNOWLEDGE_GAP = "knowledge_gap"                  # 知识缺陷
    METHOD_ERROR = "method_error"                    # 方法错误


class SeverityLevel(str, Enum):
    """错误严重程度"""
    LOW = "low"           # 轻微错误，偶发性
    MEDIUM = "medium"     # 中等错误，需要注意
    HIGH = "high"         # 严重错误，需要重点关注
    CRITICAL = "critical" # 关键错误，基础概念问题


class ErrorFrequency(str, Enum):
    """错误频率"""
    RARE = "rare"         # 罕见（<10%）
    OCCASIONAL = "occasional"  # 偶尔（10-30%）
    FREQUENT = "frequent"      # 频繁（30-60%）
    SYSTEMATIC = "systematic"   # 系统性（>60%）


# ============= 请求模型 =============

class ErrorAnalysisRequest(BaseModel):
    """错误分析请求"""
    student_id: int = Field(..., description="学生ID")
    subject: str = Field(..., description="科目")
    timeframe_days: Optional[int] = Field(30, description="分析时间范围（天）")
    include_recommendations: bool = Field(True, description="是否包含改进建议")





# ============= 响应模型 =============

class ErrorDetail(BaseModel):
    """具体错误详情"""
    error_type: ErrorTypeEnum = Field(..., description="错误类型")
    description: str = Field(..., description="错误描述")
    location: Optional[str] = Field(None, description="错误位置")
    severity: SeverityLevel = Field(..., description="严重程度")

    # 错误分析
    root_cause: str = Field(..., description="根本原因")
    typical_example: Optional[str] = Field(None, description="典型示例")

    # 改进建议
    correction_suggestion: str = Field(..., description="改正建议")
    practice_recommendation: Optional[str] = Field(None, description="练习建议")


class SystematicError(BaseModel):
    """系统性错误"""
    pattern_name: str = Field(..., description="错误模式名称")
    error_type: ErrorTypeEnum = Field(..., description="错误类型")
    frequency: ErrorFrequency = Field(..., description="出现频率")
    occurrence_count: int = Field(..., description="出现次数")
    total_opportunities: int = Field(..., description="总机会数")

    # 影响分析
    affected_knowledge_points: List[str] = Field(default_factory=list, description="影响的知识点")
    impact_score: float = Field(..., description="影响分数（0-1）")

    # 时间趋势
    first_occurrence: datetime = Field(..., description="首次出现时间")
    last_occurrence: datetime = Field(..., description="最近出现时间")
    trend: str = Field(..., description="变化趋势：improving/stable/worsening")

    # 详细分析
    details: List[ErrorDetail] = Field(default_factory=list, description="具体错误详情")


class ImprovementRecommendation(BaseModel):
    """改进建议"""
    priority: int = Field(..., description="优先级（1-5，5最高）")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="详细描述")

    # 具体行动
    action_items: List[str] = Field(default_factory=list, description="行动项目")
    estimated_time: Optional[str] = Field(None, description="预计完成时间")

    # 相关资源
    learning_resources: List[str] = Field(default_factory=list, description="学习资源")
    practice_exercises: List[str] = Field(default_factory=list, description="练习题目")

    # 成效预期
    expected_improvement: str = Field(..., description="预期改善效果")
    success_indicators: List[str] = Field(default_factory=list, description="成功指标")


class ErrorPatternAnalysis(BaseModel):
    """错误模式分析结果"""
    student_id: int = Field(..., description="学生ID")
    subject: str = Field(..., description="科目")
    analysis_period: str = Field(..., description="分析时间段")

    # 总体统计
    total_questions: int = Field(..., description="总题目数")
    total_errors: int = Field(..., description="总错误数")
    error_rate: float = Field(..., description="错误率")

    # 错误分类统计
    error_type_distribution: Dict[str, int] = Field(default_factory=dict, description="错误类型分布")
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="严重程度分布")

    # 系统性错误
    systematic_errors: List[SystematicError] = Field(default_factory=list, description="系统性错误列表")

    # 改进建议
    improvement_recommendations: List[ImprovementRecommendation] = Field(
        default_factory=list,
        description="改进建议"
    )

    # 进步评估
    progress_indicators: Dict[str, Any] = Field(default_factory=dict, description="进步指标")
    comparison_with_previous: Optional[Dict[str, float]] = Field(
        None,
        description="与上期对比"
    )

    # 元数据
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
    analysis_version: str = Field("1.0", description="分析算法版本")




class ErrorTrendAnalysis(BaseModel):
    """错误趋势分析"""
    student_id: int = Field(..., description="学生ID")
    subject: str = Field(..., description="科目")

    # 时间序列数据
    daily_error_rates: List[Dict[str, Any]] = Field(default_factory=list, description="每日错误率")
    weekly_summaries: List[Dict[str, Any]] = Field(default_factory=list, description="周度汇总")

    # 趋势指标
    overall_trend: str = Field(..., description="总体趋势")
    improvement_rate: float = Field(..., description="改进速度")
    regression_areas: List[str] = Field(default_factory=list, description="退步领域")

    # 预测
    predicted_mastery_time: Optional[int] = Field(None, description="预计掌握时间（天）")
    risk_assessment: str = Field(..., description="风险评估")
