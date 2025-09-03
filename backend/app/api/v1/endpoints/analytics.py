"""
Analytics and prediction endpoints for EduPredict
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List
from app.models.user import TokenData
from app.core.security import get_current_user
from app.services.analytics_service import AnalyticsService
from app.services.ml_service import MLService
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ✅ Dependency injectors
def get_analytics_service(db=Depends(get_database)) -> AnalyticsService:
    return AnalyticsService(db)


def get_ml_service(db=Depends(get_database)) -> MLService:
    return MLService(db)


@router.get("/dashboard-stats/{role}")
async def get_dashboard_stats(
    role: str,
    current_user: TokenData = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """Get dashboard statistics for a specific role"""
    return await analytics_service.get_dashboard_stats(role, current_user.sub)


@router.get("/dropout-prediction/{student_id}")
async def get_dropout_prediction(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """Get dropout risk prediction for a student"""
    return await ml_service.predict_dropout_risk(student_id)


@router.get("/institution-analytics")
async def get_institution_analytics(
    current_user: TokenData = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """Get institution-wide analytics"""
    return await analytics_service.get_institution_analytics()


@router.get("/at-risk-students")
async def get_at_risk_students(
    current_user: TokenData = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> List[Dict[str, Any]]:
    """Get list of at-risk students"""
    return await analytics_service.get_at_risk_students()


@router.get("/grade-predictions/{student_id}")
async def get_grade_predictions(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """Get grade predictions for a student's courses"""
    return await ml_service.predict_grades(student_id)


@router.get("/performance-trends/{student_id}")
async def get_performance_trends(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """Get performance trends for a student"""
    return await analytics_service.get_performance_trends(student_id)


@router.get("/class-analytics/{class_id}")
async def get_class_analytics(
    class_id: str,
    current_user: TokenData = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """Get analytics for a specific class"""
    return await analytics_service.get_class_analytics(class_id)
