from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from app.models.base import PyObjectId, MongoBaseModel


class CourseBase(MongoBaseModel):
    """Base course model"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    department: Optional[str] = Field(None, max_length=100)
    credits: int = Field(..., ge=1, le=10)
    semester: str = Field(..., min_length=1, max_length=50)
    academic_year: str = Field(..., min_length=4, max_length=20)
    schedule: Optional[str] = Field(None, max_length=200)
    room: Optional[str] = Field(None, max_length=100)
    max_students: Optional[int] = Field(None, ge=1, le=500)

    @validator("code")
    def validate_code(cls, v):
        """Ensure course code follows a specific format (e.g., CS-101)"""
        if not v.replace("-", "").isalnum():
            raise ValueError("Course code must be alphanumeric with optional hyphens")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    department: Optional[str] = Field(None, max_length=100)
    credits: Optional[int] = Field(None, ge=1, le=10)
    semester: Optional[str] = Field(None, min_length=1, max_length=50)
    academic_year: Optional[str] = Field(None, min_length=4, max_length=20)
    schedule: Optional[str] = Field(None, max_length=200)
    room: Optional[str] = Field(None, max_length=100)
    max_students: Optional[int] = Field(None, ge=1, le=500)
    is_active: Optional[bool] = None


class Course(CourseBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    teacher_id: str
    teacher_name: Optional[str] = None
    students: List[str] = Field(default_factory=list)
    student_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CourseWithStats(Course):
    """Course model with additional statistics"""
    average_grade: Optional[float] = None
    attendance_rate: Optional[float] = None
    completion_rate: Optional[float] = None
    at_risk_students: int = 0
    hdfs_path: Optional[str] = None  # Path to HDFS storage for course data