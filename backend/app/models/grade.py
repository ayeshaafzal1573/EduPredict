from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.models.base import PyObjectId, MongoBaseModel


class GradeType(str, Enum):
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PARTICIPATION = "participation"
    MIDTERM = "midterm"
    FINAL = "final"


class GradeBase(MongoBaseModel):
    """Base grade model"""
    student_id: str
    course_id: str
    assignment_name: str = Field(..., min_length=1, max_length=200)
    grade_type: GradeType
    points_earned: float = Field(..., ge=0)
    points_possible: float = Field(..., gt=0)
    percentage: Optional[float] = None
    letter_grade: Optional[str] = None
    grade_points: Optional[float] = None
    weight: float = Field(1.0, ge=0, le=1.0)
    notes: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None

    @validator("student_id")
    def validate_student_id(cls, v):
        """Ensure student_id follows a specific format"""
        if not v.startswith("STU-") or not v[4:].isdigit():
            raise ValueError("student_id must start with 'STU-' followed by digits")
        return v

    @validator("course_id")
    def validate_course_id(cls, v):
        """Ensure course_id follows a specific format"""
        if not v.replace("-", "").isalnum():
            raise ValueError("Course ID must be alphanumeric with optional hyphens")
        return v


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    assignment_name: Optional[str] = Field(None, min_length=1, max_length=200)
    grade_type: Optional[GradeType] = None
    points_earned: Optional[float] = Field(None, ge=0)
    points_possible: Optional[float] = Field(None, gt=0)
    percentage: Optional[float] = Field(None, ge=0, le=100)
    letter_grade: Optional[str] = None
    grade_points: Optional[float] = Field(None, ge=0, le=4.0)
    weight: Optional[float] = Field(None, ge=0, le=1.0)
    notes: Optional[str] = None
    due_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None


class GradeBulkCreate(BaseModel):
    course_id: str
    assignment_name: str
    grade_type: GradeType
    points_possible: float
    weight: float = 1.0
    due_date: Optional[datetime] = None
    grades: List[Dict[str, Any]]


class Grade(GradeBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    graded_by: str
    graded_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GradeStats(BaseModel):
    total_assignments: int
    completed_assignments: int
    average_percentage: float
    average_grade_points: float
    current_letter_grade: str
    grade_distribution: Dict[str, int]
    trend: str
    hdfs_path: Optional[str] = None  # Path to HDFS storage for grade data


class CourseGradebook(BaseModel):
    course_id: str
    course_name: str
    assignments: List[Dict[str, Any]]
    students: List[Dict[str, Any]]
    statistics: Dict[str, Any]


class TranscriptEntry(BaseModel):
    course_id: str
    course_name: str
    course_code: str
    credits: int
    semester: str
    academic_year: str
    final_grade: str
    grade_points: float
    instructor: str


class AssignmentSummary(BaseModel):
    name: str
    type: str
    points_possible: float
    weight: float = 1.0
    due_date: Optional[datetime] = None


class StudentGradeSummary(BaseModel):
    student_id: str
    student_name: str
    grades: Dict[str, Dict[str, Any]]
    total_points: float = 0
    total_possible: float = 0
    current_grade: str = "N/A"
    current_percentage: Optional[float] = None