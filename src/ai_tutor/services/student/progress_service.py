"""
学习进度管理服务
实现学生学习进度计算、薄弱知识点识别、学习轨迹分析等核心算法
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set, Any
from collections import defaultdict, Counter
from statistics import mean, stdev

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, Integer, Float

from ...core.logger import LoggerMixin
from ...models.student import Student
from ...models.homework import HomeworkSession, Question, SubjectEnum
from ...models.knowledge import KnowledgeProgress, KnowledgePoint, ErrorPattern
from ...schemas.student_schemas import SubjectProgress, LearningTrend
from ...db.database import get_db


class ProgressAlgorithm:
    """进度计算核心算法"""

    # 权重配置
    RECENT_WEIGHT = 0.6      # 近期表现权重
    HISTORICAL_WEIGHT = 0.4   # 历史表现权重
    CONFIDENCE_THRESHOLD = 0.75  # 掌握程度阈值
    MIN_ATTEMPTS_FOR_CONFIDENCE = 3  # 最小练习次数要求

    @classmethod
    def calculate_mastery_rate(
        cls,
        correct_answers: int,
        total_answers: int,
        recent_accuracy: float,
        time_decay_factor: float = 0.95
    ) -> float:
        """
        计算知识点掌握率

        Args:
            correct_answers: 历史正确答题数
            total_answers: 历史总答题数
            recent_accuracy: 近期准确率 (0-1)
            time_decay_factor: 时间衰减因子

        Returns:
            掌握率 (0-1)
        """
        if total_answers == 0:
            return 0.0

        # 历史准确率
        historical_accuracy = correct_answers / total_answers

        # 综合计算：近期表现 + 历史表现
        mastery_rate = (
            recent_accuracy * cls.RECENT_WEIGHT +
            historical_accuracy * cls.HISTORICAL_WEIGHT
        ) * time_decay_factor

        return min(1.0, max(0.0, mastery_rate))

    @classmethod
    def identify_weak_points(
        cls,
        knowledge_progresses: List[Dict],
        threshold: float = 0.6
    ) -> List[str]:
        """
        识别薄弱知识点

        Args:
            knowledge_progresses: 知识点进度列表
            threshold: 薄弱知识点阈值

        Returns:
            薄弱知识点名称列表
        """
        weak_points = []

        for progress in knowledge_progresses:
            mastery_level = progress.get('mastery_level', 0.0)
            total_attempts = progress.get('total_attempts', 0)
            knowledge_point_name = progress.get('knowledge_point_name', '')

            # 判断条件：掌握率低于阈值 且 有足够的练习次数
            if (mastery_level < threshold and
                total_attempts >= cls.MIN_ATTEMPTS_FOR_CONFIDENCE):
                weak_points.append(knowledge_point_name)

        return weak_points

    @classmethod
    def calculate_learning_velocity(
        cls,
        progress_history: List[Tuple[datetime, float]],
        days_window: int = 14
    ) -> float:
        """
        计算学习速度（进步速率）

        Args:
            progress_history: (时间, 掌握率) 的历史数据
            days_window: 计算窗口天数

        Returns:
            学习速度 (每天的进步率)
        """
        if len(progress_history) < 2:
            return 0.0

        # 按时间排序
        sorted_history = sorted(progress_history, key=lambda x: x[0])

        # 取最近的数据点
        cutoff_time = datetime.now() - timedelta(days=days_window)
        recent_history = [
            (time, rate) for time, rate in sorted_history
            if time >= cutoff_time
        ]

        if len(recent_history) < 2:
            recent_history = sorted_history[-2:]  # 至少取最后两个点

        # 计算线性回归斜率
        n = len(recent_history)
        x_values = [(h[0] - recent_history[0][0]).days for h in recent_history]
        y_values = [h[1] for h in recent_history]

        if len(set(x_values)) == 1:  # 避免除零错误
            return 0.0

        # 简单线性回归
        x_mean = mean(x_values)
        y_mean = mean(y_values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    @classmethod
    def predict_mastery_time(
        cls,
        current_mastery: float,
        target_mastery: float,
        learning_velocity: float
    ) -> Optional[int]:
        """
        预测达到目标掌握率需要的天数

        Args:
            current_mastery: 当前掌握率
            target_mastery: 目标掌握率
            learning_velocity: 学习速度

        Returns:
            预计天数，如果无法预测则返回None
        """
        if learning_velocity <= 0 or current_mastery >= target_mastery:
            return None

        days_needed = (target_mastery - current_mastery) / learning_velocity
        return max(1, int(days_needed))


class ProgressService(LoggerMixin):
    """学习进度管理服务"""

    def __init__(self):
        self.algorithm = ProgressAlgorithm()

    def get_db_session(self) -> Session:
        """获取数据库会话"""
        return next(get_db())

    async def calculate_subject_progress(
        self,
        student_id: int,
        subject: str,
        timeframe_days: int = 30
    ) -> SubjectProgress:
        """
        计算学生在指定科目的学习进度

        Args:
            student_id: 学生ID
            subject: 科目名称
            timeframe_days: 统计时间范围

        Returns:
            科目学习进度对象
        """
        db = self.get_db_session()

        try:
            # 获取时间范围
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)

            # 查询作业会话数据
            homework_sessions = db.query(HomeworkSession).filter(
                and_(
                    HomeworkSession.student_id == student_id,
                    HomeworkSession.subject == subject,
                    HomeworkSession.completed_at >= cutoff_date,
                    HomeworkSession.status == "completed"
                )
            ).all()

            # 计算总体统计
            total_questions = 0
            correct_questions = 0
            all_scores = []

            for session in homework_sessions:
                questions = db.query(Question).filter(
                    Question.homework_session_id == session.id
                ).all()

                for question in questions:
                    total_questions += 1
                    if question.is_correct:
                        correct_questions += 1
                    if question.score is not None:
                        all_scores.append(question.score)

            # 计算掌握率
            mastery_rate = 0.0
            recent_performance = 0.0

            if total_questions > 0:
                historical_accuracy = correct_questions / total_questions

                # 计算近期表现（最近7天）
                recent_cutoff = datetime.now() - timedelta(days=7)
                recent_sessions = [s for s in homework_sessions if s.completed_at >= recent_cutoff]

                recent_correct = 0
                recent_total = 0

                for session in recent_sessions:
                    questions = db.query(Question).filter(
                        Question.homework_session_id == session.id
                    ).all()

                    for question in questions:
                        recent_total += 1
                        if question.is_correct:
                            recent_correct += 1

                if recent_total > 0:
                    recent_performance = recent_correct / recent_total
                else:
                    recent_performance = historical_accuracy

                # 使用算法计算综合掌握率
                mastery_rate = self.algorithm.calculate_mastery_rate(
                    correct_answers=correct_questions,
                    total_answers=total_questions,
                    recent_accuracy=recent_performance,
                    time_decay_factor=0.95
                )

            # 获取薄弱知识点
            weak_knowledge_points = await self._get_weak_knowledge_points(
                db, student_id, subject
            )

            self.log_event(
                "计算科目学习进度",
                student_id=student_id,
                subject=subject,
                mastery_rate=mastery_rate,
                total_questions=total_questions,
                correct_questions=correct_questions
            )

            return SubjectProgress(
                subject=subject,
                mastery_rate=mastery_rate,
                total_questions=total_questions,
                correct_questions=correct_questions,
                recent_performance=recent_performance,
                weak_knowledge_points=weak_knowledge_points
            )

        except Exception as e:
            self.log_error("计算科目进度失败", error_msg=str(e), student_id=student_id, subject=subject)
            raise
        finally:
            db.close()

    async def get_learning_trends(
        self,
        student_id: int,
        subject: str,
        days: int = 30
    ) -> List[LearningTrend]:
        """
        获取学习趋势数据

        Args:
            student_id: 学生ID
            subject: 科目
            days: 统计天数

        Returns:
            学习趋势列表
        """
        db = self.get_db_session()

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # 按天聚合数据
            daily_stats = db.query(
                func.date(HomeworkSession.completed_at).label('date'),
                func.count(Question.id).label('total_questions'),
                func.sum(func.cast(Question.is_correct, Integer)).label('correct_questions'),
                func.avg(Question.score).label('avg_score')
            ).join(Question).filter(
                and_(
                    HomeworkSession.student_id == student_id,
                    HomeworkSession.subject == subject,
                    HomeworkSession.completed_at >= cutoff_date,
                    HomeworkSession.status == "completed"
                )
            ).group_by(
                func.date(HomeworkSession.completed_at)
            ).order_by(
                func.date(HomeworkSession.completed_at)
            ).all()

            trends = []
            for stat in daily_stats:
                accuracy = (stat.correct_questions / stat.total_questions
                           if stat.total_questions > 0 else 0.0)

                trends.append(LearningTrend(
                    date=stat.date,
                    accuracy_rate=accuracy,
                    practice_count=stat.total_questions,
                    average_score=stat.avg_score or 0.0
                ))

            return trends

        except Exception as e:
            self.log_error("获取学习趋势失败", error_msg=str(e), student_id=student_id, subject=subject)
            raise
        finally:
            db.close()

    async def update_knowledge_progress(
        self,
        student_id: int,
        knowledge_point_id: int,
        is_correct: bool,
        confidence_score: float = None
    ) -> None:
        """
        更新知识点掌握进度

        Args:
            student_id: 学生ID
            knowledge_point_id: 知识点ID
            is_correct: 本次练习是否正确
            confidence_score: 置信度分数
        """
        db = self.get_db_session()

        try:
            # 查询或创建知识点进度记录
            progress = db.query(KnowledgeProgress).filter(
                and_(
                    KnowledgeProgress.student_id == student_id,
                    KnowledgeProgress.knowledge_point_id == knowledge_point_id
                )
            ).first()

            if not progress:
                progress = KnowledgeProgress(
                    student_id=student_id,
                    knowledge_point_id=knowledge_point_id,
                    first_learned_at=datetime.now(),
                    total_attempts=0,
                    correct_attempts=0,
                    mastery_level=0.0,
                    last_practiced_at=datetime.now(),
                    common_errors={}
                )
                db.add(progress)

            # 更新统计数据
            progress.total_attempts += 1
            if is_correct:
                progress.correct_attempts += 1

            # 计算准确率
            progress.accuracy_rate = progress.correct_attempts / progress.total_attempts

            # 更新掌握程度
            if progress.total_attempts >= 3:  # 需要足够的数据点
                # 获取历史表现
                recent_accuracy = self._calculate_recent_accuracy(
                    db, student_id, knowledge_point_id, days=7
                )

                progress.mastery_level = self.algorithm.calculate_mastery_rate(
                    correct_answers=progress.correct_attempts,
                    total_answers=progress.total_attempts,
                    recent_accuracy=recent_accuracy or progress.accuracy_rate
                )

            # 更新置信度
            if confidence_score is not None:
                progress.confidence_score = confidence_score

            # 更新时间戳
            progress.last_practiced_at = datetime.now()
            progress.updated_at = datetime.now()

            # 检查是否达到掌握标准
            if (progress.mastery_level >= self.algorithm.CONFIDENCE_THRESHOLD and
                progress.mastery_achieved_at is None):
                progress.mastery_achieved_at = datetime.now()

            db.commit()

            self.log_event(
                "更新知识点进度",
                student_id=student_id,
                knowledge_point_id=knowledge_point_id,
                mastery_level=progress.mastery_level,
                accuracy_rate=progress.accuracy_rate
            )

        except Exception as e:
            db.rollback()
            self.log_error("更新知识点进度失败", error_msg=str(e), student_id=student_id)
            raise
        finally:
            db.close()

    async def get_learning_recommendations(
        self,
        student_id: int,
        subject: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取个性化学习建议

        Args:
            student_id: 学生ID
            subject: 科目
            limit: 建议数量限制

        Returns:
            学习建议列表
        """
        db = self.get_db_session()

        try:
            # 获取薄弱知识点
            weak_points_query = db.query(
                KnowledgeProgress, KnowledgePoint
            ).join(KnowledgePoint).filter(
                and_(
                    KnowledgeProgress.student_id == student_id,
                    KnowledgePoint.subject == subject,
                    KnowledgeProgress.mastery_level < 0.6,
                    KnowledgeProgress.total_attempts >= 2
                )
            ).order_by(KnowledgeProgress.mastery_level).limit(limit)

            recommendations = []

            for progress, knowledge_point in weak_points_query.all():
                # 分析错误模式
                common_errors = progress.common_errors or {}

                # 生成建议
                recommendation = {
                    "knowledge_point": knowledge_point.name,
                    "knowledge_point_id": knowledge_point.id,
                    "current_mastery": progress.mastery_level,
                    "priority": "high" if progress.mastery_level < 0.4 else "medium",
                    "suggested_practice_time": self._estimate_practice_time(progress),
                    "recommended_exercises": progress.recommended_exercises or [],
                    "improvement_strategies": self._generate_improvement_strategies(
                        knowledge_point, progress, common_errors
                    ),
                    "estimated_mastery_days": self._estimate_mastery_timeline(progress)
                }

                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            self.log_error("获取学习建议失败", error_msg=str(e), student_id=student_id, subject=subject)
            raise
        finally:
            db.close()

    async def analyze_learning_patterns(
        self,
        student_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        分析学生学习模式

        Args:
            student_id: 学生ID
            days: 分析天数

        Returns:
            学习模式分析结果
        """
        db = self.get_db_session()

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # 获取学习时间分布
            hourly_activity = db.query(
                func.extract('hour', HomeworkSession.created_at).label('hour'),
                func.count(HomeworkSession.id).label('count')
            ).filter(
                and_(
                    HomeworkSession.student_id == student_id,
                    HomeworkSession.created_at >= cutoff_date
                )
            ).group_by(
                func.extract('hour', HomeworkSession.created_at)
            ).all()

            # 学习频率分析
            daily_activity = db.query(
                func.date(HomeworkSession.created_at).label('date'),
                func.count(HomeworkSession.id).label('sessions'),
                func.sum(Question.score).label('total_score')
            ).join(Question).filter(
                and_(
                    HomeworkSession.student_id == student_id,
                    HomeworkSession.created_at >= cutoff_date
                )
            ).group_by(
                func.date(HomeworkSession.created_at)
            ).all()

            # 科目偏好分析
            subject_performance = db.query(
                HomeworkSession.subject,
                func.count(Question.id).label('question_count'),
                func.avg(func.cast(Question.is_correct, Float)).label('accuracy'),
                func.avg(Question.score).label('avg_score')
            ).join(Question).filter(
                and_(
                    HomeworkSession.student_id == student_id,
                    HomeworkSession.created_at >= cutoff_date
                )
            ).group_by(HomeworkSession.subject).all()

            # 计算学习一致性
            daily_counts = [activity.sessions for activity in daily_activity]
            learning_consistency = (1 - (stdev(daily_counts) / mean(daily_counts))
                                  if len(daily_counts) > 1 and mean(daily_counts) > 0 else 0)

            # 识别最佳学习时间
            if hourly_activity:
                best_hour = max(hourly_activity, key=lambda x: x.count).hour
            else:
                best_hour = None

            return {
                "learning_consistency": max(0, learning_consistency),
                "best_learning_hour": best_hour,
                "daily_activity_pattern": [
                    {"date": str(activity.date), "sessions": activity.sessions}
                    for activity in daily_activity
                ],
                "subject_preferences": [
                    {
                        "subject": perf.subject,
                        "engagement_level": perf.question_count,
                        "performance": perf.accuracy or 0,
                        "avg_score": perf.avg_score or 0
                    }
                    for perf in subject_performance
                ],
                "total_study_days": len(daily_activity),
                "avg_daily_sessions": mean([a.sessions for a in daily_activity]) if daily_activity else 0
            }

        except Exception as e:
            self.log_error("分析学习模式失败", error_msg=str(e), student_id=student_id)
            raise
        finally:
            db.close()

    # === 私有辅助方法 ===

    async def _get_weak_knowledge_points(
        self,
        db: Session,
        student_id: int,
        subject: str
    ) -> List[str]:
        """获取薄弱知识点列表"""
        try:
            weak_points_query = db.query(
                KnowledgeProgress, KnowledgePoint
            ).join(KnowledgePoint).filter(
                and_(
                    KnowledgeProgress.student_id == student_id,
                    KnowledgePoint.subject == subject,
                    KnowledgeProgress.mastery_level < 0.6,
                    KnowledgeProgress.total_attempts >= 2
                )
            ).order_by(KnowledgeProgress.mastery_level)

            return [kp.name for _, kp in weak_points_query.all()]

        except Exception:
            return []

    def _calculate_recent_accuracy(
        self,
        db: Session,
        student_id: int,
        knowledge_point_id: int,
        days: int = 7
    ) -> Optional[float]:
        """计算近期准确率"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # 这里需要根据实际的题目-知识点关联表来查询
            # 暂时返回None，在实际项目中需要实现具体的查询逻辑
            return None

        except Exception:
            return None

    def _estimate_practice_time(self, progress: KnowledgeProgress) -> int:
        """估算需要的练习时间（分钟）"""
        base_time = 30  # 基础练习时间
        mastery_gap = 1.0 - progress.mastery_level
        return int(base_time * (1 + mastery_gap * 2))

    def _generate_improvement_strategies(
        self,
        knowledge_point: KnowledgePoint,
        progress: KnowledgeProgress,
        common_errors: Dict
    ) -> List[str]:
        """生成改进策略"""
        strategies = []

        if progress.mastery_level < 0.3:
            strategies.append("建议从基础概念开始复习")
            strategies.append("寻求老师或同学的帮助")
        elif progress.mastery_level < 0.6:
            strategies.append("增加相关练习题的数量")
            strategies.append("总结常见错误和解题技巧")
        else:
            strategies.append("通过变式练习巩固理解")
            strategies.append("尝试教别人来加深理解")

        # 基于错误模式的个性化建议
        if common_errors:
            error_types = list(common_errors.keys())
            if "calculation_error" in error_types:
                strategies.append("注意计算细节，使用验算方法")
            if "concept_confusion" in error_types:
                strategies.append("重点理解概念区别和应用场景")

        return strategies

    def _estimate_mastery_timeline(self, progress: KnowledgeProgress) -> Optional[int]:
        """估算掌握时间线（天数）"""
        if progress.mastery_level >= 0.75:
            return None  # 已经掌握

        # 基于当前掌握率和历史进步速度的简单估算
        target_mastery = 0.75
        current_mastery = progress.mastery_level

        # 假设每天能提升0.05的掌握率（可以根据历史数据调整）
        daily_improvement = 0.05

        days_needed = (target_mastery - current_mastery) / daily_improvement
        return max(1, int(days_needed))


# 单例模式
_progress_service_instance = None


def get_progress_service() -> ProgressService:
    """获取进度服务实例"""
    global _progress_service_instance
    if _progress_service_instance is None:
        _progress_service_instance = ProgressService()
    return _progress_service_instance
