import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId
import bcrypt

MONGO_URI = "mongodb+srv://ayeshaafzal1573:bzRBxk5ae4TcuRO7@cluster0.c8tez.mongodb.net/edupredict?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "edupredict"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def seed_users():
    password1 = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    password2 = bcrypt.hashpw("student123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    users = [
        {
            "_id": ObjectId(),
            "email": "analyst@gmail.com",
            "first_name": "Analyst",
            "last_name": "Khan",
            "role": "analyst",
            "is_active": True,
            "hashed_password": "analyst123",
          "created_at": datetime.now(timezone.utc),
"updated_at": datetime.now(timezone.utc),
"last_login": datetime.now(timezone.utc),
        },
        {
            "_id": ObjectId(),
            "email": "ayesha@gmail.com",
            "first_name": "Aisha",
            "last_name": "Afzal",
            "role": "student",
            "is_active": True,
            "hashed_password":" ayesha123",
           "created_at": datetime.now(timezone.utc),
"updated_at": datetime.now(timezone.utc),
"last_login": datetime.now(timezone.utc),
        }
    ]
    await db.users.insert_many(users)
    print("✅ Users inserted!")

async def seed_predictions():
    predictions = [
        {
            "_id": ObjectId(),
            "user_email": "analyst@gmail.com",
            "subject": "Math",
            "confidence": 0.87,
            "prediction": "Pass",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_email": "ayesha@gmail.com",
            "subject": "Science",
            "confidence": 0.65,
            "prediction": "Needs Improvement",
            "created_at": datetime.utcnow()
        }
    ]
    await db.predictions.insert_many(predictions)
    print("✅ Predictions inserted!")

async def seed_notifications():
    notifications = [
        {
            "_id": ObjectId(),
            "user_email": "analyst@gmail.com",
            "message": "New student report generated",
            "is_read": False,
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_email": "ayesha@gmail.com",
            "message": "Welcome to EduPredict! 🎉",
            "is_read": True,
            "created_at": datetime.utcnow()
        }
    ]
    await db.notifications.insert_many(notifications)
    print("✅ Notifications inserted!")

async def seed_logs():
    logs = [
        {
            "_id": ObjectId(),
            "action": "login",
            "user_email": "analyst@gmail.com",
            "status": "success",
            "timestamp": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "action": "view_dashboard",
            "user_email": "ayesha@gmail.com",
            "status": "success",
            "timestamp": datetime.utcnow()
        }
    ]
    await db.logs.insert_many(logs)
    print("✅ Logs inserted!")

async def seed():
    await seed_users()
    await seed_predictions()
    await seed_notifications()
    await seed_logs()

if __name__ == "__main__":
    asyncio.run(seed())
