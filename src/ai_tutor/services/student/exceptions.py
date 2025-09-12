"""
学生管理相关的自定义异常类
"""


class StudentServiceError(Exception):
    """学生服务基础异常"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class StudentNotFoundError(StudentServiceError):
    """学生未找到异常"""

    def __init__(self, student_id: int = None, student_name: str = None):
        if student_id:
            message = f"学生未找到: ID={student_id}"
            details = {"student_id": student_id}
        elif student_name:
            message = f"学生未找到: 姓名={student_name}"
            details = {"student_name": student_name}
        else:
            message = "学生未找到"
            details = {}
        super().__init__(message, details)


class DuplicateStudentError(StudentServiceError):
    """学生重复异常"""

    def __init__(self, name: str, class_name: str = None, student_id: str = None):
        if student_id:
            message = f"学号重复: {student_id}"
            details = {"student_id": student_id, "conflict_type": "student_id"}
        else:
            message = f"学生重复: {name}"
            if class_name:
                message += f" (班级: {class_name})"
            details = {
                "name": name,
                "class_name": class_name,
                "conflict_type": "name_class",
            }
        super().__init__(message, details)


class InvalidStudentDataError(StudentServiceError):
    """学生数据无效异常"""

    def __init__(self, field: str, value: str = None, reason: str = None):
        message = f"无效的学生数据: {field}"
        if value:
            message += f" ({value})"
        if reason:
            message += f" - {reason}"
        details = {"field": field, "value": value, "reason": reason}
        super().__init__(message, details)


class StudentInactiveError(StudentServiceError):
    """学生非激活状态异常"""

    def __init__(self, student_id: int):
        message = f"学生已停用: ID={student_id}"
        details = {"student_id": student_id}
        super().__init__(message, details)


class DatabaseOperationError(StudentServiceError):
    """数据库操作异常"""

    def __init__(self, operation: str, original_error: Exception = None):
        message = f"数据库操作失败: {operation}"
        details = {"operation": operation}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        super().__init__(message, details)
