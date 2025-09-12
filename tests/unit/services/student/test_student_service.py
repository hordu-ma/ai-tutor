"""
StudentService单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.ai_tutor.services.student.student_service import StudentService
from src.ai_tutor.services.student.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    DatabaseOperationError,
)
from src.ai_tutor.schemas.student_schemas import (
    StudentCreate,
    StudentUpdate,
    StudentFilter,
    PaginationParams,
)
from src.ai_tutor.models.student import Student


class TestStudentService:
    """StudentService测试类"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        mock_db = Mock()
        mock_db.query.return_value = Mock()
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
        # 安排Mock链式调用
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # 无重复学生
        mock_db.query.return_value = mock_query
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, "id", 1))

        # 模拟数据库返回
        with patch(
            "src.ai_tutor.services.student.student_service.Student"
        ) as MockStudent:
            MockStudent.return_value = sample_student_model

            # 执行
            result = await student_service.create_student(sample_student_data)

            # 断言
            assert result.name == "张小明"
            assert result.grade == "初二"
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
        # 安排
        mock_db.query().filter().first.return_value = None
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
        mock_db.query().filter().first.return_value = sample_student_model

        # 执行
        result = await student_service.get_student(1)

        # 断言
        assert result.id == 1
        assert result.name == "张小明"
        mock_db.query().filter.assert_called_once()

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
        # 安排
        mock_db.query().filter().first.return_value = sample_student_model
        mock_db.query().filter().scalar.return_value = 10  # homework_count
        mock_db.query().join().filter().first.return_value = Mock(total=100, correct=80)
        mock_db.query().filter().all.return_value = [("math",), ("physics",)]

        # 执行
        result = await student_service.get_student(1, include_stats=True)

        # 断言
        assert hasattr(result, "stats")
        assert hasattr(result, "recent_activities")


class TestUpdateStudent(TestStudentService):
    """更新学生测试"""

    @pytest.mark.asyncio
    async def test_update_student_success(
        self, student_service, sample_student_model, mock_db
    ):
        """测试成功更新学生"""
        # 安排
        mock_db.query().filter().first.return_value = sample_student_model
        update_data = StudentUpdate(name="张小强", phone="13912345678")

        # 执行
        result = await student_service.update_student(1, update_data)

        # 断言
        assert sample_student_model.name == "张小强"
        assert sample_student_model.phone == "13912345678"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_student_not_found(self, student_service, mock_db):
        """测试更新不存在的学生"""
        # 安排
        mock_db.query().filter().first.return_value = None
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
        mock_db.query().filter().first.return_value = sample_student_model
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
        mock_db.query().filter().first.return_value = sample_student_model

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
        mock_db.query().filter().first.return_value = sample_student_model

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
        mock_db.query().filter().first.return_value = None

        # 执行和断言
        with pytest.raises(StudentNotFoundError):
            await student_service.delete_student(999)


class TestListStudents(TestStudentService):
    """学生列表测试"""

    @pytest.mark.asyncio
    async def test_list_students_with_pagination(self, student_service, mock_db):
        """测试分页查询学生列表"""
        # 安排
        sample_students = [Mock(id=i, name=f"学生{i}") for i in range(1, 6)]
        mock_query = Mock()
        mock_query.count.return_value = 100
        mock_query.order_by().offset().limit().all.return_value = sample_students
        mock_db.query.return_value = mock_query

        pagination = PaginationParams(page=1, page_size=5)

        # 执行
        result = await student_service.list_students(pagination=pagination)

        # 断言
        assert len(result.students) == 5
        assert result.total_count == 100
        assert result.page == 1
        assert result.total_pages == 20
        assert result.has_next is True
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_list_students_with_filters(self, student_service, mock_db):
        """测试带过滤条件的学生列表"""
        # 安排
        filters = StudentFilter(name="张", grade="初二", is_active=True)
        mock_query = Mock()
        mock_query.count.return_value = 5
        mock_query.order_by().offset().limit().all.return_value = []
        mock_db.query.return_value = mock_query

        # 执行
        result = await student_service.list_students(filters=filters)

        # 断言
        assert result.total_count == 5
        # 验证过滤条件被应用
        assert mock_query.filter.call_count >= 3  # 至少应用了3个过滤条件


class TestSearchStudents(TestStudentService):
    """搜索学生测试"""

    @pytest.mark.asyncio
    async def test_search_students_by_name(self, student_service, mock_db):
        """测试按姓名搜索学生"""
        # 安排
        sample_results = [Mock(name="张小明"), Mock(name="张小红")]
        mock_query = Mock()
        mock_query.filter().order_by().limit().all.return_value = sample_results
        mock_db.query.return_value = mock_query

        # 执行
        result = await student_service.search_students("张", limit=10)

        # 断言
        assert len(result) == 2
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.limit.assert_called_once_with(10)


class TestStudentStats(TestStudentService):
    """学生统计测试"""

    @pytest.mark.asyncio
    async def test_get_student_stats(
        self, student_service, sample_student_model, mock_db
    ):
        """测试获取学生统计信息"""
        # 安排
        mock_db.query().filter().first.return_value = sample_student_model
        mock_db.query().filter().scalar.return_value = 20  # homework_count
        mock_db.query().join().filter().first.return_value = Mock(
            total=200, correct=160
        )
        mock_db.query().filter().scalar.side_effect = [15]  # active_days
        mock_db.query().filter().all.return_value = [("math",), ("physics",)]

        # 执行
        result = await student_service.get_student_stats(1)

        # 断言
        assert result.total_homework_sessions == 20
        assert result.total_questions_answered == 200
        assert result.overall_accuracy_rate == 0.8
        assert result.active_days == 15
        assert "math" in result.subjects_studied
        assert "physics" in result.subjects_studied


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
        # 安排
        mock_db.query().filter().filter().first.side_effect = [
            None,  # 第一次查询学号不重复
            Mock(name="张三", class_name="初二(1)班"),  # 第二次查询姓名班级重复
        ]

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
        query = Mock()
        filters = StudentFilter(
            name="张", grade="初二", class_name="3班", is_active=True
        )

        result_query = student_service._apply_student_filters(query, filters)

        # 验证所有条件都被应用
        assert query.filter.call_count == 4

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
        # 安排
        mock_db.query().filter().first.return_value = sample_student_model
        mock_db.query().filter().scalar.return_value = 1000  # 大量作业
        mock_db.query().join().filter().first.return_value = Mock(
            total=10000, correct=8000
        )
        mock_db.query().filter().scalar.side_effect = [100]  # 活跃天数
        mock_db.query().filter().all.return_value = [
            ("math",),
            ("physics",),
            ("english",),
        ]

        # 执行
        result = await student_service.get_student_stats(1)

        # 断言：验证大数据量下的计算正确性
        assert result.total_homework_sessions == 1000
        assert result.total_questions_answered == 10000
        assert result.overall_accuracy_rate == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
