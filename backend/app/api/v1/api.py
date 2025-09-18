from fastapi import APIRouter
from app.api.v1 import students, courses, attendance, grades, analytics, notifications, auth, users, data

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router, prefix="/users")
api_router.include_router(students.router)
api_router.include_router(courses.router)
api_router.include_router(attendance.router)
api_router.include_router(grades.router)
api_router.include_router(analytics.router)
api_router.include_router(notifications.router)
api_router.include_router(data.router)