"""
API router configuration for EduPredict v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, students, courses, attendance, grades, analytics, notifications

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(grades.router, prefix="/grades", tags=["grades"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
