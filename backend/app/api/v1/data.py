from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.services.student_service import StudentService, get_student_service
from app.services.course_service import CourseService, get_course_service
from app.core.hdfs_utils import HDFSClient
from loguru import logger
import pandas as pd
import json

router = APIRouter(prefix="/data", tags=["Data Ingestion"])

@router.post("/upload", response_model=dict)
async def upload_data(file: UploadFile = File(...), student_service: StudentService = Depends(get_student_service), course_service: CourseService = Depends(get_course_service)):
    """
    Upload and process CSV data for students or courses
    
    Args:
        file: CSV file with student or course data
        student_service: Student service dependency
        course_service: Course service dependency
    
    Returns:
        Status of data ingestion
    
    Raises:
        HTTPException: If file invalid or server error
    """
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")
        df = pd.read_csv(file.file)
        # Assume CSV has columns matching StudentCreate or CourseCreate
        if "student_id" in df.columns:
            for _, row in df.iterrows():
                student_data = row.to_dict()
                await student_service.create_student(StudentCreate(**student_data))
        elif "code" in df.columns:
            for _, row in df.iterrows():
                course_data = row.to_dict()
                await course_service.create_course(CourseCreate(**course_data))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV format")
        
        # Save to HDFS
        hdfs_client = HDFSClient()
        hdfs_path = f"/edupredict/uploads/{file.filename}"
        hdfs_client.save_data(df.to_json().encode(), hdfs_path)
        
        return {"message": "Data uploaded successfully", "hdfs_path": hdfs_path}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to upload data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))