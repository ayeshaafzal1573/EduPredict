#!/usr/bin/env python3
"""
Seed script for EduPredict database
Creates sample users, students, courses, and test data
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import pandas as pd

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import UserRole

async def create_sample_users():
    """Create sample users for testing"""
    users = [
        {
            "email": "admin@edupredict.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.ADMIN,
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "email": "teacher@edupredict.com",
            "first_name": "John",
            "last_name": "Teacher",
            "role": UserRole.TEACHER,
            "hashed_password": get_password_hash("teacher123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "email": "student@edupredict.com",
            "first_name": "Jane",
            "last_name": "Student",
            "role": UserRole.STUDENT,
            "hashed_password": get_password_hash("student123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "email": "analyst@edupredict.com",
            "first_name": "Data",
            "last_name": "Analyst",
            "role": UserRole.ANALYST,
            "hashed_password": get_password_hash("analyst123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    return users

async def create_sample_students():
    """Create sample student profiles"""
    students = []
    
    # Read from CSV if available
    csv_path = "data/sample_data/students_sample.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            student = {
                "student_id": row["student_id"],
                "user_id": None,  # Will be linked later
                "date_of_birth": date(2002, 5, 15),
                "gender": row["gender"],
                "department": row["department"],
                "program": row["program"],
                "enrollment_date": date(2021, 9, 1),
                "expected_graduation": date(2025, 5, 15),
                "current_semester": row["current_semester"],
                "current_year": row["current_year"],
                "gpa": row["gpa"],
                "total_credits": row["total_credits"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            students.append(student)
    
    return students

async def create_sample_courses():
    """Create sample courses"""
    courses = [
        {
            "name": "Introduction to Computer Science",
            "code": "CS-101",
            "description": "Fundamentals of computer science and programming",
            "department": "Computer Science",
            "credits": 3,
            "semester": "Fall 2024",
            "academic_year": "2024",
            "schedule": "MWF 10:00-11:00",
            "room": "CS-201",
            "max_students": 30,
            "teacher_id": None,  # Will be linked later
            "students": [],
            "student_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Calculus II",
            "code": "MATH-201",
            "description": "Advanced calculus concepts and applications",
            "department": "Mathematics",
            "credits": 4,
            "semester": "Fall 2024",
            "academic_year": "2024",
            "schedule": "TTh 14:00-15:30",
            "room": "MATH-105",
            "max_students": 25,
            "teacher_id": None,
            "students": [],
            "student_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "General Physics I",
            "code": "PHYS-101",
            "description": "Introduction to mechanics and thermodynamics",
            "department": "Physics",
            "credits": 4,
            "semester": "Fall 2024",
            "academic_year": "2024",
            "schedule": "MWF 13:00-14:00",
            "room": "PHYS-301",
            "max_students": 20,
            "teacher_id": None,
            "students": [],
            "student_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    return courses

async def seed_database():
    """Main seeding function"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB]
        
        logger.info("Starting database seeding...")
        
        # Create users
        users_collection = db.users
        users = await create_sample_users()
        
        # Clear existing data
        await users_collection.delete_many({})
        await db.students.delete_many({})
        await db.courses.delete_many({})
        await db.grades.delete_many({})
        await db.attendance.delete_many({})
        await db.notifications.delete_many({})
        
        # Insert users
        user_result = await users_collection.insert_many(users)
        logger.info(f"Created {len(user_result.inserted_ids)} users")
        
        # Get user IDs for linking
        admin_user = await users_collection.find_one({"email": "admin@edupredict.com"})
        teacher_user = await users_collection.find_one({"email": "teacher@edupredict.com"})
        student_user = await users_collection.find_one({"email": "student@edupredict.com"})
        analyst_user = await users_collection.find_one({"email": "analyst@edupredict.com"})
        
        # Create students
        students = await create_sample_students()
        if students:
            # Link first student to student user
            students[0]["user_id"] = student_user["_id"]
            
            students_result = await db.students.insert_many(students)
            logger.info(f"Created {len(students_result.inserted_ids)} students")
        
        # Create courses
        courses = await create_sample_courses()
        if teacher_user:
            for course in courses:
                course["teacher_id"] = str(teacher_user["_id"])
                course["teacher_name"] = f"{teacher_user['first_name']} {teacher_user['last_name']}"
        
        courses_result = await db.courses.insert_many(courses)
        logger.info(f"Created {len(courses_result.inserted_ids)} courses")
        
        # Create sample grades
        if students and courses:
            grades = []
            for i, student in enumerate(students[:5]):  # First 5 students
                for j, course in enumerate(courses):
                    grade = {
                        "student_id": student["student_id"],
                        "course_id": course["code"],
                        "assignment_name": f"Assignment {j+1}",
                        "grade_type": "assignment",
                        "points_earned": 85 + (i * 2) - (j * 3),
                        "points_possible": 100,
                        "percentage": 85 + (i * 2) - (j * 3),
                        "letter_grade": "B+",
                        "grade_points": 3.3,
                        "weight": 1.0,
                        "graded_by": str(teacher_user["_id"]) if teacher_user else "teacher",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    grades.append(grade)
            
            if grades:
                grades_result = await db.grades.insert_many(grades)
                logger.info(f"Created {len(grades_result.inserted_ids)} grade records")
        
        # Create sample attendance
        if students and courses:
            attendance_records = []
            start_date = date.today() - timedelta(days=30)
            
            for i in range(30):  # Last 30 days
                current_date = start_date + timedelta(days=i)
                for student in students[:5]:  # First 5 students
                    for course in courses:
                        # 85% attendance rate
                        status = "present" if (i + hash(student["student_id"])) % 10 < 8.5 else "absent"
                        
                        record = {
                            "student_id": student["student_id"],
                            "course_id": course["code"],
                            "date": current_date,
                            "status": status,
                            "marked_by": str(teacher_user["_id"]) if teacher_user else "teacher",
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                        attendance_records.append(record)
            
            if attendance_records:
                attendance_result = await db.attendance.insert_many(attendance_records)
                logger.info(f"Created {len(attendance_result.inserted_ids)} attendance records")
        
        # Create sample notifications
        notifications = [
            {
                "user_id": str(student_user["_id"]) if student_user else "student",
                "title": "Grade Updated",
                "message": "Your grade for Computer Science 101 has been updated.",
                "type": "grade",
                "is_read": False,
                "created_at": datetime.utcnow()
            },
            {
                "user_id": str(student_user["_id"]) if student_user else "student",
                "title": "Low Attendance Alert",
                "message": "Your attendance in Mathematics 201 is below 75%.",
                "type": "attendance",
                "is_read": False,
                "created_at": datetime.utcnow()
            }
        ]
        
        notifications_result = await db.notifications.insert_many(notifications)
        logger.info(f"Created {len(notifications_result.inserted_ids)} notifications")
        
        logger.info("✅ Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database seeding failed: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())