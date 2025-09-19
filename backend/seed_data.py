#!/usr/bin/env python3
"""
EduPredict Database Seeding Script
Seeds the MongoDB database with sample data for testing and demonstration
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta, UTC
from loguru import logger
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_to_mongo, get_users_collection, get_students_collection, get_courses_collection, get_grades_collection, get_attendance_collection, close_mongo_connection
from app.core.security import get_password_hash

async def seed_users():
    """Seed user accounts"""
    try:
        collection = await get_users_collection()
        
        # Clear existing users
        await collection.delete_many({})
        
        users = [
            {
                "email": "admin@edupredict.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "hashed_password": get_password_hash("admin123"),
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            },
            {
                "email": "teacher@edupredict.com",
                "first_name": "John",
                "last_name": "Teacher",
                "role": "teacher",
                "hashed_password": get_password_hash("teacher123"),
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            },
            {
                "email": "student@edupredict.com",
                "first_name": "Jane",
                "last_name": "Student",
                "role": "student",
                "hashed_password": get_password_hash("student123"),
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            },
            {
                "email": "analyst@edupredict.com",
                "first_name": "Data",
                "last_name": "Analyst",
                "role": "analyst",
                "hashed_password": get_password_hash("analyst123"),
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
        ]
        
        # Add additional sample users
        departments = ["Computer Science", "Engineering", "Mathematics", "Physics", "Chemistry", "Biology"]
        for i in range(5, 30):
            dept = random.choice(departments)
            users.append({
                "email": f"student{i}@edupredict.com",
                "first_name": f"Student{i}",
                "last_name": f"Test{i}",
                "role": "student",
                "hashed_password": get_password_hash("student123"),
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            })
        
        result = await collection.insert_many(users)
        logger.info(f"✅ Seeded {len(result.inserted_ids)} users")
        return result.inserted_ids
        
    except Exception as e:
        logger.error(f"❌ Failed to seed users: {e}")
        raise

async def seed_students(user_ids):
    """Seed student profiles"""
    try:
        collection = await get_students_collection()
        users_collection = await get_users_collection()
        
        # Clear existing students
        await collection.delete_many({})
        
        # Get student users
        student_users = await users_collection.find({"role": "student"}).to_list(length=None)
        
        students = []
        departments = ["Computer Science", "Engineering", "Mathematics", "Physics", "Chemistry", "Biology"]
        programs = ["Bachelor of Science", "Bachelor of Engineering", "Bachelor of Arts"]
        
        for i, user in enumerate(student_users):
            # Generate valid random dates (avoid invalid days like Feb 30)
            year = 2000 + random.randint(1, 4)
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # Safe max day to avoid invalid dates
            dept = random.choice(departments)
            program = random.choice(programs)
            
            student = {
                "student_id": f"STU-{str(i+1).zfill(3)}",
                "user_id": str(user["_id"]),
                "date_of_birth": datetime(year, month, day),  # Convert to datetime
                "gender": random.choice(["male", "female"]),
                "department": dept,
                "program": program,
                "enrollment_date": datetime(2020 + random.randint(0, 3), 9, 1),  # Convert to datetime
                "expected_graduation": datetime(2024 + random.randint(0, 2), 5, 15),  # Convert to datetime
                "current_semester": random.randint(1, 8),
                "current_year": random.randint(1, 4),
                "gpa": round(random.uniform(1.8, 3.9), 2),
                "total_credits": random.randint(30, 120),
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
            students.append(student)
        
        result = await collection.insert_many(students)
        logger.info(f"✅ Seeded {len(result.inserted_ids)} students")
        return students
        
    except Exception as e:
        logger.error(f"❌ Failed to seed students: {e}")
        raise

async def seed_courses(user_ids):
    """Seed course data"""
    try:
        collection = await get_courses_collection()
        users_collection = await get_users_collection()
        
        # Clear existing courses
        await collection.delete_many({})
        
        # Get teacher users
        teacher_users = await users_collection.find({"role": "teacher"}).to_list(length=None)
        
        courses_data = [
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
                "max_students": 30
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
                "max_students": 25
            },
            {
                "name": "General Physics I",
                "code": "PHYS-101",
                "description": "Introduction to mechanics and thermodynamics",
                "department": "Physics",
                "credits": 4,
                "semester": "Fall 2024",
                "academic_year": "2024",
                "schedule": "MWF 09:00-10:00",
                "room": "PHYS-301",
                "max_students": 35
            },
            {
                "name": "Engineering Mechanics",
                "code": "ENG-102",
                "description": "Statics and dynamics in engineering",
                "department": "Engineering",
                "credits": 3,
                "semester": "Fall 2024",
                "academic_year": "2024",
                "schedule": "TTh 11:00-12:30",
                "room": "ENG-150",
                "max_students": 28
            },
            {
                "name": "General Chemistry",
                "code": "CHEM-101",
                "description": "Basic principles of chemistry",
                "department": "Chemistry",
                "credits": 4,
                "semester": "Fall 2024",
                "academic_year": "2024",
                "schedule": "MWF 13:00-14:00",
                "room": "CHEM-210",
                "max_students": 32
            }
        ]
        
        courses = []
        for i, course_data in enumerate(courses_data):
            teacher = teacher_users[i % len(teacher_users)] if teacher_users else None
            
            course = {
                **course_data,
                "teacher_id": str(teacher["_id"]) if teacher else "",
                "teacher_name": f"{teacher['first_name']} {teacher['last_name']}" if teacher else "",
                "students": [],
                "student_count": 0,
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
            courses.append(course)
        
        result = await collection.insert_many(courses)
        logger.info(f"✅ Seeded {len(result.inserted_ids)} courses")
        return courses
        
    except Exception as e:
        logger.error(f"❌ Failed to seed courses: {e}")
        raise

async def seed_enrollments(students, courses):
    """Seed student enrollments in courses"""
    try:
        courses_collection = await get_courses_collection()
        
        # Enroll students in random courses
        for student in students:
            # Each student enrolls in 3-5 courses
            num_courses = random.randint(3, 5)
            selected_courses = random.sample(courses, min(num_courses, len(courses)))
            
            for course in selected_courses:
                await courses_collection.update_one(
                    {"code": course["code"]},
                    {
                        "$addToSet": {"students": student["student_id"]},
                        "$inc": {"student_count": 1}
                    }
                )
        
        logger.info("✅ Seeded student enrollments")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed enrollments: {e}")
        raise

async def seed_grades(students, courses):
    """Seed grade data"""
    try:
        collection = await get_grades_collection()
        
        # Clear existing grades
        await collection.delete_many({})
        
        grades = []
        assignment_types = ["assignment", "quiz", "exam", "project", "participation"]
        
        for student in students:
            # Generate grades for enrolled courses
            student_courses = random.sample(courses, random.randint(3, 5))
            
            for course in student_courses:
                # Generate 3-5 grades per course
                for j in range(random.randint(3, 5)):
                    assignment_type = random.choice(assignment_types)
                    points_possible = random.choice([50, 75, 100, 150, 200])
                    
                    # Base performance on student's GPA
                    base_performance = student["gpa"] / 4.0
                    variation = random.uniform(-0.2, 0.2)
                    performance = max(0.0, min(1.0, base_performance + variation))
                    
                    points_earned = round(points_possible * performance)
                    percentage = (points_earned / points_possible * 100) if points_possible > 0 else 0
                    
                    grade = {
                        "student_id": student["student_id"],
                        "course_id": course["code"],
                        "course_name": course["name"],
                        "assignment_name": f"{assignment_type.title()} {j+1}",
                        "grade_type": assignment_type,
                        "points_earned": points_earned,
                        "points_possible": points_possible,
                        "percentage": round(percentage, 1),
                        "letter_grade": calculate_letter_grade(percentage),
                        "grade_points": percentage_to_gpa(percentage),
                        "weight": 1.0,
                        "notes": "",
                        "graded_by": course.get("teacher_id", "system"),
                        "created_at": datetime.now(UTC) - timedelta(days=random.randint(1, 90)),
                        "updated_at": datetime.now(UTC)
                    }
                    grades.append(grade)
        
        if grades:
            result = await collection.insert_many(grades)
            logger.info(f"✅ Seeded {len(result.inserted_ids)} grades")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed grades: {e}")
        raise

async def seed_attendance(students, courses):
    """Seed attendance data"""
    try:
        collection = await get_attendance_collection()
        
        # Clear existing attendance
        await collection.delete_many({})
        
        attendance_records = []
        
        # Generate attendance for the last 30 days
        for day in range(30):
            attendance_date = date.today() - timedelta(days=day)
            
            # Skip weekends
            if attendance_date.weekday() >= 5:
                continue
                
            for student in students:
                # Student attends 2-4 courses per day
                student_courses = random.sample(courses, random.randint(2, 4))
                
                for course in student_courses:
                    # Attendance probability based on student's overall performance
                    base_attendance = 0.85
                    gpa_factor = (student["gpa"] - 2.0) / 2.0 * 0.15  # GPA influence
                    attendance_prob = max(0.5, min(0.98, base_attendance + gpa_factor))
                    
                    status = "present" if random.random() < attendance_prob else random.choice(["absent", "late", "excused"])
                    
                    record = {
                        "student_id": student["student_id"],
                        "course_id": course["code"],
                        "date": datetime(attendance_date.year, attendance_date.month, attendance_date.day),  # Convert to datetime
                        "status": status,
                        "notes": "",
                        "marked_by": course.get("teacher_id", "system"),
                        "created_at": datetime.now(UTC),
                        "updated_at": datetime.now(UTC)
                    }
                    attendance_records.append(record)
        
        if attendance_records:
            result = await collection.insert_many(attendance_records)
            logger.info(f"✅ Seeded {len(result.inserted_ids)} attendance records")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed attendance: {e}")
        raise


def calculate_letter_grade(percentage):
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

def percentage_to_gpa(percentage):
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

async def main():
    """Main seeding function"""
    try:
        logger.info("🚀 Starting EduPredict database seeding...")
        
        # Connect to MongoDB
        connected = await connect_to_mongo()
        if not connected:
            logger.error("❌ Failed to connect to MongoDB")
            return
        
        # Seed data in order
        user_ids = await seed_users()
        students = await seed_students(user_ids)
        courses = await seed_courses(user_ids)
        await seed_enrollments(students, courses)
        await seed_grades(students, courses)
        await seed_attendance(students, courses)
        
        logger.info("🎉 Database seeding completed successfully!")
        logger.info("📋 Sample login credentials:")
        logger.info("   Admin: admin@edupredict.com / admin123")
        logger.info("   Teacher: teacher@edupredict.com / teacher123")
        logger.info("   Student: student@edupredict.com / student123")
        logger.info("   Analyst: analyst@edupredict.com / analyst123")
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())