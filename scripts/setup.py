#!/usr/bin/env python3
"""
EduPredict Setup Script
Initializes the database, creates sample data, and sets up the environment
"""

import asyncio
import os
import sys
import pandas as pd
from datetime import datetime, date
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import connect_to_mongo, get_database
from app.models.user import UserCreate, UserRole
from app.services.user_service import UserService
from app.core.security import get_password_hash


async def create_sample_users():
    """Create sample users for testing"""
    print("Creating sample users...")
    
    user_service = UserService()
    
    sample_users = [
        {
            "email": "admin@edupredict.com",
            "password": "admin123",
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.ADMIN
        },
        {
            "email": "teacher@edupredict.com",
            "password": "teacher123",
            "first_name": "John",
            "last_name": "Teacher",
            "role": UserRole.TEACHER
        },
        {
            "email": "student@edupredict.com",
            "password": "student123",
            "first_name": "Jane",
            "last_name": "Student",
            "role": UserRole.STUDENT
        },
        {
            "email": "analyst@edupredict.com",
            "password": "analyst123",
            "first_name": "Data",
            "last_name": "Analyst",
            "role": UserRole.ANALYST
        }
    ]
    
    for user_data in sample_users:
        try:
            # Check if user already exists
            existing_user = await user_service.get_user_by_email(user_data["email"])
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                continue
            
            # Create user
            user_create = UserCreate(**user_data)
            created_user = await user_service.create_user(user_create)
            print(f"Created user: {created_user.email} ({created_user.role})")
            
        except Exception as e:
            print(f"Error creating user {user_data['email']}: {e}")


async def load_sample_students():
    """Load sample student data from CSV"""
    print("Loading sample student data...")
    
    try:
        # Read CSV file
        csv_path = Path(__file__).parent.parent / "data" / "sample_data" / "students_sample.csv"
        df = pd.read_csv(csv_path)
        
        # Get database collections
        db = get_database()
        students_collection = db.students
        users_collection = db.users
        
        # Process each student
        for _, row in df.iterrows():
            try:
                # Check if student already exists
                existing_student = await students_collection.find_one({"student_id": row["student_id"]})
                if existing_student:
                    print(f"Student {row['student_id']} already exists, skipping...")
                    continue
                
                # Create user account for student
                user_data = {
                    "email": row["email"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "role": "student",
                    "is_active": True,
                    "hashed_password": get_password_hash("student123"),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Check if user already exists
                existing_user = await users_collection.find_one({"email": row["email"]})
                if not existing_user:
                    user_result = await users_collection.insert_one(user_data)
                    user_id = user_result.inserted_id
                else:
                    user_id = existing_user["_id"]
                
                # Create student profile
                student_data = {
                    "student_id": row["student_id"],
                    "user_id": user_id,
                    "date_of_birth": pd.to_datetime(row["date_of_birth"]).date(),
                    "gender": row["gender"],
                    "department": row["department"],
                    "program": row["program"],
                    "enrollment_date": pd.to_datetime(row["enrollment_date"]).date(),
                    "expected_graduation": pd.to_datetime(row["enrollment_date"]).date().replace(year=pd.to_datetime(row["enrollment_date"]).year + 4),
                    "current_semester": int(row["current_semester"]),
                    "current_year": int(row["current_year"]),
                    "gpa": float(row["gpa"]) if pd.notna(row["gpa"]) else None,
                    "total_credits": int(row["total_credits"]),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True
                }
                
                await students_collection.insert_one(student_data)
                print(f"Created student: {row['student_id']} - {row['first_name']} {row['last_name']}")
                
            except Exception as e:
                print(f"Error creating student {row['student_id']}: {e}")
                
    except Exception as e:
        print(f"Error loading sample students: {e}")


async def create_sample_courses():
    """Create sample courses"""
    print("Creating sample courses...")
    
    db = get_database()
    courses_collection = db.courses
    
    sample_courses = [
        {
            "course_code": "CS101",
            "course_name": "Introduction to Computer Science",
            "department": "Computer Science",
            "credits": 3,
            "semester": "Fall 2023",
            "instructor": "Dr. Smith",
            "description": "Basic concepts of computer science and programming",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "course_code": "MATH201",
            "course_name": "Calculus II",
            "department": "Mathematics",
            "credits": 4,
            "semester": "Fall 2023",
            "instructor": "Dr. Johnson",
            "description": "Advanced calculus concepts and applications",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "course_code": "PHYS101",
            "course_name": "General Physics I",
            "department": "Physics",
            "credits": 4,
            "semester": "Fall 2023",
            "instructor": "Dr. Williams",
            "description": "Mechanics, waves, and thermodynamics",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "course_code": "ENG102",
            "course_name": "Engineering Mechanics",
            "department": "Engineering",
            "credits": 3,
            "semester": "Fall 2023",
            "instructor": "Dr. Brown",
            "description": "Statics and dynamics in engineering",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "course_code": "CHEM101",
            "course_name": "General Chemistry",
            "department": "Chemistry",
            "credits": 4,
            "semester": "Fall 2023",
            "instructor": "Dr. Davis",
            "description": "Basic principles of chemistry",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
    ]
    
    for course in sample_courses:
        try:
            # Check if course already exists
            existing_course = await courses_collection.find_one({"course_code": course["course_code"]})
            if existing_course:
                print(f"Course {course['course_code']} already exists, skipping...")
                continue
            
            await courses_collection.insert_one(course)
            print(f"Created course: {course['course_code']} - {course['course_name']}")
            
        except Exception as e:
            print(f"Error creating course {course['course_code']}: {e}")


async def setup_database_indexes():
    """Create database indexes for better performance"""
    print("Setting up database indexes...")
    
    db = get_database()
    
    try:
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("role")
        
        # Students collection indexes
        await db.students.create_index("student_id", unique=True)
        await db.students.create_index("user_id")
        await db.students.create_index("department")
        
        # Courses collection indexes
        await db.courses.create_index("course_code", unique=True)
        await db.courses.create_index("department")
        
        # Attendance collection indexes
        await db.attendance.create_index([("student_id", 1), ("course_id", 1), ("date", 1)])
        
        # Grades collection indexes
        await db.grades.create_index([("student_id", 1), ("course_id", 1)])
        
        # Notifications collection indexes
        await db.notifications.create_index("user_id")
        await db.notifications.create_index("created_at")
        
        print("Database indexes created successfully")
        
    except Exception as e:
        print(f"Error creating indexes: {e}")


async def main():
    """Main setup function"""
    print("Starting EduPredict setup...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB")
        
        # Setup database indexes
        await setup_database_indexes()
        
        # Create sample data
        await create_sample_users()
        await load_sample_students()
        await create_sample_courses()
        
        print("\nSetup completed successfully!")
        print("\nSample login credentials:")
        print("Admin: admin@edupredict.com / admin123")
        print("Teacher: teacher@edupredict.com / teacher123")
        print("Student: student@edupredict.com / student123")
        print("Analyst: analyst@edupredict.com / analyst123")
        
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
