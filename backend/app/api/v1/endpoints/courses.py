from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
import logging

from app.models.user import TokenData, UserRole
from app.models.course import Course, CourseCreate, CourseUpdate
from app.services.course_service import CourseService
from app.core.security import get_current_user
from app.core.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter()


# ---- Dependency Provider ----
def get_course_service(db=Depends(get_database)):
    return CourseService(db)


def teacher_or_admin_required(user: TokenData):
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Teacher or Admin role required")


def admin_required(user: TokenData):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")


@router.post("/", response_model=Course)
async def create_course(
    course_data: CourseCreate,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    teacher_or_admin_required(current_user)
    try:
        return await service.create_course(course_data, current_user.sub)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[Course])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    teacher_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    try:
        if current_user.role == UserRole.STUDENT:
            return await service.get_student_courses(current_user.sub, skip, limit)
        elif current_user.role == UserRole.TEACHER:
            return await service.get_courses(skip, limit, teacher_id or current_user.sub)
        else:  # admin
            return await service.get_courses(skip, limit, teacher_id)
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve courses")


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    try:
        course = await service.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Role-based access
        if current_user.role == UserRole.STUDENT and current_user.sub not in course.students:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
        if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.sub:
            raise HTTPException(status_code=403, detail="Not the instructor of this course")

        return course
    except Exception as e:
        logger.error(f"Error fetching course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve course")


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    teacher_or_admin_required(current_user)
    try:
        return await service.update_course(course_id, course_update)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update course")


@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    admin_required(current_user)
    try:
        success = await service.delete_course(course_id)
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"message": "Course deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete course")


@router.post("/{course_id}/enroll/{student_id}")
async def enroll_student(
    course_id: str,
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    teacher_or_admin_required(current_user)
    try:
        success = await service.enroll_student(course_id, student_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to enroll student")
        return {"message": "Student enrolled successfully"}
    except Exception as e:
        logger.error(f"Error enrolling student {student_id} to course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to enroll student")


@router.delete("/{course_id}/enroll/{student_id}")
async def unenroll_student(
    course_id: str,
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    teacher_or_admin_required(current_user)
    try:
        success = await service.unenroll_student(course_id, student_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unenroll student")
        return {"message": "Student unenrolled successfully"}
    except Exception as e:
        logger.error(f"Error unenrolling student {student_id} from course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unenroll student")


@router.get("/{course_id}/students")
async def get_course_students(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    teacher_or_admin_required(current_user)
    try:
        students = await service.get_course_students(course_id)
        return students
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching students for course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve course students")
