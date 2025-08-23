"""
Grade models for EduPredict
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

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

class GradeType(str, Enum):
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PARTICIPATION = "participation"
    MIDTERM = "midterm"
    FINAL = "final"

class GradeBase(BaseModel):
    student_id: str
    course_id: str
    assignment_name: str = Field(..., min_length=1, max_length=200)
    grade_type: GradeType
    points_earned: float = Field(..., ge=0)
    points_possible: float = Field(..., gt=0)
    percentage: Optional[float] = Field(None, ge=0, le=100)
    letter_grade: Optional[str] = Field(None, max_length=5)
    grade_points: Optional[float] = Field(None, ge=0, le=4.0)
    weight: float = Field(1.0, ge=0, le=1.0)  # Weight in course grade calculation
    notes: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    assignment_name: Optional[str] = Field(None, min_length=1, max_length=200)
    grade_type: Optional[GradeType] = None
    points_earned: Optional[float] = Field(None, ge=0)
    points_possible: Optional[float] = Field(None, gt=0)
    percentage: Optional[float] = Field(None, ge=0, le=100)
    letter_grade: Optional[str] = Field(None, max_length=5)
    grade_points: Optional[float] = Field(None, ge=0, le=4.0)
    weight: Optional[float] = Field(None, ge=0, le=1.0)
    notes: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None

class GradeBulkCreate(BaseModel):
    course_id: str
    assignment_name: str
    grade_type: GradeType
    points_possible: float
    weight: float = 1.0
    due_date: Optional[datetime] = None
    grades: List[Dict[str, Any]]  # List of {student_id: str, points_earned: float, notes?: str}

class Grade(GradeBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    graded_by: str  # Teacher who assigned the grade
    graded_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class GradeStats(BaseModel):
    """Grade statistics for a student or course"""
    total_assignments: int
    completed_assignments: int
    average_percentage: float
    average_grade_points: float
    current_letter_grade: str
    grade_distribution: Dict[str, int]  # Letter grade -> count
    trend: str  # "improving", "declining", "stable"

class CourseGradebook(BaseModel):
    """Complete gradebook for a course"""
    course_id: str
    course_name: str
    assignments: List[Dict[str, Any]]  # Assignment metadata
    students: List[Dict[str, Any]]     # Student grades matrix
    statistics: Dict[str, Any]         # Course-wide statistics

class TranscriptEntry(BaseModel):
    """Entry for student transcript"""
    course_id: str
    course_name: str
    course_code: str
    credits: int
    semester: str
    academic_year: str
    final_grade: str
    grade_points: float
    instructor: str
