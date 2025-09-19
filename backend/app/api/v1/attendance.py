import traceback
from fastapi import APIRouter, Body, Depends, HTTPException, status
from app.core.security import get_current_user, TokenData
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_attendance_collection, get_students_collection, get_courses_collection
from datetime import datetime, date
from loguru import logger

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/")
async def get_attendance_records(
    student_id: str = None,
    course_id: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    try:
        query = {}

        # Resolve student_id
        if student_id:
            if student_id == "me":
                student = await students_collection.find_one({"user_id": current_user.user_id})
                if student:
                    query["student_id"] = student["student_id"]
                else:
                    return []
            else:
                query["student_id"] = student_id

        # Filter by course
        if course_id:
            query["course_id"] = course_id

        # Filter by date
        if date_from:
            query["date"] = {"$gte": datetime.fromisoformat(date_from)}
        if date_to:
            if "date" in query:
                query["date"]["$lte"] = datetime.fromisoformat(date_to)
            else:
                query["date"] = {"$lte": datetime.fromisoformat(date_to)}

        # Fetch from Mongo
        records = await attendance_collection.find(query).limit(limit).to_list(length=limit)

        # Format result
        result = [{
            "id": str(r["_id"]),
            "student_id": r.get("student_id"),
            "course_id": r.get("course_id"),
            "date": r.get("date"),
            "status": r.get("status"),
            "marked_by": r.get("marked_by"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at")
        } for r in records]

        return result

    except Exception as e:
        logger.error(f"Error fetching attendance: {e}")
        return []

@router.post("/bulk")
async def create_bulk_attendance(
    bulk_data: dict = Body(...),
    current_user: TokenData = Depends(get_current_user),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
):
    try:
        print("Received bulk data:", bulk_data)  # Debug log

        # Extract data from request
        course_id = bulk_data.get("course_id")
        attendance_date = bulk_data.get("date")
        records = bulk_data.get("attendance_records", [])  # ✅ define records here

        if not course_id or not attendance_date or not records:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Ensure attendance_date is a datetime (MongoDB can store it)
        if isinstance(attendance_date, str):
            attendance_date = datetime.strptime(attendance_date, "%Y-%m-%d")
        elif isinstance(attendance_date, date):
            attendance_date = datetime.combine(attendance_date, datetime.min.time())

        # Delete existing records for this course and date
        await attendance_collection.delete_many({
            "course_id": course_id,
            "date": attendance_date
        })

        # Prepare documents to insert
        attendance_docs = []
        for record in records:
            if not record.get("student_id"):
                continue
            doc = {
                "student_id": record.get("student_id"),
                "course_id": course_id,
                "date": attendance_date,
                "status": record.get("status", "present"),
                "notes": record.get("notes", ""),
                "marked_by": current_user.user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            attendance_docs.append(doc)

        # Insert new records
        if attendance_docs:
            await attendance_collection.insert_many(attendance_docs)

        return {"message": f"Bulk attendance created successfully for {len(attendance_docs)} students"}

    except Exception as e:
        print("Error creating bulk attendance:", e)
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create bulk attendance")

@router.post("/")
async def create_attendance(
    attendance_data: dict,
    current_user: TokenData = Depends(get_current_user),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
):
    """Create a new attendance record"""
    try:
        doc = {
            "student_id": attendance_data.get("student_id"),
            "course_id": attendance_data.get("course_id"),
            "date": attendance_data.get("date"),
            "status": attendance_data.get("status", "present"),
            "notes": attendance_data.get("notes", ""),
            "marked_by": current_user.user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await attendance_collection.insert_one(doc)
        return {"message": "Attendance created successfully", "id": str(result.inserted_id)}
        
    except Exception as e:
        logger.error(f"Error creating attendance: {e}")
        raise HTTPException(status_code=500, detail="Failed to create attendance")