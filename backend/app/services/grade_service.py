from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_grades_collection
from app.models.grade import Grade, GradeCreate, GradeUpdate, GradeStats
from datetime import datetime

class GradeService:
    """Service for grade-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_grade(self, grade: GradeCreate) -> Grade:
        """Create a new grade record"""
        try:
            # Calculate percentage and letter grade
            percentage = (grade.points_earned / grade.points_possible * 100) if grade.points_possible > 0 else 0
            letter_grade = self.calculate_letter_grade(percentage)
            grade_points = self.percentage_to_gpa(percentage)
            
            grade_dict = grade.dict()
            grade_dict.update({
                "percentage": round(percentage, 1),
                "letter_grade": letter_grade,
                "grade_points": round(grade_points, 2),
                "graded_by": "system",  # This should come from current user
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            result = await self.collection.insert_one(grade_dict)
            grade_in_db = await self.collection.find_one({"_id": result.inserted_id})
            
            # Convert to Grade model
            grade_data = {
                "id": str(grade_in_db["_id"]),
                "student_id": grade_in_db["student_id"],
                "course_id": grade_in_db["course_id"],
                "assignment_name": grade_in_db["assignment_name"],
                "grade_type": grade_in_db["grade_type"],
                "points_earned": grade_in_db["points_earned"],
                "points_possible": grade_in_db["points_possible"],
                "percentage": grade_in_db.get("percentage"),
                "letter_grade": grade_in_db.get("letter_grade"),
                "grade_points": grade_in_db.get("grade_points"),
                "weight": grade_in_db.get("weight", 1.0),
                "notes": grade_in_db.get("notes"),
                "graded_by": grade_in_db["graded_by"],
                "created_at": grade_in_db["created_at"],
                "updated_at": grade_in_db["updated_at"]
            }
            
            return Grade(**grade_data)
        except Exception as e:
            logger.error(f"Failed to create grade for student {grade.student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def calculate_letter_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 97: return "A+"
        elif percentage >= 93: return "A"
        elif percentage >= 90: return "A-"
        elif percentage >= 87: return "B+"
        elif percentage >= 83: return "B"
        elif percentage >= 80: return "B-"
        elif percentage >= 77: return "C+"
        elif percentage >= 73: return "C"
        elif percentage >= 70: return "C-"
        elif percentage >= 67: return "D+"
        elif percentage >= 63: return "D"
        elif percentage >= 60: return "D-"
        else: return "F"

    def percentage_to_gpa(self, percentage):
        """Convert percentage to GPA points"""
        if percentage >= 97: return 4.0
        elif percentage >= 93: return 4.0
        elif percentage >= 90: return 3.7
        elif percentage >= 87: return 3.3
        elif percentage >= 83: return 3.0
        elif percentage >= 80: return 2.7
        elif percentage >= 77: return 2.3
        elif percentage >= 73: return 2.0
        elif percentage >= 70: return 1.7
        elif percentage >= 67: return 1.3
        elif percentage >= 63: return 1.0
        elif percentage >= 60: return 0.7
        else: return 0.0

    async def generate_grade_stats(self, student_id: str, course_id: str) -> GradeStats:
        """Generate grade statistics"""
        try:
            grades = await self.collection.find({"student_id": student_id, "course_id": course_id}).to_list(length=1000)
            if not grades:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No grades found")
            
            total_assignments = len(grades)
            completed = len([g for g in grades if g.get("percentage") is not None])
            
            # Calculate averages
            total_percentage = sum(g.get("percentage", 0) for g in grades if g.get("percentage") is not None)
            avg_percentage = total_percentage / completed if completed > 0 else 0.0
            
            total_grade_points = sum(g.get("grade_points", 0) for g in grades if g.get("grade_points") is not None)
            avg_grade_points = total_grade_points / completed if completed > 0 else 0.0
            
            current_letter_grade = self.calculate_letter_grade(avg_percentage)
            
            # Grade distribution
            grade_distribution = {}
            for grade in grades:
                letter = grade.get("letter_grade", "C")
                grade_distribution[letter] = grade_distribution.get(letter, 0) + 1
            
            stats = {
                "total_assignments": total_assignments,
                "completed_assignments": completed,
                "average_percentage": round(avg_percentage, 2),
                "average_grade_points": round(avg_grade_points, 2),
                "current_letter_grade": current_letter_grade,
                "grade_distribution": grade_distribution,
                "trend": "Stable",
                "hdfs_path": None
            }
            
            return GradeStats(**stats)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate grade stats for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_grade_service(collection: AsyncIOMotorCollection = Depends(get_grades_collection)) -> GradeService:
    """Dependency for GradeService"""
    return GradeService(collection)