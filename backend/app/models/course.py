"""
Course models for EduPredict
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class CourseBase(BaseModel):
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

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class CourseWithStats(Course):
    """Course model with additional statistics"""
    average_grade: Optional[float] = None
    attendance_rate: Optional[float] = None
    completion_rate: Optional[float] = None
    at_risk_students: int = 0
