# EduPredict API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Refresh
Tokens expire after 30 minutes. Use the refresh endpoint to get a new token:

```http
POST /auth/refresh
Authorization: Bearer <refresh-token>
```

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### POST /auth/login
Authenticate user and get access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /auth/me
Get current user information.

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "last_login": "2023-01-01T12:00:00Z"
}
```

### Users Management

#### GET /users
Get list of users (Admin only).

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100)
- `role` (string): Filter by user role

**Response:**
```json
[
  {
    "id": "user_id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z"
  }
]
```

#### GET /users/{user_id}
Get user by ID.

#### PUT /users/{user_id}
Update user information.

#### DELETE /users/{user_id}
Delete user (soft delete).

### Students

#### GET /students
Get list of students.

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Number of records
- `department` (string): Filter by department
- `program` (string): Filter by program
- `year` (int): Filter by current year

**Response:**
```json
[
  {
    "id": "student_id",
    "student_id": "STU001",
    "user_id": "user_id",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Computer Science",
    "program": "Bachelor of Science",
    "current_semester": 5,
    "current_year": 3,
    "gpa": 3.2,
    "total_credits": 75
  }
]
```

#### POST /students
Create new student profile.

#### GET /students/{student_id}
Get student details.

#### PUT /students/{student_id}
Update student information.

#### GET /students/{student_id}/performance
Get student performance metrics.

**Response:**
```json
{
  "student_id": "STU001",
  "semester": 5,
  "year": 3,
  "gpa": 3.2,
  "credits_completed": 75,
  "attendance_rate": 0.85,
  "dropout_risk_score": 0.25,
  "predicted_grade": 3.4,
  "risk_factors": ["Low attendance in Math"],
  "recommendations": ["Attend tutoring sessions"]
}
```

### Courses

#### GET /courses
Get list of courses.

#### POST /courses
Create new course.

#### GET /courses/{course_id}
Get course details.

#### PUT /courses/{course_id}
Update course information.

#### DELETE /courses/{course_id}
Delete course.

### Attendance

#### GET /attendance
Get attendance records.

**Query Parameters:**
- `student_id` (string): Filter by student
- `course_id` (string): Filter by course
- `date_from` (date): Start date filter
- `date_to` (date): End date filter

#### POST /attendance
Mark attendance.

**Request Body:**
```json
{
  "student_id": "STU001",
  "course_id": "CS101",
  "date": "2023-01-01",
  "status": "present",
  "notes": "On time"
}
```

#### GET /attendance/student/{student_id}
Get attendance for specific student.

### Grades

#### GET /grades
Get grade records.

#### POST /grades
Create grade entry.

**Request Body:**
```json
{
  "student_id": "STU001",
  "course_id": "CS101",
  "assignment_type": "exam",
  "assignment_name": "Midterm Exam",
  "points_earned": 85,
  "points_possible": 100,
  "grade_date": "2023-01-01"
}
```

#### GET /grades/student/{student_id}
Get grades for specific student.

### Analytics

#### GET /analytics/dropout-prediction/{student_id}
Get dropout risk prediction for student.

**Response:**
```json
{
  "student_id": "STU001",
  "dropout_risk_score": 0.25,
  "dropout_prediction": false,
  "risk_level": "low",
  "risk_factors": [
    "Low attendance in Math",
    "Declining GPA trend"
  ],
  "recommendations": [
    "Schedule academic counseling",
    "Improve attendance"
  ]
}
```

#### GET /analytics/grade-prediction/{student_id}/{course_id}
Get grade prediction for student in specific course.

**Response:**
```json
{
  "student_id": "STU001",
  "course_id": "CS101",
  "predicted_grade": 3.4,
  "grade_letter": "B+",
  "confidence": 0.85,
  "factors": [
    "Strong performance in assignments",
    "Good attendance record"
  ]
}
```

#### GET /analytics/performance-trends
Get performance trends data.

#### GET /analytics/dashboard-stats/{role}
Get dashboard statistics for specific role.

**Response:**
```json
{
  "total_students": 150,
  "at_risk_students": 12,
  "average_gpa": 3.2,
  "attendance_rate": 0.87,
  "recent_alerts": 5
}
```

### Notifications

#### GET /notifications
Get user notifications.

**Query Parameters:**
- `unread_only` (bool): Show only unread notifications
- `limit` (int): Number of notifications to return

**Response:**
```json
[
  {
    "id": "notification_id",
    "title": "Low Attendance Alert",
    "message": "Your attendance in CS101 is below 75%",
    "type": "warning",
    "is_read": false,
    "created_at": "2023-01-01T12:00:00Z"
  }
]
```

#### PUT /notifications/{notification_id}/read
Mark notification as read.

#### PUT /notifications/read-all
Mark all notifications as read.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate limited:
- Authentication endpoints: 5 requests per minute
- General endpoints: 100 requests per minute
- Analytics endpoints: 20 requests per minute

## Pagination

List endpoints support pagination:

```http
GET /students?skip=0&limit=20
```

Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "has_next": true
}
```

## WebSocket Endpoints

Real-time notifications are available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications');
ws.onmessage = function(event) {
    const notification = JSON.parse(event.data);
    console.log('New notification:', notification);
};
```

## SDK and Client Libraries

Official client libraries are available for:
- JavaScript/TypeScript
- Python
- Java
- C#

Example usage (JavaScript):
```javascript
import { EduPredictAPI } from 'edupredict-js-sdk';

const api = new EduPredictAPI({
  baseURL: 'http://localhost:8000/api/v1',
  token: 'your-jwt-token'
});

const students = await api.students.getAll();
const prediction = await api.analytics.getDropoutPrediction('STU001');
```
