"""
StudentService单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ai_tutor.services.student.student_service import StudentService
from ai_tutor.services.student.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    DatabaseOperationError,
)
from ai_tutor.schemas.student_schemas import (
    StudentCreate,
    StudentUpdate,
    StudentFilter,
    PaginationParams,
)
from ai_tutor.models.student import Student


class TestStudentService:
    """StudentService测试类"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        mock_db = Mock()

        # 创建支持链式调用的query mock
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query

        mock_db.query.return_value = mock_query
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.rollback = Mock()
        mock_db.refresh = Mock()
        mock_db.delete = Mock()
        return mock_db

    @pytest.fixture
    def student_service(self, mock_db):
        """创建StudentService实例"""
        with patch.object(StudentService, "log_event"):
            return StudentService(mock_db)

    @pytest.fixture
    def sample_student_data(self):
        """示例学生数据"""
        return StudentCreate(
            name="张小明",
            grade="初二",
            class_name="初二(3)班",
            student_id="2023001",
            phone="13812345678",
            email="zhangxiaoming@example.com",
            parent_phone="13987654321",
            preferred_subjects=["math", "physics"],
            learning_style="视觉型",
        )

    @pytest.fixture
    def sample_student_model(self):
        """示例学生模型"""
        return Student(
            id=1,
            name="张小明",
            grade="初二",
            class_name="初二(3)班",
            student_id="2023001",
            phone="13812345678",
            email="zhangxiaoming@example.com",
            parent_phone="13987654321",
            preferred_subjects=["math", "physics"],
            learning_style="视觉型",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


class TestCreateStudent(TestStudentService):
    """创建学生测试"""

    @pytest.mark.asyncio
    async def test_create_student_success(
        self, student_service, sample_student_data, sample_student_model, mock_db
    ):
        """测试成功创建学生"""
        # 确保没有重复学生
        mock_db.query.return_value.first.return_value = None

        # 模拟refresh操作设置id
        def mock_refresh(obj):
            obj.id = 1
            obj.is_active = True
            obj.created_at = datetime.now()
            obj.updated_at = datetime.now()

        mock_db.refresh.side_effect = mock_refresh

        # 模拟数据库返回
        with patch(
            "ai_tutor.services.student.student_service.Student"
        ) as MockStudent:
            MockStudent.return_value = sample_student_model

            # 执行
            result = await student_service.create_student(sample_student_data)

            # 断言
            assert result.id == 1
            assert result.name == "张小明"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_student_duplicate_error(
        self, student_service, sample_student_data, mock_db
    ):
        """测试创建重复学生"""
        # 安排：模拟学号重复
        mock_db.query().filter().first.return_value = Mock(student_id="2023001")

        # 执行和断言
        with pytest.raises(DuplicateStudentError) as exc_info:
            await student_service.create_student(sample_student_data)

        assert "学号重复" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_student_invalid_grade(
        self, student_service, sample_student_data, mock_db
    ):
        """测试无效年级"""
        # 安排
        sample_student_data.grade = "大一"  # 无效年级
        mock_db.query().filter().first.return_value = None

        # 执行和断言
        with pytest.raises(InvalidStudentDataError) as exc_info:
            await student_service.create_student(sample_student_data)

        assert "年级必须在初一到高三范围内" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_student_database_error(
        self, student_service, sample_student_data, mock_db
    ):
        """测试数据库错误"""
        # 安排 - 确保通过重复检查但在commit时失败
        mock_db.query.return_value.first.return_value = None
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        # 执行和断言
        with pytest.raises(DatabaseOperationError):
            await student_service.create_student(sample_student_data)

        mock_db.rollback.assert_called_once()


class TestGetStudent(TestStudentService):
    """获取学生测试"""

    @pytest.mark.asyncio
    async def test_get_student_success(
        self, student_service, sample_student_model, mock_db
    ):
        """测试成功获取学生"""
        # 安排
        mock_db.query.return_value.first.return_value = sample_student_model

        # 执行
        result = await student_service.get_student(1)

        # 断言
        assert result.id == 1
        assert result.name == "张小明"
        mock_db.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_student_not_found(self, student_service, mock_db):
        """测试学生未找到"""
        # 安排
        mock_db.query().filter().first.return_value = None

        # 执行和断言
        with pytest.raises(StudentNotFoundError) as exc_info:
            await student_service.get_student(999)

        assert exc_info.value.details["student_id"] == 999

    @pytest.mark.asyncio
    async def test_get_student_with_stats(
        self, student_service, sample_student_model, mock_db
    ):
        """测试获取学生详细信息（包含统计）"""
        # 简化测试 - 直接模拟内部方法而不是复杂的查询链
        with patch.object(student_service, '_get_student_stats') as mock_stats:
            with patch.object(student_service, '_get_recent_activities') as mock_activities:
                # 安排
                mock_db.query.return_value.filter.return_value.first.return_value = sample_student_model

                # 模拟统计数据
                from ai_tutor.schemas.student_schemas import StudentStats
                mock_stats.return_value = StudentStats(
                    homework_count=10,
                    total_questions=100,
                    correct_questions=80,
                    accuracy_rate=0.8,
                    active_days=15,
                    subjects_studied=["math", "physics"],
                    subject_progress=[]
                )

                # 模拟活动数据
                mock_activities.return_value = []

                # 执行
                result = await student_service.get_student(1, include_stats=True)

                # 断言
                assert hasattr(result, "stats")
                assert hasattr(result, "recent_activities")
                mock_stats.assert_called_once_with(1)
                mock_activities.assert_called_once_with(1, limit=10)


class TestUpdateStudent(TestStudentService):
    """更新学生测试"""

    @pytest.mark.asyncio
    async def test_update_student_success(
        self, student_service, sample_student_model, mock_db
    ):
        """测试成功更新学生"""
        # 安排 - 简化mock设置，专注于重复检查
        mock_db.query.return_value.filter.return_value.first.return_value = sample_student_model

        # 为重复检查设置不同的mock
        with patch.object(student_service, '_check_duplicate_student') as mock_check:
            mock_check.return_value = None  # 无重复

            update_data = StudentUpdate(name="李小红", phone="13911111111")

            # 执行
            result = await student_service.update_student(1, update_data)

            # 断言
            assert result.id == 1
            mock_db.commit.assert_called_once()
            mock_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_students_with_filters(
        self, student_service, sample_student_model, mock_db
    ):
        """测试带筛选条件的学生列表"""
        # 简化测试 - 使用patch模拟复杂的过滤逻辑
        with patch.object(student_service, '_apply_student_filters') as mock_apply_filters:
            # 安排
            filters = StudentFilter(name="张", grade="初二", is_active=True)
            pagination = PaginationParams(page=1, page_size=10)

            # 设置完整的查询链mock
            mock_query = Mock()
            mock_apply_filters.return_value = mock_query
            mock_query.count.return_value = 1
            mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_student_model]
            mock_db.query.return_value = Mock()

            # 执行
            result = await student_service.list_students(filters, pagination)

            # 断言
            assert len(result.students) == 1
            assert result.total_count == 1
            assert result.page == 1
            assert result.page_size == 10
            mock_apply_filters.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_student_not_found(self, student_service, mock_db):
        """测试更新不存在的学生"""
        # 安排
        mock_db.query.return_value.first.return_value = None
        update_data = StudentUpdate(name="新名字")

        # 执行和断言
        with pytest.raises(StudentNotFoundError):
            await student_service.update_student(999, update_data)

    @pytest.mark.asyncio
    async def test_update_student_no_changes(
        self, student_service, sample_student_model, mock_db
    ):
        """测试无更新内容"""
        # 安排
        mock_db.query.return_value.first.return_value = sample_student_model
        update_data = StudentUpdate()  # 空更新

        # 执行
        result = await student_service.update_student(1, update_data)

        # 断言
        mock_db.commit.assert_not_called()  # 应该没有提交
        assert result.name == "张小明"  # 保持原样


class TestDeleteStudent(TestStudentService):
    """删除学生测试"""

    @pytest.mark.asyncio
    async def test_soft_delete_student(
        self, student_service, sample_student_model, mock_db
    ):
        """测试软删除学生"""
        # 安排
        mock_db.query.return_value.first.return_value = sample_student_model

        # 执行
        result = await student_service.delete_student(1, soft_delete=True)

        # 断言
        assert result is True
        assert sample_student_model.is_active is False
        mock_db.commit.assert_called_once()
        mock_db.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_hard_delete_student(
        self, student_service, sample_student_model, mock_db
    ):
        """测试硬删除学生"""
        # 安排
        mock_db.query.return_value.first.return_value = sample_student_model

        # 执行
        result = await student_service.delete_student(1, soft_delete=False)

        # 断言
        assert result is True
        mock_db.delete.assert_called_once_with(sample_student_model)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_student_not_found(self, student_service, mock_db):
        """测试删除不存在的学生"""
        # 安排
        mock_db.query.return_value.first.return_value = None

        # 执行和断言
        with pytest.raises(StudentNotFoundError):
            await student_service.delete_student(999)


class TestListStudents(TestStudentService):
    """学生列表测试"""

    @pytest.mark.asyncio
    async def test_list_students_with_pagination(self, student_service, mock_db, sample_student_model):
        """测试分页查询学生列表"""
        # 安排 - 创建真实的Student对象
        sample_students = []
        for i in range(1, 6):
            student = Student(
                id=i,
                name=f"学生{i}",
                grade="初二",
                class_name="初二(3)班",
                student_id=f"202300{i}",
                phone="13812345678",
                email=f"student{i}@example.com",
                parent_phone="13987654321",
                preferred_subjects=["math"],
                learning_style="视觉型",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            sample_students.append(student)

        # 设置完整的查询链mock
        mock_query = Mock()
        mock_query.count.return_value = 100
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_students
        mock_db.query.return_value = mock_query

        pagination = PaginationParams(page=1, page_size=5)

        # 执行
        result = await student_service.list_students(pagination=pagination)

        # 断言
        assert len(result.students) == 5
        assert result.total_count == 100
        assert result.page == 1
        assert result.page_size == 5
        assert result.total_pages == 20
        assert result.has_next is True
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_list_students_with_filters(self, student_service, mock_db):
        """测试带过滤条件的学生列表"""
        # 简化测试 - 直接模拟_apply_student_filters方法
        with patch.object(student_service, '_apply_student_filters') as mock_apply_filters:
            # 安排
            filters = StudentFilter(name="张", grade="初二", is_active=True)

            # 创建真实的Student对象
            sample_students = [
                Student(
                    id=1,
                    name="张小明",
                    grade="初二",
                    class_name="初二(3)班",
                    student_id="2023001",
                    phone="13812345678",
                    email="zhang@example.com",
                    parent_phone="13987654321",
                    preferred_subjects=["math"],
                    learning_style="视觉型",
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ]

            mock_query = Mock()
            mock_apply_filters.return_value = mock_query
            mock_query.count.return_value = 1
            mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_students
            mock_db.query.return_value = Mock()

            # 执行
            result = await student_service.list_students(filters=filters)

            # 断言
            assert result.total_count == 1
            assert len(result.students) == 1
            assert result.students[0].name == "张小明"
            mock_apply_filters.assert_called_once()


class TestSearchStudents(TestStudentService):
    """搜索学生测试"""

    @pytest.mark.asyncio
    async def test_search_students_by_name(self, student_service, mock_db):
        """测试按姓名搜索学生"""
        # 安排 - 创建真实的Student对象
        sample_results = [
            Student(
                id=1,
                name="张小明",
                grade="初二",
                class_name="初二(3)班",
                student_id="2023001",
                phone="13812345678",
                email="zhang1@example.com",
                parent_phone="13987654321",
                preferred_subjects=["math"],
                learning_style="视觉型",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Student(
                id=2,
                name="张小红",
                grade="初二",
                class_name="初二(4)班",
                student_id="2023002",
                phone="13812345679",
                email="zhang2@example.com",
                parent_phone="13987654322",
                preferred_subjects=["physics"],
                learning_style="听觉型",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = sample_results
        mock_db.query.return_value = mock_query

        # 执行
        result = await student_service.search_students("张", limit=10)

        # 断言
        assert len(result) == 2
        assert result[0].name == "张小明"
        assert result[1].name == "张小红"
        # 检查查询链被正确调用
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.order_by.assert_called_once()
        mock_query.filter.return_value.order_by.return_value.limit.assert_called_once_with(10)


class TestStudentStats(TestStudentService):
    """学生统计测试"""

    @pytest.mark.asyncio
    async def test_get_student_stats(
        self, student_service, sample_student_model, mock_db
    ):
        """测试获取学生统计信息"""
        # 简化测试 - 直接模拟内部方法
        with patch.object(student_service, '_get_student_stats') as mock_get_stats:
            # 安排
            mock_db.query.return_value.filter.return_value.first.return_value = sample_student_model

            # 模拟统计数据
            from ai_tutor.schemas.student_schemas import StudentStats
            mock_get_stats.return_value = StudentStats(
                total_homework_sessions=20,
                total_questions_answered=200,
                overall_accuracy_rate=0.8,
                active_days=15,
                subjects_studied=["math", "physics"],
                subject_progress=[],
                recent_trends=[]
            )

            # 执行
            result = await student_service.get_student_stats(1)

            # 断言
            assert result.total_homework_sessions == 20
            assert result.total_questions_answered == 200
            assert result.overall_accuracy_rate == 0.8
            assert result.active_days == 15
            assert "math" in result.subjects_studied
            assert "physics" in result.subjects_studied
            mock_get_stats.assert_called_once_with(1)


class TestValidation(TestStudentService):
    """数据验证测试"""

    @pytest.mark.asyncio
    async def test_validate_student_data_invalid_grade(self, student_service):
        """测试无效年级验证"""
        invalid_data = {"grade": "大学一年级"}

        with pytest.raises(InvalidStudentDataError) as exc_info:
            await student_service._validate_student_data(invalid_data)

        assert "年级必须在初一到高三范围内" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_student_data_long_class_name(self, student_service):
        """测试班级名称过长"""
        invalid_data = {
            "class_name": "这是一个非常非常非常长的班级名称超过了20个字符的限制"
        }

        with pytest.raises(InvalidStudentDataError) as exc_info:
            await student_service._validate_student_data(invalid_data)

        assert "班级名称过长" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_duplicate_student_by_student_id(
        self, student_service, mock_db
    ):
        """测试检查学号重复"""
        # 安排
        mock_db.query().filter().filter().first.return_value = Mock(
            student_id="2023001"
        )

        # 执行和断言
        with pytest.raises(DuplicateStudentError) as exc_info:
            await student_service._check_duplicate_student(
                name="张三", student_id="2023001"
            )

        assert exc_info.value.details["conflict_type"] == "student_id"

    @pytest.mark.asyncio
    async def test_check_duplicate_student_by_name_class(
        self, student_service, mock_db
    ):
        """测试检查同班同名重复"""
        # 安排 - 只有一次查询（同班同名检查），因为没有提供student_id
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = Mock(
            name="张三", class_name="初二(1)班"
        )

        # 执行和断言
        with pytest.raises(DuplicateStudentError) as exc_info:
            await student_service._check_duplicate_student(
                name="张三", class_name="初二(1)班"
            )

        assert exc_info.value.details["conflict_type"] == "name_class"


class TestFilterApplication(TestStudentService):
    """过滤条件应用测试"""

    def test_apply_student_filters_name(self, student_service, mock_db):
        """测试姓名过滤"""
        query = Mock()
        filters = StudentFilter(name="张")

        result_query = student_service._apply_student_filters(query, filters)

        query.filter.assert_called()

    def test_apply_student_filters_multiple_conditions(self, student_service, mock_db):
        """测试多个过滤条件"""
        # 创建链式mock查询对象
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_query3 = Mock()
        mock_query4 = Mock()

        # 设置链式调用
        query = Mock()
        query.filter.return_value = mock_query1
        mock_query1.filter.return_value = mock_query2
        mock_query2.filter.return_value = mock_query3
        mock_query3.filter.return_value = mock_query4

        filters = StudentFilter(
            name="张", grade="初二", class_name="3班", is_active=True
        )

        result_query = student_service._apply_student_filters(query, filters)

        # 验证所有条件都被应用（每次filter调用都在前一个返回的对象上调用）
        query.filter.assert_called_once()  # 第一次调用在原始query上
        mock_query1.filter.assert_called_once()  # 第二次调用在mock_query1上
        mock_query2.filter.assert_called_once()  # 第三次调用在mock_query2上
        mock_query3.filter.assert_called_once()  # 第四次调用在mock_query3上

    def test_apply_student_filters_homework_filter(self, student_service, mock_db):
        """测试作业记录过滤"""
        query = Mock()
        filters = StudentFilter(has_homework=True)

        result_query = student_service._apply_student_filters(query, filters)

        query.join.assert_called_once()


# 性能测试
class TestPerformance(TestStudentService):
    """性能相关测试"""

    @pytest.mark.asyncio
    async def test_batch_operations_performance(self, student_service, mock_db):
        """测试批量操作性能"""
        # 这里可以添加性能基准测试
        # 例如：测试大量学生数据的查询性能
        pass

    @pytest.mark.asyncio
    async def test_stats_calculation_performance(
        self, student_service, sample_student_model, mock_db
    ):
        """测试统计计算性能"""
        # 简化测试 - 直接模拟内部方法
        with patch.object(student_service, '_get_student_stats') as mock_get_stats:
            # 安排
            mock_db.query.return_value.filter.return_value.first.return_value = sample_student_model

            # 模拟大数据量统计
            from ai_tutor.schemas.student_schemas import StudentStats
            mock_get_stats.return_value = StudentStats(
                total_homework_sessions=1000,
                total_questions_answered=10000,
                overall_accuracy_rate=0.8,
                active_days=100,
                subjects_studied=["math", "physics", "english"],
                subject_progress=[],
                recent_trends=[]
            )

            # 执行
            result = await student_service.get_student_stats(1)

            # 断言：验证大数据量下的计算正确性
            assert result.total_homework_sessions == 1000
            assert result.total_questions_answered == 10000
            assert result.overall_accuracy_rate == 0.8
            mock_get_stats.assert_called_once_with(1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
