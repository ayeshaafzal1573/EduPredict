"""
Analytics and prediction endpoints for EduPredict
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List
from app.models.user import TokenData
from app.core.security import get_current_user
from app.services.analytics_service import AnalyticsService
from app.services.ml_service import MLService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

analytics_service = AnalyticsService()
ml_service = MLService()

@router.get("/dropout-prediction/{student_id}")
async def get_dropout_prediction(
    student_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dropout risk prediction for student"""
    try:
        logger.info(f"Getting dropout prediction for student: {student_id}")
        prediction = await ml_service.predict_dropout_risk(student_id)
        return prediction
    except Exception as e:
        logger.error(f"Failed to get dropout prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate dropout prediction"
        )

@router.get("/dashboard-stats/{role}")
async def get_dashboard_stats(
    role: str,
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard statistics for specific role"""
    try:
        logger.info(f"Fetching dashboard stats for role: {role}")
        stats = await analytics_service.get_dashboard_stats(role, current_user.sub)
        return stats
    except Exception as e:
        logger.error(f"Failed to fetch dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )

@router.get("/grade-predictions/{student_id}")
async def get_grade_predictions(
    student_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get grade predictions for a student's courses"""
    try:
        logger.info(f"Getting grade predictions for student: {student_id}")
        predictions = await ml_service.predict_grades(student_id)
        return predictions
    except Exception as e:
        logger.error(f"Failed to get grade predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get grade predictions"
        )

@router.get("/performance-trends/{student_id}")
async def get_performance_trends(
    student_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get performance trends for a student"""
    try:
        logger.info(f"Getting performance trends for student: {student_id}")
        trends = await analytics_service.get_performance_trends(student_id)
        return trends
    except Exception as e:
        logger.error(f"Failed to get performance trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance trends"
        )

@router.get("/class-analytics/{class_id}")
async def get_class_analytics(
    class_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get analytics for a specific class"""
    try:
        logger.info(f"Getting class analytics for class: {class_id}")
        analytics = await analytics_service.get_class_analytics(class_id)
        return analytics
    except Exception as e:
        logger.error(f"Failed to get class analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get class analytics"
        )
