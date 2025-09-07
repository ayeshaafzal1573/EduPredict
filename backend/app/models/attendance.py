
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from app.models.base import PyObjectId, MongoBaseModel


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceBase(MongoBaseModel):
    """Base attendance model"""
    student_id: str
    course_id: str
    date: date
    status: AttendanceStatus
    notes: Optional[str] = Field(None, max_length=500)

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


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceBulkCreate(BaseModel):
    course_id: str
    date: date
    attendance_records: List[Dict[str, Any]]


class Attendance(AttendanceBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    marked_by: str
    marked_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AttendanceStats(BaseModel):
    """Attendance statistics for a student or course"""
    total_classes: int
    attended: int
    absent: int
    late: int
    excused: int
    attendance_rate: float
    period_start: date
    period_end: date
    hdfs_path: Optional[str] = None  # Path to HDFS storage for attendance data


class AttendanceSummary(BaseModel):
    """Summary of attendance for reporting"""
    student_id: str
    course_id: str
    stats: AttendanceStats
    recent_absences: List[date]