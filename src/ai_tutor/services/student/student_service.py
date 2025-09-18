"""
学生管理核心服务
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, or_, func, desc, distinct, Integer
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ...core.logger import LoggerMixin
from ...models.student import Student
from ...models.homework import HomeworkSession, Question
from ...models.knowledge import KnowledgeProgress
from ...schemas.student_schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentStats,
    StudentFilter,
    PaginationParams,
    StudentListResponse,
    SubjectProgress,
    LearningTrend,
    StudentActivity,
    StudentDetailResponse,
    HomeworkSubmission,
    HomeworkHistoryResponse,
)
from .exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    StudentInactiveError,
    DatabaseOperationError,
)


class StudentService(LoggerMixin):
    """学生管理服务类"""

    def __init__(self, db: Session):
        """初始化学生服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self.log_event("学生管理服务初始化")

    async def create_student(self, student_data: StudentCreate) -> StudentResponse:
        """创建新学生

        Args:
            student_data: 学生创建数据

        Returns:
            StudentResponse: 创建的学生信息

        Raises:
            DuplicateStudentError: 学生重复
            InvalidStudentDataError: 数据无效
            DatabaseOperationError: 数据库操作错误
        """
        try:
            self.log_event(
                "开始创建学生", name=student_data.name, grade=student_data.grade
            )

            # 验证学生数据
            await self._validate_student_data(student_data.model_dump(), is_create=True)

            # 检查重复
            await self._check_duplicate_student(
                name=student_data.name,
                class_name=student_data.class_name,
                student_id=student_data.student_id,
            )

            # 创建学生记录
            db_student = Student(**student_data.model_dump())
            self.db.add(db_student)
            self.db.commit()
            self.db.refresh(db_student)

            # 转换为响应模型
            result = StudentResponse.model_validate(db_student)

            self.log_event(
                "学生创建成功",
                student_id=result.id,
                name=result.name,
                grade=result.grade,
            )

            return result

        except (DuplicateStudentError, InvalidStudentDataError):
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            self.log_error("数据完整性约束违反", exception=str(e))
            raise DuplicateStudentError(
                name=student_data.name,
                class_name=student_data.class_name,
                student_id=student_data.student_id,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            self.log_error("数据库操作错误", exception=str(e))
            raise DatabaseOperationError("创建学生", e)
        except Exception as e:
            self.db.rollback()
            self.log_error("创建学生失败", error_msg=str(e), error_type=type(e).__name__)
            raise DatabaseOperationError("创建学生", e)

    async def get_student(
        self, student_id: int, include_stats: bool = False
    ) -> StudentResponse:
        """根据ID获取学生信息

        Args:
            student_id: 学生ID
            include_stats: 是否包含统计信息

        Returns:
            StudentResponse: 学生信息

        Raises:
            StudentNotFoundError: 学生未找到
        """
        try:
            self.log_event(
                "获取学生信息", student_id=student_id, include_stats=include_stats
            )

            # 查询学生
            query = self.db.query(Student).filter(Student.id == student_id)
            student = query.first()

            if not student:
                raise StudentNotFoundError(student_id=student_id)

            if include_stats:
                # 获取详细信息包含统计
                stats = await self._get_student_stats(student_id)
                activities = await self._get_recent_activities(student_id, limit=10)

                result = StudentDetailResponse.model_validate(student)
                result.stats = stats
                result.recent_activities = activities
            else:
                result = StudentResponse.model_validate(student)

            self.log_event("获取学生信息成功", student_id=student_id, name=student.name)
            return result

        except StudentNotFoundError:
            raise
        except Exception as e:
            self.log_error("获取学生信息失败", student_id=student_id, exception=str(e))
            raise DatabaseOperationError("获取学生", e)

    async def update_student(
        self, student_id: int, student_data: StudentUpdate
    ) -> StudentResponse:
        """更新学生信息

        Args:
            student_id: 学生ID
            student_data: 更新数据

        Returns:
            StudentResponse: 更新后的学生信息

        Raises:
            StudentNotFoundError: 学生未找到
            DuplicateStudentError: 学生重复
            InvalidStudentDataError: 数据无效
        """
        try:
            self.log_event("开始更新学生", student_id=student_id)

            # 获取现有学生
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise StudentNotFoundError(student_id=student_id)

            # 获取更新字段
            update_data = student_data.model_dump(exclude_unset=True)
            if not update_data:
                self.log_warning("没有提供更新数据", student_id=student_id)
                return StudentResponse.model_validate(student)

            # 验证数据
            await self._validate_student_data(update_data, is_create=False)

            # 检查重复（如果更新了姓名、班级或学号）
            if any(
                field in update_data for field in ["name", "class_name", "student_id"]
            ):
                name = update_data.get("name", student.name)
                class_name = update_data.get("class_name", student.class_name)
                student_id_value = update_data.get("student_id", student.student_id)

                await self._check_duplicate_student(
                    name=name,
                    class_name=class_name,
                    student_id=student_id_value,
                    exclude_id=student_id,
                )

            # 更新字段
            for field, value in update_data.items():
                setattr(student, field, value)

            self.db.commit()
            self.db.refresh(student)

            result = StudentResponse.model_validate(student)

            self.log_event(
                "学生更新成功",
                student_id=student_id,
                updated_fields=list(update_data.keys()),
            )

            return result

        except (StudentNotFoundError, DuplicateStudentError, InvalidStudentDataError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            self.log_error("更新学生失败", student_id=student_id, exception=str(e))
            raise DatabaseOperationError("更新学生", e)

    async def delete_student(self, student_id: int, soft_delete: bool = True) -> bool:
        """删除学生（支持软删除）

        Args:
            student_id: 学生ID
            soft_delete: 是否软删除（默认True）

        Returns:
            bool: 操作是否成功

        Raises:
            StudentNotFoundError: 学生未找到
        """
        try:
            self.log_event(
                "开始删除学生", student_id=student_id, soft_delete=soft_delete
            )

            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise StudentNotFoundError(student_id=student_id)

            if soft_delete:
                # 软删除：设置为非活跃状态
                student.is_active = False
                self.db.commit()
                self.log_event("学生软删除成功", student_id=student_id)
            else:
                # 硬删除：实际删除记录（谨慎使用）
                self.db.delete(student)
                self.db.commit()
                self.log_event("学生硬删除成功", student_id=student_id)

            return True

        except StudentNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            self.log_error("删除学生失败", student_id=student_id, exception=str(e))
            raise DatabaseOperationError("删除学生", e)

    async def list_students(
        self,
        filters: Optional[StudentFilter] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> StudentListResponse:
        """分页查询学生列表

        Args:
            filters: 过滤条件
            pagination: 分页参数

        Returns:
            StudentListResponse: 学生列表响应
        """
        try:
            if pagination is None:
                pagination = PaginationParams()

            self.log_event(
                "查询学生列表", page=pagination.page, page_size=pagination.page_size
            )

            # 构建查询
            query = self.db.query(Student)

            # 应用过滤条件
            if filters:
                query = self._apply_student_filters(query, filters)

            # 获取总数
            total_count = query.count()

            # 应用分页和排序
            students = (
                query.order_by(desc(Student.created_at), Student.id)
                .offset(pagination.offset)
                .limit(pagination.page_size)
                .all()
            )

            # 转换为响应模型
            student_responses = [StudentResponse.model_validate(s) for s in students]

            result = StudentListResponse.create(
                students=student_responses,
                total_count=total_count,
                pagination=pagination,
            )

            self.log_event(
                "查询学生列表成功",
                count=len(student_responses),
                total=total_count,
                page=pagination.page,
            )

            return result

        except Exception as e:
            self.log_error("查询学生列表失败", exception=str(e))
            raise DatabaseOperationError("查询学生列表", e)

    async def search_students(
        self, keyword: str, limit: int = 20
    ) -> List[StudentResponse]:
        """搜索学生（按姓名、学号、班级）

        Args:
            keyword: 搜索关键词
            limit: 限制数量

        Returns:
            List[StudentResponse]: 学生列表
        """
        try:
            self.log_event("搜索学生", keyword=keyword, limit=limit)

            keyword = f"%{keyword}%"
            students = (
                self.db.query(Student)
                .filter(
                    and_(
                        Student.is_active == True,
                        or_(
                            Student.name.like(keyword),
                            Student.student_id.like(keyword),
                            Student.class_name.like(keyword),
                        ),
                    )
                )
                .order_by(Student.name)
                .limit(limit)
                .all()
            )

            result = [StudentResponse.model_validate(s) for s in students]

            self.log_event("搜索学生成功", keyword=keyword, count=len(result))
            return result

        except Exception as e:
            self.log_error("搜索学生失败", keyword=keyword, exception=str(e))
            raise DatabaseOperationError("搜索学生", e)

    async def get_student_stats(self, student_id: int) -> StudentStats:
        """获取学生学习统计信息

        Args:
            student_id: 学生ID

        Returns:
            StudentStats: 学习统计信息
        """
        try:
            # 验证学生存在
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise StudentNotFoundError(student_id=student_id)

            return await self._get_student_stats(student_id)

        except StudentNotFoundError:
            raise
        except Exception as e:
            self.log_error("获取学生统计失败", student_id=student_id, exception=str(e))
            raise DatabaseOperationError("获取学生统计", e)

    async def get_homework_history(
        self,
        student_id: int,
        limit: int = 20,
        offset: int = 0,
        subject: Optional[str] = None
    ) -> List[HomeworkSubmission]:
        """获取学生作业历史记录

        Args:
            student_id: 学生ID
            limit: 返回记录数量限制
            offset: 偏移量
            subject: 科目筛选（可选）

        Returns:
            List[HomeworkSubmission]: 作业提交记录列表
        """
        try:
            # 验证学生存在
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise StudentNotFoundError(student_id=student_id)

            self.log_event("获取作业历史", student_id=student_id, limit=limit, offset=offset)

            # 构建查询
            query = self.db.query(HomeworkSession).filter(
                HomeworkSession.student_id == student_id
            )

            # 添加科目筛选
            if subject:
                query = query.filter(HomeworkSession.subject == subject.upper())

            # 排序和分页
            homework_sessions = (
                query.order_by(desc(HomeworkSession.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            # 转换为HomeworkSubmission格式
            submissions = []
            for session in homework_sessions:
                # 计算统计信息
                questions = self.db.query(Question).filter(
                    Question.homework_session_id == session.id
                ).all()

                total_questions = len(questions)
                correct_answers = sum(1 for q in questions if q.is_correct)
                accuracy_rate = correct_answers / total_questions if total_questions > 0 else 0.0
                total_score = sum(q.score for q in questions if q.score is not None)
                max_score = sum(q.max_score for q in questions if q.max_score is not None)
                grade_percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

                # 提取错误类型和知识点
                error_types = []
                weak_knowledge_points = []
                improvement_suggestions = []

                for question in questions:
                    if hasattr(question, 'error_type') and question.error_type:
                        error_types.append(question.error_type)
                    if hasattr(question, 'knowledge_points') and question.knowledge_points:
                        weak_knowledge_points.extend(question.knowledge_points)
                    if hasattr(question, 'feedback') and question.feedback:
                        improvement_suggestions.append(question.feedback)

                submission = HomeworkSubmission(
                    id=session.id,
                    student_id=session.student_id,
                    subject=session.subject.lower() if session.subject else "unknown",
                    submission_date=session.created_at,
                    total_questions=total_questions,
                    correct_answers=correct_answers,
                    accuracy_rate=round(accuracy_rate, 3),
                    total_score=round(total_score, 2),
                    max_score=round(max_score, 2),
                    grade_percentage=round(grade_percentage, 1),
                    time_spent_minutes=getattr(session, 'time_spent_minutes', None),
                    difficulty_level=getattr(session, 'difficulty_level', 3),
                    ai_provider=getattr(session, 'ai_provider', None),
                    ocr_text=getattr(session, 'ocr_text', None),
                    processing_time=getattr(session, 'processing_time', None),
                    feedback=getattr(session, 'feedback', None),
                    weak_knowledge_points=list(set(weak_knowledge_points)),
                    improvement_suggestions=list(set(improvement_suggestions)),
                    error_types=list(set(error_types)),
                    is_completed=getattr(session, 'is_completed', True),
                    created_at=session.created_at,
                    updated_at=session.updated_at or session.created_at
                )
                submissions.append(submission)

            self.log_event(
                "获取作业历史成功",
                student_id=student_id,
                submissions_count=len(submissions)
            )
            return submissions

        except StudentNotFoundError:
            raise
        except Exception as e:
            self.log_error(
                "获取作业历史失败",
                student_id=student_id,
                exception=str(e)
            )
            # 返回空列表而不是抛出异常，保证前端能正常处理
            return []

    # 私有辅助方法

    async def _validate_student_data(self, data: dict, is_create: bool = True) -> None:
        """验证学生数据"""
        # 基础格式验证已经在Pydantic模型中完成

        # 业务规则验证
        if "grade" in data:
            valid_grades = ["初一", "初二", "初三", "高一", "高二", "高三"]
            if data["grade"] not in valid_grades:
                raise InvalidStudentDataError(
                    "grade", data["grade"], "年级必须在初一到高三范围内"
                )

        if "class_name" in data and data["class_name"]:
            class_name = data["class_name"]
            if len(class_name) > 20:
                raise InvalidStudentDataError("class_name", class_name, "班级名称过长")

    async def _check_duplicate_student(
        self,
        name: str,
        class_name: str = None,
        student_id: str = None,
        exclude_id: int = None,
    ) -> None:
        """检查学生重复"""
        query = self.db.query(Student).filter(Student.is_active == True)

        if exclude_id:
            query = query.filter(Student.id != exclude_id)

        # 检查学号重复
        if student_id:
            existing = query.filter(Student.student_id == student_id).first()
            if existing:
                raise DuplicateStudentError(name, student_id=student_id)

        # 检查同班同名
        if class_name:
            existing = query.filter(
                and_(Student.name == name, Student.class_name == class_name)
            ).first()
            if existing:
                raise DuplicateStudentError(name, class_name)

    def _apply_student_filters(self, query, filters: StudentFilter):
        """应用学生过滤条件"""
        if filters.name:
            query = query.filter(Student.name.like(f"%{filters.name}%"))

        if filters.grade:
            query = query.filter(Student.grade == filters.grade)

        if filters.class_name:
            query = query.filter(Student.class_name.like(f"%{filters.class_name}%"))

        if filters.is_active is not None:
            query = query.filter(Student.is_active == filters.is_active)

        if filters.created_after:
            query = query.filter(Student.created_at >= filters.created_after)

        if filters.created_before:
            query = query.filter(Student.created_at <= filters.created_before)

        # 有作业记录的学生过滤
        if filters.has_homework is not None:
            if filters.has_homework:
                query = query.join(HomeworkSession).filter(
                    HomeworkSession.student_id == Student.id
                )
            else:
                query = query.outerjoin(HomeworkSession).filter(
                    HomeworkSession.student_id.is_(None)
                )

        return query

    async def _get_student_stats(self, student_id: int) -> StudentStats:
        """获取学生统计信息（内部方法）"""
        # 基础统计
        homework_count = (
            self.db.query(func.count(HomeworkSession.id))
            .filter(HomeworkSession.student_id == student_id)
            .scalar()
            or 0
        )

        question_stats = (
            self.db.query(
                func.count(Question.id).label("total"),
                func.sum(func.cast(Question.is_correct, Integer)).label("correct"),
            )
            .join(HomeworkSession)
            .filter(HomeworkSession.student_id == student_id)
            .first()
        )

        total_questions = question_stats.total or 0
        correct_questions = question_stats.correct or 0
        accuracy_rate = (
            correct_questions / total_questions if total_questions > 0 else 0.0
        )

        # 活跃天数统计
        active_days = (
            self.db.query(func.count(distinct(func.date(HomeworkSession.created_at))))
            .filter(HomeworkSession.student_id == student_id)
            .scalar()
            or 0
        )

        # 已学习科目
        subjects_studied = (
            self.db.query(distinct(HomeworkSession.subject))
            .filter(HomeworkSession.student_id == student_id)
            .all()
        )
        subjects_list = [s[0] for s in subjects_studied if s[0]]

        # 各科目进度（简化版本）
        subject_progress = []
        for subject in subjects_list:
            subject_stats = (
                self.db.query(
                    func.count(Question.id).label("total"),
                    func.sum(func.cast(Question.is_correct, Integer)).label("correct"),
                )
                .join(HomeworkSession)
                .filter(
                    and_(
                        HomeworkSession.student_id == student_id,
                        HomeworkSession.subject == subject,
                    )
                )
                .first()
            )

            total = subject_stats.total or 0
            correct = subject_stats.correct or 0
            mastery = correct / total if total > 0 else 0.0

            subject_progress.append(
                SubjectProgress(
                    subject=subject,
                    mastery_rate=mastery,
                    total_questions=total,
                    correct_questions=correct,
                    recent_performance=mastery,  # 简化处理
                    weak_knowledge_points=[],  # TODO: 实现知识点分析
                )
            )

        # 最近趋势（简化版本）
        recent_trends = await self._get_learning_trends(student_id, days=7)

        return StudentStats(
            total_homework_sessions=homework_count,
            total_questions_answered=total_questions,
            overall_accuracy_rate=accuracy_rate,
            active_days=active_days,
            subjects_studied=subjects_list,
            subject_progress=subject_progress,
            recent_trends=recent_trends,
        )

    async def _get_learning_trends(
        self, student_id: int, days: int = 7
    ) -> List[LearningTrend]:
        """获取学习趋势数据"""
        # 简化实现：最近N天的每日统计
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        trends = []
        for i in range(days):
            date = start_date + timedelta(days=i)

            # 查询该天的作业统计
            day_stats = (
                self.db.query(
                    func.count(Question.id).label("total"),
                    func.sum(func.cast(Question.is_correct, Integer)).label("correct"),
                )
                .join(HomeworkSession)
                .filter(
                    and_(
                        HomeworkSession.student_id == student_id,
                        func.date(HomeworkSession.created_at) == date.date(),
                    )
                )
                .first()
            )

            total = day_stats.total or 0
            correct = day_stats.correct or 0
            accuracy = correct / total if total > 0 else 0.0

            trends.append(
                LearningTrend(
                    date=date,
                    accuracy_rate=accuracy,
                    questions_count=total,
                    study_time_minutes=0,  # TODO: 实现学习时长统计
                )
            )

        return trends

    async def _get_recent_activities(
        self, student_id: int, limit: int = 10
    ) -> List[StudentActivity]:
        """获取最近活动记录"""
        # 查询最近的作业记录
        sessions = (
            self.db.query(HomeworkSession)
            .filter(HomeworkSession.student_id == student_id)
            .order_by(desc(HomeworkSession.created_at))
            .limit(limit)
            .all()
        )

        activities = []
        for session in sessions:
            # 计算该次作业的正确率
            total_questions = len(session.questions) if session.questions else 0
            correct_questions = (
                sum(1 for q in session.questions if q.is_correct)
                if session.questions
                else 0
            )
            accuracy = (
                correct_questions / total_questions if total_questions > 0 else 0.0
            )

            activities.append(
                StudentActivity(
                    activity_type="homework_completion",
                    activity_date=session.created_at,
                    subject=session.subject,
                    description=f"完成{session.subject}作业，共{total_questions}题",
                    performance=accuracy,
                )
            )

        return activities
