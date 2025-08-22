"""
Student models and schemas for EduPredict
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from bson import ObjectId
from app.models.user import PyObjectId


class StudentProfile(BaseModel):
    """Student profile information"""
    student_id: str = Field(..., description="Unique student identifier")
    user_id: PyObjectId = Field(..., description="Reference to user account")
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other)$")
    phone: Optional[str] = Field(None, pattern="^[+]?[1-9]?[0-9]{7,15}$")
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    enrollment_date: date
    expected_graduation: date
    current_semester: int = Field(..., ge=1, le=8)
    current_year: int = Field(..., ge=1, le=4)
    department: str
    program: str  # e.g., "Computer Science", "Engineering"
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    total_credits: int = Field(default=0, ge=0)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class StudentCreate(BaseModel):
    """Student creation model"""
    student_id: str
    user_id: str
    date_of_birth: date
    gender: str
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    enrollment_date: date
    expected_graduation: date
    current_semester: int
    current_year: int
    department: str
    program: str


class StudentUpdate(BaseModel):
    """Student update model"""
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    current_semester: Optional[int] = None
    current_year: Optional[int] = None
    gpa: Optional[float] = None
    total_credits: Optional[int] = None


class StudentInDB(StudentProfile):
    """Student model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Student(BaseModel):
    """Student response model"""
    id: str
    student_id: str
    user_id: str
    date_of_birth: date
    gender: str
    phone: Optional[str]
    address: Optional[str]
    emergency_contact: Optional[Dict[str, str]]
    enrollment_date: date
    expected_graduation: date
    current_semester: int
    current_year: int
    department: str
    program: str
    gpa: Optional[float]
    total_credits: int
    created_at: datetime
    updated_at: datetime
    is_active: bool


class StudentPerformance(BaseModel):
    """Student performance metrics"""
    student_id: str
    semester: int
    year: int
    gpa: float
    credits_completed: int
    attendance_rate: float
    dropout_risk_score: float = Field(..., ge=0.0, le=1.0)
    predicted_grade: Optional[float] = None
    risk_factors: List[str] = []
    recommendations: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class StudentAnalytics(BaseModel):
    """Student analytics data"""
    student_id: str
    performance_trend: List[Dict[str, Any]]  # Historical performance data
    attendance_trend: List[Dict[str, Any]]   # Attendance over time
    grade_distribution: Dict[str, int]       # Grade distribution
    risk_assessment: Dict[str, Any]          # Risk factors and scores
    predictions: Dict[str, Any]              # ML predictions
    generated_at: datetime = Field(default_factory=datetime.utcnow)
