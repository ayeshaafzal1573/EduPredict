"""
Grade service for EduPredict (DI based clean version)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.grade import Grade, GradeCreate, GradeUpdate, GradeBulkCreate, GradeStats
from app.services.user_service import UserService
from app.services.course_service import CourseService
import logging

logger = logging.getLogger(__name__)

class GradeService:
    def __init__(self, db: AsyncIOMotorDatabase, user_service: UserService, course_service: CourseService):
        self.db = db
        self.user_service = user_service
        self.course_service = course_service

    def _get_collection(self):
        """Get grades collection"""
        if not self.db:
            raise Exception("Database not available")
        return self.db.get_collection("grades")

    def _calculate_percentage(self, points_earned: float, points_possible: float) -> float:
        """Calculate percentage from points"""
        if points_possible <= 0:
            return 0.0
        return round((points_earned / points_possible) * 100, 2)

    def _calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 97:
            return "A+"
        elif percentage >= 93:
            return "A"
        elif percentage >= 90:
            return "A-"
        elif percentage >= 87:
            return "B+"
        elif percentage >= 83:
            return "B"
        elif percentage >= 80:
            return "B-"
        elif percentage >= 77:
            return "C+"
        elif percentage >= 73:
            return "C"
        elif percentage >= 70:
            return "C-"
        elif percentage >= 67:
            return "D+"
        elif percentage >= 63:
            return "D"
        elif percentage >= 60:
            return "D-"
        else:
            return "F"

    def _calculate_grade_points(self, letter_grade: str) -> float:
        """Convert letter grade to grade points (4.0 scale)"""
        grade_points = {
            "A+": 4.0, "A": 4.0, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "D-": 0.7,
            "F": 0.0
        }
        return grade_points.get(letter_grade, 0.0)

    async def create_grade(self, grade_data: GradeCreate, graded_by: str) -> Grade:
        """Create a new grade record"""
        try:
            collection = self._get_collection()

            # Get student and course information
            student = await self.user_service.get_user_by_id(grade_data.student_id)
            course = await self.course_service.get_course_by_id(grade_data.course_id)
            grader = await self.user_service.get_user_by_id(graded_by)

            if not student:
                raise ValueError("Student not found")
            if not course:
                raise ValueError("Course not found")
            if not grader:
                raise ValueError("Grader not found")

            # Verify student is enrolled in the course
            if grade_data.student_id not in course.students:
                raise ValueError("Student is not enrolled in this course")

            # Calculate derived fields
            percentage = self._calculate_percentage(grade_data.points_earned, grade_data.points_possible)
            letter_grade = self._calculate_letter_grade(percentage)
            grade_points = self._calculate_grade_points(letter_grade)

            grade_dict = grade_data.model_dump()
            grade_dict.update({
                "_id": ObjectId(),
                "percentage": percentage,
                "letter_grade": letter_grade,
                "grade_points": grade_points,
                "student_name": f"{student.first_name} {student.last_name}",
                "course_name": course.name,
                "graded_by": graded_by,
                "graded_by_name": f"{grader.first_name} {grader.last_name}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            result = await collection.insert_one(grade_dict)
            grade_dict["_id"] = result.inserted_id

            return Grade(**grade_dict)
        except Exception as e:
            logger.error(f"Error creating grade: {str(e)}")
            raise

    

    async def create_grade(self, grade_data: GradeCreate, graded_by: str) -> Grade:
        """Create a new grade record"""
        try:
            collection = self._get_collection()

            # Get student and course information
            student = await self.user_service.get_user_by_id(grade_data.student_id)
            course = await self.course_service.get_course_by_id(grade_data.course_id)
            grader = await self.user_service.get_user_by_id(graded_by)

            if not student:
                raise ValueError("Student not found")
            if not course:
                raise ValueError("Course not found")
            if not grader:
                raise ValueError("Grader not found")

            # Verify student is enrolled in the course
            if grade_data.student_id not in course.students:
                raise ValueError("Student is not enrolled in this course")

            # Calculate derived fields
            percentage = self._calculate_percentage(grade_data.points_earned, grade_data.points_possible)
            letter_grade = self._calculate_letter_grade(percentage)
            grade_points = self._calculate_grade_points(letter_grade)

            grade_dict = grade_data.model_dump()
            grade_dict.update({
                "_id": ObjectId(),
                "percentage": percentage,
                "letter_grade": letter_grade,
                "grade_points": grade_points,
                "student_name": f"{student.first_name} {student.last_name}",
                "course_name": course.name,
                "graded_by": graded_by,
                "graded_by_name": f"{grader.first_name} {grader.last_name}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            result = await collection.insert_one(grade_dict)
            grade_dict["_id"] = result.inserted_id

            return Grade(**grade_dict)
        except Exception as e:
            logger.error(f"Error creating grade: {str(e)}")
            raise
async def create_bulk_grades(self, bulk_data: GradeBulkCreate, graded_by: str) -> List[Grade]:
        """Create multiple grade records at once"""
        try:
            collection = self._get_collection()

            # Get course information
            course = await self.course_service.get_course_by_id(bulk_data.course_id)
            if not course:
                raise ValueError("Course not found")

            grader = await self.user_service.get_user_by_id(graded_by)
            if not grader:
                raise ValueError("Grader not found")

            grade_records = []
            for grade_data in bulk_data.grades:
                student_id = grade_data.get("student_id")
                points_earned = grade_data.get("points_earned", 0)
                notes = grade_data.get("notes", "")

                # Get student info
                student = await self.user_service.get_user_by_id(student_id)
                if not student:
                    continue

                # Verify enrollment
                if student_id not in course.students:
                    continue

                # Derived fields
                percentage = self._calculate_percentage(points_earned, bulk_data.points_possible)
                letter_grade = self._calculate_letter_grade(percentage)
                grade_points = self._calculate_grade_points(letter_grade)

                grade_dict = {
                    "_id": ObjectId(),
                    "student_id": student_id,
                    "course_id": bulk_data.course_id,
                    "assignment_name": bulk_data.assignment_name,
                    "grade_type": bulk_data.grade_type,
                    "points_earned": points_earned,
                    "points_possible": bulk_data.points_possible,
                    "percentage": percentage,
                    "letter_grade": letter_grade,
                    "grade_points": grade_points,
                    "weight": bulk_data.weight,
                    "notes": notes,
                    "due_date": bulk_data.due_date,
                    "submitted_date": None,
                    "student_name": f"{student.first_name} {student.last_name}",
                    "course_name": course.name,
                    "graded_by": graded_by,
                    "graded_by_name": f"{grader.first_name} {grader.last_name}",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }

                grade_records.append(grade_dict)

            if grade_records:
                result = await collection.insert_many(grade_records)
                for i, inserted_id in enumerate(result.inserted_ids):
                    grade_records[i]["_id"] = inserted_id

            return [Grade(**record) for record in grade_records]
        except Exception as e:
            logger.error(f"Error creating bulk grades: {str(e)}")
            raise


async def get_grades(
        self,
        skip: int = 0,
        limit: int = 100,
        student_id: Optional[str] = None,
        course_id: Optional[str] = None,
        grade_type: Optional[str] = None,
        user_role: str = "student",
        user_id: Optional[str] = None
    ) -> List[Grade]:
        """Get grade records with filtering"""
        try:
            collection = self._get_collection()
            query: Dict[str, Any] = {}

            if student_id:
                query["student_id"] = student_id
            if course_id:
                query["course_id"] = course_id
            if grade_type:
                query["grade_type"] = grade_type

            # Role-based filtering
            if user_role == "teacher":
                teacher_courses = await self.course_service.get_courses(teacher_id=user_id)
                course_ids = [str(course.id) for course in teacher_courses]
                if course_id and course_id not in course_ids:
                    return []
                if not course_id:
                    query["course_id"] = {"$in": course_ids}

            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            grade_data = await cursor.to_list(length=limit)

            return [Grade(**record) for record in grade_data]
        except Exception as e:
            logger.error(f"Error getting grades: {str(e)}")


    
async def update_grade(self, grade_id: str, grade_update: GradeUpdate) -> Grade:
        """Update a grade record"""
        try:
            collection = self._get_collection()
            
            # Get current grade to recalculate derived fields if needed
            current_grade = await collection.find_one({"_id": ObjectId(grade_id)})
            if not current_grade:
                raise ValueError("Grade record not found")

            update_data = {k: v for k, v in grade_update.model_dump().items() if v is not None}
            
            # Recalculate derived fields if points changed
            if "points_earned" in update_data or "points_possible" in update_data:
                points_earned = update_data.get("points_earned", current_grade["points_earned"])
                points_possible = update_data.get("points_possible", current_grade["points_possible"])
                
                percentage = self._calculate_percentage(points_earned, points_possible)
                letter_grade = self._calculate_letter_grade(percentage)
                grade_points = self._calculate_grade_points(letter_grade)
                
                update_data.update({
                    "percentage": percentage,
                    "letter_grade": letter_grade,
                    "grade_points": grade_points
                })

            update_data["updated_at"] = datetime.utcnow()

            result = await collection.update_one(
                {"_id": ObjectId(grade_id)},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                raise ValueError("Grade record not found or no changes made")

            updated_record = await collection.find_one({"_id": ObjectId(grade_id)})
            if not updated_record:
                raise ValueError("Failed to retrieve updated grade record")

            return Grade(**updated_record)
        except Exception as e:
            logger.error(f"Error updating grade: {str(e)}")
            raise

async def delete_grade(self, grade_id: str) -> bool:
        """Delete a grade record"""
        try:
            collection = self._get_collection()
            
            result = await collection.delete_one({"_id": ObjectId(grade_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting grade: {str(e)}")
            return False
async def get_student_grade_stats(self, student_id: str, course_id: Optional[str] = None) -> GradeStats:
        """Get grade statistics for a student"""
        try:
            collection = self._get_collection()
            
            query = {"student_id": student_id}
            if course_id:
                query["course_id"] = course_id

            grades = await collection.find(query).to_list(None)
            
            if not grades:
                return GradeStats(
                    total_assignments=0,
                    completed_assignments=0,
                    average_percentage=0.0,
                    average_grade_points=0.0,
                    current_letter_grade="N/A",
                    grade_distribution={},
                    trend="stable"
                )

            # Calculate statistics
            total_assignments = len(grades)
            completed_assignments = len([g for g in grades if g.get("points_earned", 0) > 0])
            
            # Weighted average calculation
            total_weighted_points = sum(g.get("grade_points", 0) * g.get("weight", 1) for g in grades)
            total_weight = sum(g.get("weight", 1) for g in grades)
            average_grade_points = total_weighted_points / total_weight if total_weight > 0 else 0
            
            # Calculate average percentage
            total_weighted_percentage = sum(g.get("percentage", 0) * g.get("weight", 1) for g in grades)
            average_percentage = total_weighted_percentage / total_weight if total_weight > 0 else 0
            
            current_letter_grade = self._calculate_letter_grade(average_percentage)
            
            # Grade distribution
            grade_distribution = {}
            for grade in grades:
                letter = grade.get("letter_grade", "F")
                grade_distribution[letter] = grade_distribution.get(letter, 0) + 1

            # Calculate trend (simplified)
            trend = "stable"
            if len(grades) >= 3:
                recent_avg = sum(g.get("grade_points", 0) for g in grades[-3:]) / 3
                older_avg = sum(g.get("grade_points", 0) for g in grades[:-3]) / max(1, len(grades) - 3)
                if recent_avg > older_avg + 0.2:
                    trend = "improving"
                elif recent_avg < older_avg - 0.2:
                    trend = "declining"

            return GradeStats(
                total_assignments=total_assignments,
                completed_assignments=completed_assignments,
                average_percentage=round(average_percentage, 2),
                average_grade_points=round(average_grade_points, 2),
                current_letter_grade=current_letter_grade,
                grade_distribution=grade_distribution,
                trend=trend
            )
        except Exception as e:
            logger.error(f"Error getting student grade stats: {str(e)}")
            raise
async def update_grade(self, grade_id: str, grade_update: GradeUpdate) -> Grade:
        """Update a grade record"""
        try:
            collection = self._get_collection()

            current_grade = await collection.find_one({"_id": ObjectId(grade_id)})
            if not current_grade:
                raise ValueError("Grade record not found")

            update_data = {k: v for k, v in grade_update.model_dump().items() if v is not None}

            # Recalculate derived fields if points changed
            if "points_earned" in update_data or "points_possible" in update_data:
                points_earned = update_data.get("points_earned", current_grade["points_earned"])
                points_possible = update_data.get("points_possible", current_grade["points_possible"])

                percentage = self._calculate_percentage(points_earned, points_possible)
                letter_grade = self._calculate_letter_grade(percentage)
                grade_points = self._calculate_grade_points(letter_grade)

                update_data.update({
                    "percentage": percentage,
                    "letter_grade": letter_grade,
                    "grade_points": grade_points
                })

            update_data["updated_at"] = datetime.utcnow()

            result = await collection.update_one(
                {"_id": ObjectId(grade_id)},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                raise ValueError("Grade not found or no changes made")

            updated_record = await collection.find_one({"_id": ObjectId(grade_id)})
            if not updated_record:
                raise ValueError("Failed to retrieve updated grade record")

            return Grade(**updated_record)
        except Exception as e:
            logger.error(f"Error updating grade: {str(e)}")
            raise

async def delete_grade(self, grade_id: str) -> bool:
        """Delete a grade record"""
        try:
            collection = self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(grade_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting grade: {str(e)}")
            return False

async def get_student_grade_stats(self, student_id: str, course_id: Optional[str] = None) -> GradeStats:
        """Get grade statistics for a student"""
        try:
            collection = self._get_collection()

            query: Dict[str, Any] = {"student_id": student_id}
            if course_id:
                query["course_id"] = course_id

            grades = await collection.find(query).to_list(None)
            if not grades:
                return GradeStats(
                    total_assignments=0,
                    completed_assignments=0,
                    average_percentage=0.0,
                    average_grade_points=0.0,
                    current_letter_grade="N/A",
                    grade_distribution={},
                    trend="stable"
                )

            total_assignments = len(grades)
            completed_assignments = len([g for g in grades if g.get("points_earned", 0) > 0])

            total_weighted_points = sum(g.get("grade_points", 0) * g.get("weight", 1) for g in grades)
            total_weight = sum(g.get("weight", 1) for g in grades)
            average_grade_points = total_weighted_points / total_weight if total_weight > 0 else 0

            total_weighted_percentage = sum(g.get("percentage", 0) * g.get("weight", 1) for g in grades)
            average_percentage = total_weighted_percentage / total_weight if total_weight > 0 else 0

            current_letter_grade = self._calculate_letter_grade(average_percentage)

            grade_distribution: Dict[str, int] = {}
            for grade in grades:
                letter = grade.get("letter_grade", "F")
                grade_distribution[letter] = grade_distribution.get(letter, 0) + 1

            trend = "stable"
            if len(grades) >= 3:
                recent_avg = sum(g.get("grade_points", 0) for g in grades[-3:]) / 3
                older_avg = sum(g.get("grade_points", 0) for g in grades[:-3]) / max(1, len(grades) - 3)
                if recent_avg > older_avg + 0.2:
                    trend = "improving"
                elif recent_avg < older_avg - 0.2:
                    trend = "declining"

            return GradeStats(
                total_assignments=total_assignments,
                completed_assignments=completed_assignments,
                average_percentage=round(average_percentage, 2),
                average_grade_points=round(average_grade_points, 2),
                current_letter_grade=current_letter_grade,
                grade_distribution=grade_distribution,
                trend=trend
            )
        except Exception as e:
            logger.error(f"Error getting student grade stats: {str(e)}")
            raise

async def get_course_gradebook(self, course_id: str) -> Dict[str, Any]:
        """Get complete gradebook for a course"""
        try:
            collection = self._get_collection()

            course = await self.course_service.get_course_by_id(course_id)
            if not course:
                raise ValueError("Course not found")

            grades = await collection.find({"course_id": course_id}).to_list(None)

            assignments: Dict[str, Dict[str, Any]] = {}
            students: Dict[str, Dict[str, Any]] = {}

            for grade in grades:
                assignment_key = f"{grade['assignment_name']}_{grade['grade_type']}"
                student_id = grade["student_id"]

                if assignment_key not in assignments:
                    assignments[assignment_key] = {
                        "name": grade["assignment_name"],
                        "type": grade["grade_type"],
                        "points_possible": grade["points_possible"],
                        "weight": grade.get("weight", 1.0),
                        "due_date": grade.get("due_date")
                    }

                if student_id not in students:
                    students[student_id] = {
                        "student_id": student_id,
                        "student_name": grade["student_name"],
                        "grades": {},
                        "total_points": 0,
                        "total_possible": 0,
                        "current_grade": "N/A"
                    }

                students[student_id]["grades"][assignment_key] = {
                    "points_earned": grade["points_earned"],
                    "percentage": grade["percentage"],
                    "letter_grade": grade["letter_grade"]
                }

            for student_data in students.values():
                total_weighted_points = 0
                total_weight = 0

                for assignment_key, assignment_data in assignments.items():
                    if assignment_key in student_data["grades"]:
                        grade_data = student_data["grades"][assignment_key]
                        weight = assignment_data["weight"]
                        points_earned = grade_data["points_earned"]
                        points_possible = assignment_data["points_possible"]

                        if points_possible > 0:
                            percentage = (points_earned / points_possible) * 100
                            total_weighted_points += percentage * weight
                            total_weight += weight

                if total_weight > 0:
                    current_percentage = total_weighted_points / total_weight
                    student_data["current_grade"] = self._calculate_letter_grade(current_percentage)
                    student_data["current_percentage"] = round(current_percentage, 2)

            return {
                "course_id": course_id,
                "course_name": course.name,
                "assignments": list(assignments.values()),
                "students": list(students.values()),
                "statistics": {
                    "total_students": len(students),
                    "total_assignments": len(assignments),
                    "class_average": self._calculate_class_average(list(students.values()))
                }
            }
        except Exception as e:
            logger.error(f"Error getting course gradebook: {str(e)}")
            raise

def _calculate_class_average(self, students: List[Dict[str, Any]]) -> float:
        """Calculate class average from student data"""
        try:
            valid_grades = [s.get("current_percentage", 0) for s in students if s.get("current_percentage", 0) > 0]
            return round(sum(valid_grades) / len(valid_grades), 2) if valid_grades else 0.0
        except Exception as e:
            logger.error(f"Error calculating class average: {str(e)}")
            return 0.0

