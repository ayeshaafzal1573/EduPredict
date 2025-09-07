from fastapi import APIRouter, Depends, HTTPException, status
from app.services.analytics_service import AnalyticsService, get_analytics_service
from app.models.student import StudentAnalytics
from app.core.security import require_roles, UserRole, get_current_user, TokenData
from app.ml.dropout_predictor import dropout_predictor
from app.ml.grade_predictor import grade_predictor
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_students_collection, get_grades_collection, get_attendance_collection, get_courses_collection
from loguru import logger

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard-stats/{role}")
async def get_dashboard_stats(
    role: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
):
    """Get dashboard statistics for a specific role"""
    try:
        if role == "student":
            # Get student data
            student = await students_collection.find_one({"user_id": current_user.user_id})
            if not student:
                return {
                    "current_gpa": 0.0,
                    "semester_gpa": 0.0,
                    "total_credits": 0,
                    "completed_credits": 0,
                    "attendance_rate": 0,
                    "risk_level": "unknown",
                    "courses_enrolled": 0
                }
            
            # Calculate attendance rate
            attendance_records = await attendance_collection.find({"student_id": student["student_id"]}).to_list(length=None)
            total_classes = len(attendance_records)
            attended_classes = len([r for r in attendance_records if r["status"] == "present"])
            attendance_rate = (attended_classes / total_classes * 100) if total_classes > 0 else 0
            
            # Get enrolled courses
            enrolled_courses = await courses_collection.find({"students": {"$in": [student["student_id"]]}}).to_list(length=None)
            
            return {
                "current_gpa": student.get("gpa", 0.0),
                "semester_gpa": student.get("gpa", 0.0),
                "total_credits": student.get("total_credits", 0),
                "completed_credits": student.get("total_credits", 0),
                "attendance_rate": round(attendance_rate, 1),
                "risk_level": "low",
                "courses_enrolled": len(enrolled_courses)
            }
            
        elif role == "teacher":
            # Get teacher's courses
            teacher_courses = await courses_collection.find({"teacher_id": current_user.user_id}).to_list(length=None)
            
            # Count total students across all courses
            total_students = 0
            for course in teacher_courses:
                total_students += len(course.get("students", []))
            
            # Calculate average attendance for teacher's courses
            course_ids = [course["code"] for course in teacher_courses]
            attendance_records = await attendance_collection.find({"course_id": {"$in": course_ids}}).to_list(length=None)
            total_classes = len(attendance_records)
            attended_classes = len([r for r in attendance_records if r["status"] == "present"])
            avg_attendance = (attended_classes / total_classes * 100) if total_classes > 0 else 0
            
            # Get grades for teacher's courses
            grades = await grades_collection.find({"course_id": {"$in": course_ids}}).to_list(length=None)
            avg_gpa = sum(g.get("grade_points", 0) for g in grades) / len(grades) if grades else 0
            
            return {
                "totalStudents": total_students,
                "atRiskStudents": 0,  # Will be calculated by ML model
                "averageAttendance": round(avg_attendance, 1),
                "averageGPA": round(avg_gpa, 2),
                "activeClasses": len(teacher_courses)
            }
            
        elif role == "admin":
            # Get all users count
            from app.core.database import get_users_collection
            users_collection = await get_users_collection()
            
            total_users = await users_collection.count_documents({})
            active_students = await users_collection.count_documents({"role": "student", "is_active": True})
            total_teachers = await users_collection.count_documents({"role": "teacher"})
            
            # Get courses count
            active_courses = await courses_collection.count_documents({"is_active": True})
            
            # Calculate institution averages
            all_students = await students_collection.find({}).to_list(length=None)
            avg_gpa = sum(s.get("gpa", 0) for s in all_students) / len(all_students) if all_students else 0
            
            # Calculate overall attendance
            all_attendance = await attendance_collection.find({}).to_list(length=None)
            total_classes = len(all_attendance)
            attended_classes = len([r for r in all_attendance if r["status"] == "present"])
            attendance_rate = (attended_classes / total_classes * 100) if total_classes > 0 else 0
            
            return {
                "total_users": total_users,
                "active_students": active_students,
                "total_teachers": total_teachers,
                "active_courses": active_courses,
                "average_gpa": round(avg_gpa, 2),
                "attendance_rate": round(attendance_rate, 1),
                "at_risk_students": 0  # Will be calculated by ML model
            }
        else:
            return {}
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/dropout-prediction/{student_id}")
async def get_dropout_prediction(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Get dropout prediction for a student"""
    try:
        # Get student data
        student = await students_collection.find_one({"student_id": student_id})
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        # Prepare student data for ML model
        student_data = {
            "student_id": student_id,
            "gpa": student.get("gpa", 0.0),
            "attendance_rate": 0.85,  # This should come from attendance calculation
            "total_credits": student.get("total_credits", 0),
            "current_semester": student.get("current_semester", 1),
            "current_year": student.get("current_year", 1),
            "age": 20,  # Calculate from date_of_birth
            "gender": student.get("gender", ""),
            "department": student.get("department", "")
        }
        
        # Get prediction from ML model
        prediction = dropout_predictor.predict_dropout_risk(student_data)
        return prediction
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting dropout prediction: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/grade-predictions/{student_id}")
async def get_grade_predictions(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """Get grade predictions for a student"""
    try:
        # Get student data
        student = await students_collection.find_one({"student_id": student_id})
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        # Get student's courses
        enrolled_courses = await courses_collection.find({"students": {"$in": [student_id]}}).to_list(length=None)
        
        predictions = []
        for course in enrolled_courses:
            student_data = {
                "student_id": student_id,
                "gpa": student.get("gpa", 0.0),
                "attendance_rate": 0.85
            }
            
            course_data = {
                "course_id": course["code"],
                "assignment_avg": 85.0,
                "quiz_avg": 87.0,
                "midterm_score": 82.0,
                "participation_score": 90.0,
                "difficulty_rating": 3.0
            }
            
            prediction = grade_predictor.predict_grade(student_data, course_data)
            predictions.append({
                "course": course["name"],
                "current": "B+",
                "predicted": prediction["predicted_letter_grade"],
                "confidence": prediction["confidence"]
            })
        
        return {
            "student_id": student_id,
            "overall_predicted_gpa": student.get("gpa", 3.0) + 0.2,
            "predictions": predictions
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting grade predictions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/performance-trends/{student_id}")
async def get_performance_trends(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Get performance trends for a student"""
    try:
        student = await students_collection.find_one({"student_id": student_id})
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        # Generate trend data based on current semester
        current_semester = student.get("current_semester", 1)
        current_gpa = student.get("gpa", 3.0)
        
        trends = []
        for i in range(max(1, current_semester - 2), current_semester + 1):
            semester_name = f"Semester {i}"
            # Simulate GPA progression
            gpa_variation = (i - 1) * 0.1
            semester_gpa = max(0.0, min(4.0, current_gpa - 0.3 + gpa_variation))
            
            trends.append({
                "semester": semester_name,
                "gpa": round(semester_gpa, 2),
                "credits": 15 + (i - 1) * 3
            })
        
        return {
            "student_id": student_id,
            "grade_trends": trends
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/institution-analytics")
async def get_institution_analytics(
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection)
):
    """Get institution-wide analytics"""
    try:
        # Department distribution
        students = await students_collection.find({}).to_list(length=None)
        dept_counts = {}
        for student in students:
            dept = student.get("department", "Unknown")
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        department_distribution = [{"name": dept, "count": count} for dept, count in dept_counts.items()]
        
        # Grade distribution
        grades = await grades_collection.find({}).to_list(length=None)
        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for grade in grades:
            letter = grade.get("letter_grade", "C")
            if letter in grade_counts:
                grade_counts[letter] += 1
        
        # Top courses
        courses = await courses_collection.find({}).to_list(length=None)
        top_courses = []
        for course in courses:
            course_grades = [g for g in grades if g.get("course_id") == course.get("code")]
            avg_gpa = sum(g.get("grade_points", 0) for g in course_grades) / len(course_grades) if course_grades else 0
            
            top_courses.append({
                "name": course.get("name", "Unknown Course"),
                "code": course.get("code", ""),
                "average_gpa": round(avg_gpa, 2),
                "student_count": len(course.get("students", []))
            })
        
        top_courses.sort(key=lambda x: x["average_gpa"], reverse=True)
        
        return {
            "department_distribution": department_distribution,
            "grade_distribution": grade_counts,
            "gpa_trends": [
                {"month": "Jan", "gpa": 3.1, "attendance": 85},
                {"month": "Feb", "gpa": 3.2, "attendance": 87},
                {"month": "Mar", "gpa": 3.1, "attendance": 83}
            ],
            "top_courses": top_courses[:10],
            "risk_factors": [
                {"name": "Low Attendance", "percentage": 15},
                {"name": "Poor Assignment Completion", "percentage": 12}
            ]
        }
    except Exception as e:
        logger.error(f"Error getting institution analytics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/at-risk-students")
async def get_at_risk_students(
    limit: int = 20,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Get list of at-risk students"""
    try:
        # Get all students
        students = await students_collection.find({}).to_list(length=None)
        at_risk_students = []
        
        for student in students:
            # Simple risk calculation based on GPA
            gpa = student.get("gpa", 0.0)
            if gpa < 2.5:  # Consider students with GPA < 2.5 as at-risk
                risk_level = "high" if gpa < 2.0 else "medium"
                risk_factors = []
                
                if gpa < 2.0:
                    risk_factors.append("Very Low GPA")
                elif gpa < 2.5:
                    risk_factors.append("Low GPA")
                
                at_risk_students.append({
                    "student_id": student.get("student_id"),
                    "student_name": f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
                    "gpa": gpa,
                    "attendance_rate": 75,  # This should be calculated from attendance data
                    "risk_level": risk_level,
                    "risk_factors": risk_factors
                })
        
        # Sort by GPA (lowest first) and limit results
        at_risk_students.sort(key=lambda x: x["gpa"])
        return at_risk_students[:limit]
        
    except Exception as e:
        logger.error(f"Error getting at-risk students: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}", response_model=StudentAnalytics, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST]))])
async def get_student_analytics(student_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    """
    Retrieve comprehensive analytics for a student (Admin/Analyst only)
    """
    try:
        return await service.generate_student_analytics(student_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting student analytics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))