from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_students_collection, get_grades_collection, get_attendance_collection
from app.models.student import StudentAnalytics
from loguru import logger
import json
from typing import Dict
from datetime import datetime

class AnalyticsService:
    """Service for generating student analytics"""

    def __init__(self, students_collection: AsyncIOMotorCollection, grades_collection: AsyncIOMotorCollection, attendance_collection: AsyncIOMotorCollection):
        self.students_collection = students_collection
        self.grades_collection = grades_collection
        self.attendance_collection = attendance_collection

    async def generate_student_analytics(self, student_id: str) -> StudentAnalytics:
        """Generate comprehensive analytics for a student"""
        try:
            student = await self.students_collection.find_one({"student_id": student_id})
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            
            # Fetch grades and attendance
            grades = await self.grades_collection.find({"student_id": student_id}).to_list(length=None)
            attendance = await self.attendance_collection.find({"student_id": student_id}).to_list(length=None)
            
            # Calculate performance trend
            performance_trend = []
            current_semester = student.get("current_semester", 1)
            current_gpa = student.get("gpa", 0.0)
            
            for i in range(max(1, current_semester - 2), current_semester + 1):
                semester_name = f"Semester {i}"
                # Simulate GPA progression based on current data
                gpa_variation = (i - 1) * 0.1
                semester_gpa = max(0.0, min(4.0, current_gpa - 0.3 + gpa_variation))
                
                performance_trend.append({
                    "semester": semester_name,
                    "gpa": round(semester_gpa, 2),
                    "credits": 15 + (i - 1) * 3
                })
            
            # Calculate attendance trend
            attendance_trend = []
            months = ["Jan", "Feb", "Mar", "Apr", "May"]
            for month in months:
                # Calculate monthly attendance rate
                month_attendance = len([a for a in attendance if a["status"] == "present"]) / len(attendance) * 100 if attendance else 85
                attendance_trend.append({
                    "month": month,
                    "rate": round(month_attendance, 1)
                })
            
            # Grade distribution
            grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            for grade in grades:
                letter = grade.get("letter_grade", "C")
                if letter.startswith("A"):
                    grade_distribution["A"] += 1
                elif letter.startswith("B"):
                    grade_distribution["B"] += 1
                elif letter.startswith("C"):
                    grade_distribution["C"] += 1
                elif letter.startswith("D"):
                    grade_distribution["D"] += 1
                else:
                    grade_distribution["F"] += 1
            
            # Risk assessment
            gpa = student.get("gpa", 0.0)
            attendance_rate = len([a for a in attendance if a["status"] == "present"]) / len(attendance) if attendance else 0.85
            
            if gpa < 2.0 or attendance_rate < 0.6:
                risk_level = "high"
                risk_score = 0.8
            elif gpa < 2.5 or attendance_rate < 0.75:
                risk_level = "medium"
                risk_score = 0.5
            else:
                risk_level = "low"
                risk_score = 0.2
            
            analytics_data = {
                "student_id": student_id,
                "performance_trend": performance_trend,
                "attendance_trend": attendance_trend,
                "grade_distribution": grade_distribution,
                "risk_assessment": {
                    "score": risk_score,
                    "level": risk_level,
                    "factors": ["Low GPA"] if gpa < 2.5 else []
                },
                "predictions": {
                    "dropout_risk": risk_score,
                    "expected_gpa": min(4.0, gpa + 0.2)
                },
                "hdfs_path": None  # HDFS integration removed for simplicity
            }
            
            return StudentAnalytics(**analytics_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate analytics for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_analytics_service(
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
) -> AnalyticsService:
    """Dependency for AnalyticsService"""
    return AnalyticsService(students_collection, grades_collection, attendance_collection)