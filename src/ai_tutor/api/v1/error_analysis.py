"""
错误分析API路由
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...services.error_analysis import get_error_analysis_service, ErrorPatternService
from ...schemas.error_analysis import (
    ErrorAnalysisRequest,
    ErrorPatternAnalysis,
    ErrorTrendAnalysis
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/error-analysis",
    tags=["错误分析"]
)


@router.get("/students/{student_id}/patterns/{subject}")
async def get_error_patterns(
    student_id: int,
    subject: str,
    timeframe_days: int = Query(30, ge=1, le=365, description="分析时间范围（天）"),
    include_recommendations: bool = Query(True, description="是否包含改进建议"),
    service: ErrorPatternService = Depends(get_error_analysis_service)
) -> ErrorPatternAnalysis:
    """
    获取学生错误模式分析

    - **student_id**: 学生ID
    - **subject**: 科目 (math, physics, english等)
    - **timeframe_days**: 分析时间范围（天），默认30天
    - **include_recommendations**: 是否包含改进建议，默认true
    """
    try:
        logger.info(f"获取学生 {student_id} 的 {subject} 错误模式分析")

        # 验证科目并转换为大写
        valid_subjects = ["math", "physics", "english", "chinese", "chemistry", "biology"]
        if subject.lower() not in valid_subjects:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的科目: {subject}。支持的科目: {', '.join(valid_subjects)}"
            )

        # 转换为大写格式以匹配数据库枚举
        subject_upper = subject.upper()

        # 执行分析
        analysis = await service.analyze_student_error_patterns(
            student_id=student_id,
            subject=subject_upper,
            timeframe_days=timeframe_days
        )

        # 如果不需要建议，清空建议字段
        if not include_recommendations:
            analysis.improvement_recommendations = []

        logger.info(f"成功分析学生 {student_id} 的错误模式，发现 {len(analysis.systematic_errors)} 个系统性错误")
        return analysis

    except Exception as e:
        logger.error(f"分析错误模式失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")




@router.get("/students/{student_id}/trends/{subject}")
async def get_error_trends(
    student_id: int,
    subject: str,
    days: int = Query(30, ge=7, le=365, description="分析天数"),
    service: ErrorPatternService = Depends(get_error_analysis_service)
) -> ErrorTrendAnalysis:
    """
    获取学生错误趋势分析

    - **student_id**: 学生ID
    - **subject**: 科目
    - **days**: 分析天数，默认30天
    """
    try:
        logger.info(f"获取学生 {student_id} 的 {subject} 错误趋势分析，{days}天")

        # 转换为大写格式以匹配数据库枚举
        subject_upper = subject.upper()

        analysis = await service.get_error_trends(
            student_id=student_id,
            subject=subject_upper,
            days=days
        )

        logger.info(f"错误趋势分析完成，总体趋势: {analysis.overall_trend}")
        return analysis

    except Exception as e:
        logger.error(f"错误趋势分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/students/{student_id}/summary")
async def get_error_summary(
    student_id: int,
    subjects: List[str] = Query(None, description="科目列表，不指定则包含所有科目"),
    timeframe_days: int = Query(30, ge=1, le=365, description="时间范围（天）"),
    service: ErrorPatternService = Depends(get_error_analysis_service)
) -> dict:
    """
    获取学生多科目错误总结

    - **student_id**: 学生ID
    - **subjects**: 科目列表（可选）
    - **timeframe_days**: 时间范围（天）
    """
    try:
        logger.info(f"获取学生 {student_id} 的多科目错误总结")

        # 如果没有指定科目，使用默认科目列表
        if not subjects:
            subjects = ["math", "physics", "english"]

        summary = {}
        total_errors = 0
        total_questions = 0

        # 分别分析每个科目
        for subject in subjects:
            try:
                # 转换为大写格式以匹配数据库枚举
                subject_upper = subject.upper()

                analysis = await service.analyze_student_error_patterns(
                    student_id=student_id,
                    subject=subject_upper,
                    timeframe_days=timeframe_days
                )

                summary[subject] = {
                    "error_rate": analysis.error_rate,
                    "total_errors": analysis.total_errors,
                    "total_questions": analysis.total_questions,
                    "systematic_errors_count": len(analysis.systematic_errors),
                    "top_error_type": max(
                        analysis.error_type_distribution.items(),
                        key=lambda x: x[1]
                    )[0] if analysis.error_type_distribution else "无",
                    "improvement_trend": analysis.progress_indicators.get("improvement_trend", "unknown")
                }

                total_errors += analysis.total_errors
                total_questions += analysis.total_questions

            except Exception as e:
                logger.warning(f"分析科目 {subject} 失败: {e}")
                summary[subject] = {"error": str(e)}

        # 计算总体统计
        overall_error_rate = total_errors / total_questions if total_questions > 0 else 0

        return {
            "student_id": student_id,
            "analysis_period": f"最近{timeframe_days}天",
            "overall_error_rate": round(overall_error_rate, 3),
            "total_errors": total_errors,
            "total_questions": total_questions,
            "subjects_analysis": summary,
            "generated_at": "2024-01-15T10:00:00"  # 简化实现
        }

    except Exception as e:
        logger.error(f"多科目错误总结失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/health")
async def health_check():
    """错误分析服务健康检查"""
    try:
        service = get_error_analysis_service()
        return {
            "status": "healthy",
            "service": "ErrorPatternService",
            "message": "错误分析服务运行正常"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "ErrorPatternService",
            "error": str(e)
        }


@router.get("/error-types")
async def get_error_types():
    """获取支持的错误类型列表"""
    return {
        "error_types": [
            {
                "code": "calculation_error",
                "name": "计算错误",
                "description": "数学计算过程中的错误",
                "subjects": ["math", "physics", "chemistry"]
            },
            {
                "code": "concept_confusion",
                "name": "概念混淆",
                "description": "对基础概念理解有误",
                "subjects": ["math", "physics", "chemistry", "biology"]
            },
            {
                "code": "formula_misuse",
                "name": "公式误用",
                "description": "公式使用不当或条件不符",
                "subjects": ["math", "physics", "chemistry"]
            },
            {
                "code": "grammar_error",
                "name": "语法错误",
                "description": "语法使用错误",
                "subjects": ["english", "chinese"]
            },
            {
                "code": "vocabulary_error",
                "name": "词汇错误",
                "description": "词汇选择或使用错误",
                "subjects": ["english"]
            }
        ]
    }


@router.get("/students/{student_id}/improvement-plan/{subject}")
async def get_improvement_plan(
    student_id: int,
    subject: str,
    timeframe_days: int = Query(30, description="分析时间范围"),
    service: ErrorPatternService = Depends(get_error_analysis_service)
) -> dict:
    """
    获取个性化改进计划

    - **student_id**: 学生ID
    - **subject**: 科目
    - **timeframe_days**: 分析时间范围
    """
    try:
        logger.info(f"生成学生 {student_id} 的 {subject} 改进计划")

        # 转换为大写格式以匹配数据库枚举
        subject_upper = subject.upper()

        # 获取错误模式分析
        analysis = await service.analyze_student_error_patterns(
            student_id=student_id,
            subject=subject_upper,
            timeframe_days=timeframe_days
        )

        # 生成改进计划
        plan = {
            "student_id": student_id,
            "subject": subject,
            "current_performance": {
                "error_rate": analysis.error_rate,
                "total_questions": analysis.total_questions,
                "systematic_errors": len(analysis.systematic_errors)
            },
            "improvement_goals": [
                "将错误率降低到20%以下",
                "掌握核心概念和方法",
                "提高答题准确性"
            ],
            "action_plan": [
                {
                    "week": 1,
                    "focus": "基础概念复习",
                    "tasks": ["完成基础练习20题", "观看相关视频教程"],
                    "target": "概念理解度提升至80%"
                },
                {
                    "week": 2,
                    "focus": "错误类型专项训练",
                    "tasks": ["针对性练习", "错误总结和反思"],
                    "target": "主要错误类型改进50%"
                }
            ],
            "recommendations": analysis.improvement_recommendations,
            "estimated_duration": "2-4周",
            "success_criteria": [
                "连续10题准确率达到90%",
                "无系统性错误出现",
                "概念理解测试通过"
            ]
        }

        return plan

    except Exception as e:
        logger.error(f"生成改进计划失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
