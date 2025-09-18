"""
错误分析服务 - ErrorPatternService

提供学生错误模式分析、系统性错误识别和改进建议生成功能。
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import re
import json

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..db.database import get_db
from ..models.student import Student
from ..models.homework import Question, HomeworkSession, SubjectEnum
from ..models.knowledge import KnowledgeProgress, KnowledgePoint, ErrorPattern
from ..schemas.error_analysis import (
    ErrorPatternAnalysis,
    SystematicError,
    ErrorDetail,
    ImprovementRecommendation,
    ErrorTrendAnalysis,
    ErrorTypeEnum,
    SeverityLevel,
    ErrorFrequency
)

logger = logging.getLogger(__name__)


class ErrorClassifier:
    """错误分类器 - 分析和分类不同类型的错误"""

    def __init__(self):
        # 数学错误识别模式
        self.math_patterns = {
            ErrorTypeEnum.CALCULATION_ERROR: [
                r'计算.*错误', r'算.*错', r'加减乘除', r'运算.*错误'
            ],
            ErrorTypeEnum.FORMULA_MISUSE: [
                r'公式.*错误', r'公式.*用错', r'套用.*错误', r'公式.*不当'
            ],
            ErrorTypeEnum.CONCEPT_CONFUSION: [
                r'概念.*混淆', r'概念.*错误', r'理解.*错误', r'概念.*不清'
            ],
            ErrorTypeEnum.LOGICAL_ERROR: [
                r'逻辑.*错误', r'推理.*错误', r'思路.*错误', r'逻辑.*不当'
            ],
            ErrorTypeEnum.STEP_OMISSION: [
                r'步骤.*遗漏', r'缺少.*步骤', r'跳步', r'步骤.*不完整'
            ]
        }

        # 物理错误识别模式
        self.physics_patterns = {
            ErrorTypeEnum.UNIT_ERROR: [
                r'单位.*错误', r'量纲.*错误', r'单位.*不统一', r'单位.*转换'
            ],
            ErrorTypeEnum.PHYSICAL_PRINCIPLE: [
                r'物理.*原理', r'定律.*应用', r'原理.*错误', r'定律.*错误'
            ],
            ErrorTypeEnum.DIAGRAM_ANALYSIS: [
                r'图.*分析', r'图像.*错误', r'图表.*理解', r'图形.*分析'
            ]
        }

        # 英语错误识别模式
        self.english_patterns = {
            ErrorTypeEnum.GRAMMAR_ERROR: [
                r'语法.*错误', r'时态.*错误', r'语法.*不当', r'句法.*错误'
            ],
            ErrorTypeEnum.VOCABULARY_ERROR: [
                r'词汇.*错误', r'单词.*用错', r'词汇.*选择', r'用词.*不当'
            ],
            ErrorTypeEnum.SPELLING_ERROR: [
                r'拼写.*错误', r'单词.*拼写', r'字母.*错误', r'拼写.*错误'
            ]
        }

    def classify_error(self, question: Question, error_text: str, subject: str) -> List[ErrorTypeEnum]:
        """分类错误类型"""
        error_types = []

        if subject == "math":
            error_types.extend(self._match_patterns(error_text, self.math_patterns))
        elif subject == "physics":
            error_types.extend(self._match_patterns(error_text, self.physics_patterns))
        elif subject == "english":
            error_types.extend(self._match_patterns(error_text, self.english_patterns))

        # 如果没有匹配到具体类型，且是已知科目，分析答案差异
        if not error_types and subject in ["math", "physics", "english"]:
            error_types.extend(self._analyze_answer_difference(question))

        # 默认返回通用错误类型
        return error_types if error_types else [ErrorTypeEnum.KNOWLEDGE_GAP]

    def _match_patterns(self, text: str, patterns: Dict) -> List[ErrorTypeEnum]:
        """匹配错误模式"""
        matches = []
        for error_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(error_type)
                    break
        return matches

    def _analyze_answer_difference(self, question: Question) -> List[ErrorTypeEnum]:
        """分析答案差异来推断错误类型"""
        if not hasattr(question, 'student_answer') or not hasattr(question, 'correct_answer'):
            return []

        if not question.student_answer or not question.correct_answer:
            return []

        student_ans = str(question.student_answer).strip()
        correct_ans = str(question.correct_answer).strip()

        # 简单的启发式规则
        if self._looks_like_calculation_error(student_ans, correct_ans):
            return [ErrorTypeEnum.CALCULATION_ERROR]
        elif self._looks_like_careless_mistake(student_ans, correct_ans):
            return [ErrorTypeEnum.CARELESS_MISTAKE]
        else:
            return []

    def _looks_like_calculation_error(self, student: str, correct: str) -> bool:
        """检查是否像计算错误"""
        # 提取数字进行比较
        student_nums = re.findall(r'-?\d+\.?\d*', student)
        correct_nums = re.findall(r'-?\d+\.?\d*', correct)

        return len(student_nums) == len(correct_nums) and student_nums != correct_nums

    def _looks_like_careless_mistake(self, student: str, correct: str) -> bool:
        """检查是否像粗心错误"""
        # 字符相似度较高，可能是粗心
        if len(student) > 0 and len(correct) > 0:
            common_chars = set(student.lower()) & set(correct.lower())
            similarity = len(common_chars) / max(len(set(student.lower())), len(set(correct.lower())))
            return similarity > 0.7
        return False


class ErrorPatternService:
    """错误模式分析服务"""

    def __init__(self, db: Session):
        self.db = db
        self.classifier = ErrorClassifier()

    async def analyze_student_error_patterns(
        self,
        student_id: int,
        subject: str,
        timeframe_days: int = 30
    ) -> ErrorPatternAnalysis:
        """分析学生错误模式"""
        logger.info(f"开始分析学生 {student_id} 的 {subject} 错误模式，时间范围: {timeframe_days}天")

        # 获取时间范围内的问题数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=timeframe_days)

        questions = self._get_student_questions(student_id, subject, start_date, end_date)

        if not questions:
            logger.warning(f"学生 {student_id} 在指定时间范围内没有 {subject} 题目记录")
            return self._create_empty_analysis(student_id, subject, timeframe_days)

        # 统计基础信息
        total_questions = len(questions)
        incorrect_questions = [q for q in questions if not q.is_correct]
        total_errors = len(incorrect_questions)
        error_rate = total_errors / total_questions if total_questions > 0 else 0

        # 分析错误类型分布
        error_type_distribution = self._analyze_error_type_distribution(incorrect_questions, subject)
        severity_distribution = self._analyze_severity_distribution(incorrect_questions, subject)

        # 识别系统性错误
        systematic_errors = self._identify_systematic_errors(incorrect_questions, subject)

        # 生成改进建议
        recommendations = self._generate_improvement_recommendations(
            systematic_errors, error_type_distribution, subject
        )

        # 分析进步指标
        progress_indicators = self._calculate_progress_indicators(
            student_id, subject, questions
        )

        return ErrorPatternAnalysis(
            student_id=student_id,
            subject=subject,
            analysis_period=f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            total_questions=total_questions,
            total_errors=total_errors,
            error_rate=round(error_rate, 3),
            error_type_distribution=error_type_distribution,
            severity_distribution=severity_distribution,
            systematic_errors=systematic_errors,
            improvement_recommendations=recommendations,
            progress_indicators=progress_indicators
        )



    async def get_error_trends(
        self,
        student_id: int,
        subject: str,
        days: int = 30
    ) -> ErrorTrendAnalysis:
        """获取错误趋势分析"""
        logger.info(f"分析学生 {student_id} 的 {subject} 错误趋势，{days}天")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 获取每日数据
        daily_data = self._get_daily_error_data(student_id, subject, start_date, end_date)
        weekly_data = self._aggregate_weekly_data(daily_data)

        # 计算趋势指标
        overall_trend = self._calculate_overall_trend(daily_data)
        improvement_rate = self._calculate_improvement_rate(daily_data)

        return ErrorTrendAnalysis(
            student_id=student_id,
            subject=subject,
            daily_error_rates=daily_data,
            weekly_summaries=weekly_data,
            overall_trend=overall_trend,
            improvement_rate=improvement_rate,
            regression_areas=[],  # 简化实现
            predicted_mastery_time=None,
            risk_assessment="中等"
        )

    # ============= 私有方法 =============

    def _get_student_questions(
        self,
        student_id: int,
        subject: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Question]:
        """获取学生在指定时间范围内的题目"""
        return (
            self.db.query(Question)
            .join(HomeworkSession)
            .filter(
                HomeworkSession.student_id == student_id,
                HomeworkSession.subject == subject,
                HomeworkSession.created_at >= start_date,
                HomeworkSession.created_at <= end_date
            )
            .all()
        )

    def _analyze_error_type_distribution(
        self,
        questions: List[Question],
        subject: str
    ) -> Dict[str, int]:
        """分析错误类型分布"""
        distribution = defaultdict(int)

        for question in questions:
            error_text = question.error_analysis or ""
            error_types = self.classifier.classify_error(question, error_text, subject)

            for error_type in error_types:
                distribution[error_type.value] += 1

        return dict(distribution)

    def _analyze_severity_distribution(
        self,
        questions: List[Question],
        subject: str
    ) -> Dict[str, int]:
        """分析严重程度分布"""
        distribution = defaultdict(int)

        for question in questions:
            severity = self._determine_error_severity(question, subject)
            distribution[severity.value] += 1

        return dict(distribution)

    def _determine_error_severity(self, question: Question, subject: str) -> SeverityLevel:
        """确定错误严重程度"""
        # 简化的严重程度判断逻辑
        if question.difficulty_level and question.difficulty_level <= 2:
            return SeverityLevel.HIGH  # 简单题目错误较严重
        elif question.difficulty_level and question.difficulty_level >= 4:
            return SeverityLevel.LOW   # 难题错误较正常
        else:
            return SeverityLevel.MEDIUM

    def _identify_systematic_errors(
        self,
        questions: List[Question],
        subject: str
    ) -> List[SystematicError]:
        """识别系统性错误"""
        # 按错误类型分组
        error_groups = defaultdict(list)

        for question in questions:
            error_text = question.error_analysis or ""
            error_types = self.classifier.classify_error(question, error_text, subject)

            for error_type in error_types:
                error_groups[error_type].append(question)

        systematic_errors = []
        total_questions = len(questions)

        for error_type, error_questions in error_groups.items():
            occurrence_count = len(error_questions)
            frequency_rate = occurrence_count / total_questions

            # 判断是否为系统性错误（出现频率 > 30% 且总题数 > 3）
            if frequency_rate > 0.3 and total_questions > 3:
                frequency = self._determine_error_frequency(frequency_rate)

                systematic_error = SystematicError(
                    pattern_name=f"{subject}_{error_type.value}",
                    error_type=error_type,
                    frequency=frequency,
                    occurrence_count=occurrence_count,
                    total_opportunities=total_questions,
                    impact_score=round(frequency_rate, 2),
                    first_occurrence=min(q.created_at for q in error_questions),
                    last_occurrence=max(q.created_at for q in error_questions),
                    trend="stable",  # 简化实现
                    affected_knowledge_points=[],
                    details=[]
                )

                systematic_errors.append(systematic_error)

        return systematic_errors

    def _determine_error_frequency(self, rate: float) -> ErrorFrequency:
        """确定错误频率级别"""
        if rate < 0.1:
            return ErrorFrequency.RARE
        elif rate < 0.3:
            return ErrorFrequency.OCCASIONAL
        elif rate < 0.6:
            return ErrorFrequency.FREQUENT
        else:
            return ErrorFrequency.SYSTEMATIC

    def _generate_improvement_recommendations(
        self,
        systematic_errors: List[SystematicError],
        error_distribution: Dict[str, int],
        subject: str
    ) -> List[ImprovementRecommendation]:
        """生成改进建议"""
        recommendations = []

        # 为每个系统性错误生成建议
        for error in systematic_errors:
            priority = 5 if error.frequency == ErrorFrequency.SYSTEMATIC else 3

            recommendation = ImprovementRecommendation(
                priority=priority,
                title=f"改进{error.error_type.value}问题",
                description=f"该类型错误出现{error.occurrence_count}次，需要重点关注",
                action_items=self._get_action_items_for_error(error.error_type, subject),
                estimated_time="2-3周",
                learning_resources=self._get_learning_resources(error.error_type, subject),
                practice_exercises=[],
                expected_improvement="错误率预计降低50%",
                success_indicators=["连续5题同类型题目全对", "掌握度提升至80%以上"]
            )

            recommendations.append(recommendation)

        return sorted(recommendations, key=lambda x: x.priority, reverse=True)

    def _get_action_items_for_error(self, error_type: ErrorTypeEnum, subject: str) -> List[str]:
        """获取错误类型对应的行动项"""
        action_map = {
            ErrorTypeEnum.CALCULATION_ERROR: [
                "加强基础运算练习",
                "使用计算验证方法",
                "培养细心检查习惯"
            ],
            ErrorTypeEnum.CONCEPT_CONFUSION: [
                "重新梳理基础概念",
                "建立概念对比表",
                "增加概念应用练习"
            ],
            ErrorTypeEnum.FORMULA_MISUSE: [
                "整理公式使用条件",
                "练习公式推导过程",
                "建立公式应用场景库"
            ]
        }

        return action_map.get(error_type, ["加强相关知识点练习"])

    def _get_learning_resources(self, error_type: ErrorTypeEnum, subject: str) -> List[str]:
        """获取学习资源推荐"""
        return [
            f"{subject}基础概念复习",
            "相关练习题集",
            "视频教学资源"
        ]

    def _calculate_progress_indicators(
        self,
        student_id: int,
        subject: str,
        questions: List[Question]
    ) -> Dict[str, any]:
        """计算进步指标"""
        if not questions:
            return {}

        # 按时间排序
        sorted_questions = sorted(questions, key=lambda q: q.created_at)

        # 计算准确率趋势
        recent_accuracy = self._calculate_recent_accuracy(sorted_questions[-10:])  # 最近10题
        overall_accuracy = sum(1 for q in questions if q.is_correct) / len(questions)

        return {
            "overall_accuracy": round(overall_accuracy, 3),
            "recent_accuracy": round(recent_accuracy, 3),
            "total_practice_count": len(questions),
            "improvement_trend": "improving" if recent_accuracy > overall_accuracy else "stable"
        }

    def _calculate_recent_accuracy(self, questions: List[Question]) -> float:
        """计算最近的准确率"""
        if not questions:
            return 0.0

        correct_count = sum(1 for q in questions if q.is_correct)
        return correct_count / len(questions)

    def _create_empty_analysis(
        self,
        student_id: int,
        subject: str,
        timeframe_days: int
    ) -> ErrorPatternAnalysis:
        """创建空的分析结果"""
        return ErrorPatternAnalysis(
            student_id=student_id,
            subject=subject,
            analysis_period=f"最近{timeframe_days}天",
            total_questions=0,
            total_errors=0,
            error_rate=0.0,
            error_type_distribution={},
            severity_distribution={},
            systematic_errors=[],
            improvement_recommendations=[],
            progress_indicators={}
        )

    def _create_error_detail(
        self,
        error_type: ErrorTypeEnum,
        question: Question,
        subject: str
    ) -> ErrorDetail:
        """创建错误详情"""
        error_descriptions = {
            ErrorTypeEnum.CALCULATION_ERROR: "计算过程中出现错误",
            ErrorTypeEnum.CONCEPT_CONFUSION: "对基础概念理解有误",
            ErrorTypeEnum.FORMULA_MISUSE: "公式使用不当或条件不符",
            ErrorTypeEnum.LOGICAL_ERROR: "解题逻辑存在问题",
            ErrorTypeEnum.STEP_OMISSION: "解题步骤不完整"
        }

        correction_suggestions = {
            ErrorTypeEnum.CALCULATION_ERROR: "仔细检查计算过程，可以验算确认",
            ErrorTypeEnum.CONCEPT_CONFUSION: "重新学习相关基础概念",
            ErrorTypeEnum.FORMULA_MISUSE: "确认公式适用条件，正确套用公式",
            ErrorTypeEnum.LOGICAL_ERROR: "梳理解题思路，建立正确的逻辑链条",
            ErrorTypeEnum.STEP_OMISSION: "完整写出解题步骤，不要跳步"
        }

        return ErrorDetail(
            error_type=error_type,
            description=error_descriptions.get(error_type, "未知错误类型"),
            severity=self._determine_error_severity(question, subject),
            root_cause="需要进一步分析",
            correction_suggestion=correction_suggestions.get(error_type, "加强练习"),
            practice_recommendation=f"多做{subject}相关练习题"
        )

    def _calculate_question_score(self, question: Question, errors: List[ErrorDetail]) -> float:
        """计算题目得分"""
        if not errors:
            return 1.0

        # 简化的扣分计算
        deduction = 0.0
        for error in errors:
            if error.severity == SeverityLevel.CRITICAL:
                deduction += 0.5
            elif error.severity == SeverityLevel.HIGH:
                deduction += 0.3
            elif error.severity == SeverityLevel.MEDIUM:
                deduction += 0.2
            else:
                deduction += 0.1

        return max(0.0, 1.0 - deduction)

    def _generate_immediate_feedback(self, errors: List[ErrorDetail], subject: str) -> str:
        """生成即时反馈"""
        if not errors:
            return "答案正确！"

        error_count = len(errors)
        main_error = errors[0].error_type.value

        return f"发现{error_count}个问题，主要是{main_error}。建议重新检查解题过程。"

    def _generate_question_improvements(
        self,
        errors: List[ErrorDetail],
        subject: str
    ) -> List[str]:
        """生成题目改进建议"""
        suggestions = []

        for error in errors:
            suggestions.append(error.correction_suggestion)

        # 去重并返回
        return list(set(suggestions))

    def _analyze_knowledge_mastery(
        self,
        knowledge_points: List[str],
        errors: List[ErrorDetail]
    ) -> Dict[str, float]:
        """分析知识点掌握度"""
        mastery = {}

        for kp in knowledge_points:
            # 简化的掌握度计算：根据错误数量推断
            base_score = 0.8
            error_penalty = len(errors) * 0.1
            mastery[kp] = max(0.0, base_score - error_penalty)

        return mastery

    def _get_daily_error_data(
        self,
        student_id: int,
        subject: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, any]]:
        """获取每日错误数据"""
        # 简化实现 - 生成模拟数据
        daily_data = []
        current_date = start_date

        while current_date <= end_date:
            daily_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "error_rate": 0.3,  # 模拟数据
                "question_count": 5,
                "error_count": 1
            })
            current_date += timedelta(days=1)

        return daily_data

    def _aggregate_weekly_data(self, daily_data: List[Dict]) -> List[Dict[str, any]]:
        """聚合周度数据"""
        # 简化实现
        return [{
            "week": "Week 1",
            "avg_error_rate": 0.25,
            "total_questions": 35,
            "improvement": 0.05
        }]

    def _calculate_overall_trend(self, daily_data: List[Dict]) -> str:
        """计算总体趋势"""
        if len(daily_data) < 2:
            return "数据不足"

        # 简化实现：比较前后期平均错误率
        mid_point = len(daily_data) // 2
        early_avg = sum(d["error_rate"] for d in daily_data[:mid_point]) / mid_point
        late_avg = sum(d["error_rate"] for d in daily_data[mid_point:]) / (len(daily_data) - mid_point)

        if late_avg < early_avg * 0.9:
            return "improving"
        elif late_avg > early_avg * 1.1:
            return "worsening"
        else:
            return "stable"

    def _calculate_improvement_rate(self, daily_data: List[Dict]) -> float:
        """计算改进速度"""
        if len(daily_data) < 2:
            return 0.0

        # 简单线性回归计算改进率
        first_rate = daily_data[0]["error_rate"]
        last_rate = daily_data[-1]["error_rate"]
        days = len(daily_data)

        return round((first_rate - last_rate) / days, 4)


# ============= 服务实例管理 =============

_error_analysis_service: Optional[ErrorPatternService] = None


def get_error_analysis_service() -> ErrorPatternService:
    """获取错误分析服务实例（单例）"""
    global _error_analysis_service

    if _error_analysis_service is None:
        db = next(get_db())
        _error_analysis_service = ErrorPatternService(db)
        logger.info("ErrorPatternService 实例已创建")

    return _error_analysis_service
