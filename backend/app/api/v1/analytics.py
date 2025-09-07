from fastapi import APIRouter, Depends, HTTPException, status
from app.services.analytics_service import AnalyticsService, get_analytics_service
from app.models.student import StudentAnalytics
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard-stats/{role}")
async def get_dashboard_stats(role: str):
    """Get dashboard statistics for a specific role"""
    try:
        # Mock data for different roles
        if role == "student":
            return {
                "current_gpa": 3.2,
                "semester_gpa": 3.4,
                "total_credits": 75,
                "completed_credits": 60,
                "attendance_rate": 87,
                "risk_level": "low",
                "courses_enrolled": 5
            }
        elif role == "teacher":
            return {
                "totalStudents": 120,
                "atRiskStudents": 8,
                "averageAttendance": 87,
                "averageGPA": 3.1,
                "activeClasses": 4
            }
        elif role == "admin":
            return {
                "total_users": 250,
                "active_students": 200,
                "total_teachers": 15,
                "active_courses": 25,
                "average_gpa": 3.2,
                "attendance_rate": 85,
                "at_risk_students": 12
            }
        else:
            return {}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/dropout-prediction/{student_id}")
async def get_dropout_prediction(student_id: str):
    """Get dropout prediction for a student"""
    try:
        return {
            "student_id": student_id,
            "risk_score": 0.25,
            "risk_level": "low",
            "factors": [
                {"name": "Attendance Rate", "score": 0.15, "impact": "positive"},
                {"name": "GPA Trend", "score": 0.10, "impact": "positive"}
            ],
            "recommendations": [
                {"title": "Keep up the good work", "description": "Continue your excellent performance", "priority": "low"},
                {"title": "Study Group", "description": "Join study groups for better collaboration", "priority": "medium"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/grade-predictions/{student_id}")
async def get_grade_predictions(student_id: str):
    """Get grade predictions for a student"""
    try:
        return {
            "student_id": student_id,
            "overall_predicted_gpa": 3.4,
            "predictions": [
                {"course": "Computer Science 101", "current": "B+", "predicted": "A-", "confidence": 92},
                {"course": "Mathematics 201", "current": "B", "predicted": "B+", "confidence": 87},
                {"course": "Physics 101", "current": "B-", "predicted": "B", "confidence": 78}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/performance-trends/{student_id}")
async def get_performance_trends(student_id: str):
    """Get performance trends for a student"""
    try:
        return {
            "student_id": student_id,
            "grade_trends": [
                {"semester": "Fall 2022", "gpa": 2.8, "credits": 15},
                {"semester": "Spring 2023", "gpa": 3.0, "credits": 16},
                {"semester": "Fall 2023", "gpa": 3.2, "credits": 18}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/institution-analytics")
async def get_institution_analytics():
    """Get institution-wide analytics"""
    try:
        return {
            "department_distribution": [
                {"name": "Computer Science", "count": 80},
                {"name": "Mathematics", "count": 45},
                {"name": "Physics", "count": 35}
            ],
            "grade_distribution": {"A": 25, "B": 35, "C": 25, "D": 10, "F": 5},
            "gpa_trends": [
                {"month": "Jan", "gpa": 3.1, "attendance": 85},
                {"month": "Feb", "gpa": 3.2, "attendance": 87},
                {"month": "Mar", "gpa": 3.1, "attendance": 83}
            ],
            "top_courses": [
                {"name": "Computer Science 101", "code": "CS-101", "average_gpa": 3.5, "student_count": 30},
                {"name": "Mathematics 201", "code": "MATH-201", "average_gpa": 3.2, "student_count": 25}
            ],
            "risk_factors": [
                {"name": "Low Attendance", "percentage": 15},
                {"name": "Poor Assignment Completion", "percentage": 12}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/at-risk-students")
async def get_at_risk_students(limit: int = 20):
    """Get list of at-risk students"""
    try:
        return [
            {
                "student_id": "STU003",
                "student_name": "Mike Johnson",
                "gpa": 2.1,
                "attendance_rate": 65,
                "risk_level": "high",
                "risk_factors": ["Low GPA", "Poor Attendance"]
            },
            {
                "student_id": "STU009",
                "student_name": "Kevin Moore",
                "gpa": 1.8,
                "attendance_rate": 55,
                "risk_level": "high",
                "risk_factors": ["Very Low GPA", "Very Poor Attendance"]
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}", response_model=StudentAnalytics, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST]))])
async def get_student_analytics(student_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    """
    Retrieve comprehensive analytics for a student (Admin/Analyst only)
    
    Args:
        student_id: Unique student ID (e.g., STU-1234)
        service: Analytics service dependency
    
    Returns:
        Student analytics data
    
    Raises:
        HTTPException: If student not found or server error
    """
    try:
        return await service.generate_student_analytics(student_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))