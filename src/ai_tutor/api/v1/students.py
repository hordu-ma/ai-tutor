"""
学生管理API端点

提供学生信息的完整CRUD操作、分页查询、搜索和学习统计等功能。
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_student_service
from ...schemas.student_schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDetailResponse,
    StudentStats,
    StudentFilter,
    StudentListResponse,
    PaginationParams,
    SubjectProgress,
    LearningTrend,
)
from ...services.student.student_service import StudentService
from ...services.student.progress_service import get_progress_service, ProgressService
from ...services.student.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    DatabaseOperationError,
)
from ...core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/students", tags=["students"])


# 学习进度管理端点
@router.get("/{student_id}/progress/{subject}", response_model=SubjectProgress)
async def get_subject_progress(
    student_id: int = Path(..., description="学生ID"),
    subject: str = Path(..., description="科目名称"),
    timeframe_days: int = Query(30, ge=1, le=365, description="统计时间范围（天）"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> SubjectProgress:
    """
    获取学生在指定科目的学习进度

    - **student_id**: 学生ID
    - **subject**: 科目名称（math/physics/english等）
    - **timeframe_days**: 统计时间范围，默认30天

    返回该科目的详细学习进度，包括：
    - 掌握率
    - 练习题数量统计
    - 近期表现
    - 薄弱知识点列表
    """
    try:
        progress = await progress_service.calculate_subject_progress(
            student_id=student_id,
            subject=subject,
            timeframe_days=timeframe_days
        )
        logger.info(f"获取学生{student_id}的{subject}学习进度成功")
        return progress

    except Exception as e:
        logger.error(f"获取学习进度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取学习进度失败: {str(e)}")


@router.get("/{student_id}/progress/{subject}/trends", response_model=List[LearningTrend])
async def get_learning_trends(
    student_id: int = Path(..., description="学生ID"),
    subject: str = Path(..., description="科目名称"),
    days: int = Query(30, ge=7, le=365, description="统计天数"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[LearningTrend]:
    """
    获取学生学习趋势数据

    - **student_id**: 学生ID
    - **subject**: 科目名称
    - **days**: 统计天数，默认30天

    返回按天聚合的学习趋势数据：
    - 每日准确率变化
    - 练习量统计
    - 平均分数趋势
    """
    try:
        trends = await progress_service.get_learning_trends(
            student_id=student_id,
            subject=subject,
            days=days
        )
        logger.info(f"获取学生{student_id}的{subject}学习趋势成功")
        return trends

    except Exception as e:
        logger.error(f"获取学习趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取学习趋势失败: {str(e)}")


@router.get("/{student_id}/weak-points/{subject}")
async def get_weak_knowledge_points(
    student_id: int = Path(..., description="学生ID"),
    subject: str = Path(..., description="科目名称"),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """
    获取学生薄弱知识点分析

    - **student_id**: 学生ID
    - **subject**: 科目名称

    返回该科目下掌握不足的知识点列表及改进建议
    """
    try:
        recommendations = await progress_service.get_learning_recommendations(
            student_id=student_id,
            subject=subject,
            limit=10
        )
        logger.info(f"获取学生{student_id}的{subject}薄弱知识点成功")
        return {
            "student_id": student_id,
            "subject": subject,
            "recommendations": recommendations
        }

    except Exception as e:
        logger.error(f"获取薄弱知识点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取薄弱知识点失败: {str(e)}")


@router.get("/{student_id}/learning-patterns")
async def get_learning_patterns(
    student_id: int = Path(..., description="学生ID"),
    days: int = Query(30, ge=7, le=365, description="分析天数"),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """
    分析学生学习模式

    - **student_id**: 学生ID
    - **days**: 分析天数，默认30天

    返回学习模式分析结果：
    - 学习时间偏好
    - 学习一致性
    - 科目偏好分析
    - 学习效果评估
    """
    try:
        patterns = await progress_service.analyze_learning_patterns(
            student_id=student_id,
            days=days
        )
        logger.info(f"分析学生{student_id}学习模式成功")
        return {
            "student_id": student_id,
            "analysis_period_days": days,
            "patterns": patterns
        }

    except Exception as e:
        logger.error(f"分析学习模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析学习模式失败: {str(e)}")


@router.post("/{student_id}/knowledge-progress/{knowledge_point_id}")
async def update_knowledge_progress(
    student_id: int = Path(..., description="学生ID"),
    knowledge_point_id: int = Path(..., description="知识点ID"),
    is_correct: bool = Query(..., description="本次练习是否正确"),
    confidence_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="置信度分数"),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """
    更新学生知识点掌握进度

    - **student_id**: 学生ID
    - **knowledge_point_id**: 知识点ID
    - **is_correct**: 本次练习是否正确
    - **confidence_score**: 置信度分数（可选）

    用于在学生完成练习后更新对应知识点的掌握进度
    """
    try:
        await progress_service.update_knowledge_progress(
            student_id=student_id,
            knowledge_point_id=knowledge_point_id,
            is_correct=is_correct,
            confidence_score=confidence_score
        )
        logger.info(f"更新学生{student_id}知识点{knowledge_point_id}进度成功")
        return {
            "success": True,
            "message": "知识点进度更新成功",
            "student_id": student_id,
            "knowledge_point_id": knowledge_point_id
        }

    except Exception as e:
        logger.error(f"更新知识点进度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新知识点进度失败: {str(e)}")


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(
    student_data: StudentCreate,
    student_service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    """
    创建新学生

    - **name**: 学生姓名（必填）
    - **grade**: 年级（必填，限制为初一到高三）
    - **class_name**: 班级名称（可选）
    - **student_id**: 学号（可选，如提供必须唯一）
    - **phone**: 手机号（可选，需符合格式）
    - **email**: 邮箱（可选，需符合格式）
    - **parent_phone**: 家长手机号（可选）
    - **preferred_subjects**: 偏好科目列表（可选）
    - **learning_style**: 学习风格（可选）
    """
    try:
        logger.info("创建学生请求", name=student_data.name, grade=student_data.grade)
        result = await student_service.create_student(student_data)
        logger.info("学生创建成功", student_id=result.id, name=result.name)
        return result
    except DuplicateStudentError as e:
        logger.warning("学生重复创建失败", error=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidStudentDataError as e:
        logger.warning("学生数据无效", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseOperationError as e:
        logger.error("数据库操作失败", error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student(
    student_id: int = Path(..., description="学生ID", gt=0),
    include_stats: bool = Query(False, description="是否包含学习统计信息"),
    student_service: StudentService = Depends(get_student_service),
) -> StudentDetailResponse:
    """
    获取学生详细信息

    - **student_id**: 学生ID
    - **include_stats**: 是否包含详细统计信息（作业记录、学习趋势等）
    """
    try:
        logger.info("获取学生信息", student_id=student_id, include_stats=include_stats)
        result = await student_service.get_student(student_id, include_stats=include_stats)
        return result
    except StudentNotFoundError as e:
        logger.warning("学生未找到", student_id=student_id)
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        logger.error("获取学生信息失败", student_id=student_id, error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int = Path(..., description="学生ID", gt=0),
    student_data: StudentUpdate = ...,
    student_service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    """
    更新学生信息

    - **student_id**: 学生ID
    - 只更新提供的字段，其他字段保持不变
    - 如果更新姓名、班级或学号，会自动检查重复
    """
    try:
        logger.info("更新学生信息", student_id=student_id)
        result = await student_service.update_student(student_id, student_data)
        logger.info("学生信息更新成功", student_id=student_id)
        return result
    except StudentNotFoundError as e:
        logger.warning("待更新学生未找到", student_id=student_id)
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateStudentError as e:
        logger.warning("更新导致学生重复", student_id=student_id, error=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidStudentDataError as e:
        logger.warning("更新数据无效", student_id=student_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseOperationError as e:
        logger.error("更新学生信息失败", student_id=student_id, error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: int = Path(..., description="学生ID", gt=0),
    hard_delete: bool = Query(False, description="是否硬删除（彻底删除记录）"),
    student_service: StudentService = Depends(get_student_service),
):
    """
    删除学生

    - **student_id**: 学生ID
    - **hard_delete**: False为软删除（推荐），True为硬删除（谨慎使用）
    - 软删除会保留学生记录但设置为非活跃状态
    - 硬删除会彻底删除学生记录（不可恢复）
    """
    try:
        logger.info("删除学生请求", student_id=student_id, hard_delete=hard_delete)
        await student_service.delete_student(student_id, soft_delete=not hard_delete)
        logger.info("学生删除成功", student_id=student_id, hard_delete=hard_delete)
    except StudentNotFoundError as e:
        logger.warning("待删除学生未找到", student_id=student_id)
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        logger.error("删除学生失败", student_id=student_id, error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("", response_model=StudentListResponse)
async def list_students(
    # 分页参数
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    # 筛选参数
    name: Optional[str] = Query(None, description="按姓名筛选（模糊匹配）"),
    grade: Optional[str] = Query(None, description="按年级筛选"),
    class_name: Optional[str] = Query(None, description="按班级筛选（模糊匹配）"),
    is_active: Optional[bool] = Query(None, description="按活跃状态筛选"),
    has_homework: Optional[bool] = Query(None, description="是否有作业记录"),
    student_service: StudentService = Depends(get_student_service),
) -> StudentListResponse:
    """
    获取学生列表（支持分页和筛选）

    - **分页参数**: page（页码）, page_size（每页数量，最大100）
    - **筛选条件**: 姓名、年级、班级、活跃状态、是否有作业记录
    - **排序**: 按创建时间倒序
    """
    try:
        # 构建筛选条件
        filters = StudentFilter(
            name=name,
            grade=grade,
            class_name=class_name,
            is_active=is_active,
            has_homework=has_homework,
        )

        # 构建分页参数
        pagination = PaginationParams(page=page, page_size=page_size)

        logger.info("查询学生列表", page=page, page_size=page_size, filters=filters.model_dump(exclude_none=True))

        result = await student_service.list_students(filters=filters, pagination=pagination)

        logger.info("查询学生列表成功", total_count=result.total_count, page_count=len(result.students))
        return result

    except DatabaseOperationError as e:
        logger.error("查询学生列表失败", error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/search", response_model=List[StudentResponse])
async def search_students(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(20, description="结果数量限制", ge=1, le=100),
    student_service: StudentService = Depends(get_student_service),
) -> List[StudentResponse]:
    """
    搜索学生（按姓名、学号、班级）

    - **keyword**: 搜索关键词，会在姓名、学号、班级中进行模糊匹配
    - **limit**: 返回结果数量限制（最大100）
    - 只返回活跃状态的学生
    """
    try:
        logger.info("搜索学生", keyword=keyword, limit=limit)
        result = await student_service.search_students(keyword, limit=limit)
        logger.info("搜索学生完成", keyword=keyword, result_count=len(result))
        return result
    except DatabaseOperationError as e:
        logger.error("搜索学生失败", keyword=keyword, error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/{student_id}/stats", response_model=StudentStats)
async def get_student_stats(
    student_id: int = Path(..., description="学生ID", gt=0),
    student_service: StudentService = Depends(get_student_service),
) -> StudentStats:
    """
    获取学生学习统计信息

    - **student_id**: 学生ID
    - 返回详细的学习统计数据：
      - 总作业次数、总题目数、正确率
      - 活跃天数、已学习科目
      - 各科目掌握度和进度
      - 最近学习趋势
    """
    try:
        logger.info("获取学生统计", student_id=student_id)
        result = await student_service.get_student_stats(student_id)
        logger.info("获取学生统计成功", student_id=student_id)
        return result
    except StudentNotFoundError as e:
        logger.warning("学生统计查询失败，学生未找到", student_id=student_id)
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseOperationError as e:
        logger.error("获取学生统计失败", student_id=student_id, error=str(e))
        raise HTTPException(status_code=500, detail="服务器内部错误")
