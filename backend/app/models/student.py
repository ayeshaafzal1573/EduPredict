from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from bson import ObjectId
from app.models.base import PyObjectId, MongoBaseModel


class StudentProfile(MongoBaseModel):
    """Student profile information"""
    student_id: str = Field(..., description="Unique student identifier")
    user_id: str = Field(..., description="Reference to user account")
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

    @validator("student_id")
    def validate_student_id(cls, v):
        """Ensure student_id follows a specific format (e.g., STU-XXXX)"""
        if not v:
            raise ValueError("Student ID is required")
        if not v.startswith("STU") or len(v) < 6:
            raise ValueError("Student ID must start with 'STU' and be at least 6 characters")
        return v

    @validator("user_id")
    def validate_user_id(cls, v):
        """Ensure user_id is valid"""
        if not v:
            raise ValueError("User ID is required")
        return v

    @validator("department", "program")
    def validate_required_strings(cls, v):
        """Ensure required string fields are not empty"""
        if not v or not v.strip():
            raise ValueError("This field is required and cannot be empty")
        return v.strip()


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

    @validator("student_id")
    def validate_student_id(cls, v):
        if not v or not v.startswith("STU"):
            raise ValueError("Student ID must start with 'STU'")
        return v

    @validator("user_id")
    def validate_user_id(cls, v):
        if not v:
            raise ValueError("User ID is required")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        if v not in ["male", "female", "other"]:
            raise ValueError("Gender must be 'male', 'female', or 'other'")
        return v

    @validator("department", "program")
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("This field is required")
        return v.strip()


class StudentUpdate(BaseModel):
    """Student update model"""
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    current_semester: Optional[int] = Field(None, ge=1, le=8)
    current_year: Optional[int] = Field(None, ge=1, le=4)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    total_credits: Optional[int] = Field(None, ge=0)
    department: Optional[str] = None
    program: Optional[str] = None

    @validator("department", "program")
    def validate_strings(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty if provided")
        return v.strip() if v else v


class StudentInDB(StudentProfile):
    """Student model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Student(StudentProfile):
    """Student response model"""
    id: str
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

    @validator("student_id")
    def validate_student_id(cls, v):
        """Ensure student_id follows a specific format"""
        if not v or not v.startswith("STU"):
            raise ValueError("Student ID must start with 'STU'")
        return v


class StudentAnalytics(BaseModel):
    """Student analytics data"""
    student_id: str
    performance_trend: List[Dict[str, Any]]  # Historical performance data
    attendance_trend: List[Dict[str, Any]]   # Attendance over time
    grade_distribution: Dict[str, int]       # Grade distribution
    risk_assessment: Dict[str, Any]          # Risk factors and scores
    predictions: Dict[str, Any]              # ML predictions
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    hdfs_path: Optional[str] = None  # Path to HDFS storage for large datasets

    @validator("student_id")
    def validate_student_id(cls, v):
        """Ensure student_id follows a specific format"""
        if not v or not v.startswith("STU"):
            raise ValueError("Student ID must start with 'STU'")
        return v