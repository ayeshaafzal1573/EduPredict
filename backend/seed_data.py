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
from bson import ObjectId

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

async def create_sample_students(user_ids):
    """Create sample student profiles"""
    students = [
        {
            "student_id": "STU001",
            "user_id": user_ids.get("student@edupredict.com"),
            "date_of_birth": date(2002, 5, 15),
            "gender": "female",
            "department": "Computer Science",
            "program": "Bachelor of Science",
            "enrollment_date": date(2021, 9, 1),
            "expected_graduation": date(2025, 5, 15),
            "current_semester": 5,
            "current_year": 3,
            "gpa": 3.2,
            "total_credits": 75,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "student_id": "STU002",
            "user_id": ObjectId(),  # Placeholder user
            "date_of_birth": date(2001, 8, 22),
            "gender": "male",
            "department": "Engineering",
            "program": "Bachelor of Engineering",
            "enrollment_date": date(2020, 9, 1),
            "expected_graduation": date(2024, 5, 15),
            "current_semester": 7,
            "current_year": 4,
            "gpa": 3.8,
            "total_credits": 105,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "student_id": "STU003",
            "user_id": ObjectId(),  # Placeholder user
            "date_of_birth": date(2003, 1, 10),
            "gender": "male",
            "department": "Mathematics",
            "program": "Bachelor of Science",
            "enrollment_date": date(2022, 1, 15),
            "expected_graduation": date(2026, 1, 15),
            "current_semester": 3,
            "current_year": 2,
            "gpa": 2.1,
            "total_credits": 45,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    return students

async def create_sample_courses(teacher_id):
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
            "teacher_id": teacher_id,
            "teacher_name": "John Teacher",
            "students": ["STU001", "STU002"],
            "student_count": 2,
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
            "teacher_id": teacher_id,
            "teacher_name": "John Teacher",
            "students": ["STU001", "STU003"],
            "student_count": 2,
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
            "teacher_id": teacher_id,
            "teacher_name": "John Teacher",
            "students": ["STU001"],
            "student_count": 1,
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
        
        # Create collections
        users_collection = db.users
        students_collection = db.students
        courses_collection = db.courses
        grades_collection = db.grades
        attendance_collection = db.attendance
        notifications_collection = db.notifications
        
        # Clear existing data
        await users_collection.delete_many({})
        await students_collection.delete_many({})
        await courses_collection.delete_many({})
        await grades_collection.delete_many({})
        await attendance_collection.delete_many({})
        await notifications_collection.delete_many({})
        
        # Create users
        users = await create_sample_users()
        user_result = await users_collection.insert_many(users)
        logger.info(f"Created {len(user_result.inserted_ids)} users")
        
        # Get user IDs for linking
        user_ids = {}
        for user, user_id in zip(users, user_result.inserted_ids):
            user_ids[user["email"]] = user_id
        
        # Create students
        students = await create_sample_students(user_ids)
        students_result = await students_collection.insert_many(students)
        logger.info(f"Created {len(students_result.inserted_ids)} students")
        
        # Create courses
        teacher_id = str(user_ids["teacher@edupredict.com"])
        courses = await create_sample_courses(teacher_id)
        courses_result = await courses_collection.insert_many(courses)
        logger.info(f"Created {len(courses_result.inserted_ids)} courses")
        
        # Create sample grades
        grades = []
        for student in students:
            for course in courses:
                if student["student_id"] in course["students"]:
                    # Create multiple assignments per course
                    for i in range(3):
                        grade = {
                            "student_id": student["student_id"],
                            "course_id": course["code"],
                            "assignment_name": f"Assignment {i+1}",
                            "grade_type": "assignment",
                            "points_earned": 85 + (i * 2),
                            "points_possible": 100,
                            "percentage": 85 + (i * 2),
                            "letter_grade": "B+",
                            "grade_points": 3.3,
                            "weight": 1.0,
                            "graded_by": teacher_id,
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                        grades.append(grade)
        
        if grades:
            grades_result = await grades_collection.insert_many(grades)
            logger.info(f"Created {len(grades_result.inserted_ids)} grade records")
        
        # Create sample attendance
        attendance_records = []
        start_date = date.today() - timedelta(days=30)
        
        for i in range(30):  # Last 30 days
            current_date = start_date + timedelta(days=i)
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
                
            for student in students:
                for course in courses:
                    if student["student_id"] in course["students"]:
                        # 85% attendance rate
                        status = "present" if (i + hash(student["student_id"])) % 10 < 8.5 else "absent"
                        
                        record = {
                            "student_id": student["student_id"],
                            "course_id": course["code"],
                            "date": current_date,
                            "status": status,
                            "marked_by": teacher_id,
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                        attendance_records.append(record)
        
        if attendance_records:
            attendance_result = await attendance_collection.insert_many(attendance_records)
            logger.info(f"Created {len(attendance_result.inserted_ids)} attendance records")
        
        # Create sample notifications
        notifications = [
            {
                "user_id": str(user_ids["student@edupredict.com"]),
                "title": "Welcome to EduPredict",
                "message": "Welcome to the EduPredict system! Explore your dashboard to see your academic progress.",
                "is_read": False,
                "created_at": datetime.utcnow()
            },
            {
                "user_id": str(user_ids["teacher@edupredict.com"]),
                "title": "New Semester Started",
                "message": "Fall 2024 semester has started. Please update your course materials and attendance.",
                "is_read": False,
                "created_at": datetime.utcnow()
            }
        ]
        
        notifications_result = await notifications_collection.insert_many(notifications)
        logger.info(f"Created {len(notifications_result.inserted_ids)} notifications")
        
        logger.info("✅ Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database seeding failed: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())