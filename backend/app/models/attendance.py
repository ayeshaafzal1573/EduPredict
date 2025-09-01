"""
Attendance models for EduPredict
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from app.models.user import PyObjectId  # ✅ reuse instead of redefining


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceBase(BaseModel):
    student_id: str
    course_id: str
    date: date
    status: AttendanceStatus
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceBulkCreate(BaseModel):
    course_id: str
    date: date
    attendance_records: List[Dict[str, Any]]  # {student_id, status, notes?}


class Attendance(AttendanceBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    marked_by: str  # Teacher/Admin who marked attendance
    marked_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str}
    }


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


class AttendanceSummary(BaseModel):
    """Summary of attendance for reporting"""
    student_id: str
    course_id: str
    stats: AttendanceStats
    recent_absences: List[date]
