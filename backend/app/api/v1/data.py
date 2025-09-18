from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.core.security import get_current_user, TokenData
from app.core.database import get_students_collection, get_courses_collection
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
import pandas as pd
import json
from datetime import datetime

router = APIRouter(prefix="/data", tags=["Data Ingestion"])

@router.post("/upload", response_model=dict)
async def upload_data(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """
    Upload and process CSV data for students or courses
    
    Args:
        file: CSV file with student or course data
        current_user: Current authenticated user
        students_collection: Students database collection
        courses_collection: Courses database collection
    
    Returns:
        Status of data ingestion
    
    Raises:
        HTTPException: If file invalid or server error
    """
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")
        
        df = pd.read_csv(file.file)
        
        # Process student data
        if "student_id" in df.columns:
            students_data = []
            for _, row in df.iterrows():
                student_data = row.to_dict()
                student_data["created_at"] = datetime.utcnow()
                student_data["updated_at"] = datetime.utcnow()
                student_data["is_active"] = True
                students_data.append(student_data)
            
            if students_data:
                await students_collection.insert_many(students_data)
        
        # Process course data
        elif "code" in df.columns:
            courses_data = []
            for _, row in df.iterrows():
                course_data = row.to_dict()
                course_data["created_at"] = datetime.utcnow()
                course_data["updated_at"] = datetime.utcnow()
                course_data["is_active"] = True
                course_data["students"] = []
                course_data["student_count"] = 0
                courses_data.append(course_data)
            
            if courses_data:
                await courses_collection.insert_many(courses_data)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV format")
        
        # Log successful upload
        logger.info(f"Data uploaded successfully: {file.filename}")
        
        return {"message": "Data uploaded successfully", "filename": file.filename}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to upload data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))