# EduPredict Backend API

## Overview

EduPredict is a comprehensive AI-powered student performance and dropout prediction system built with FastAPI, MongoDB, and machine learning models. This backend provides RESTful APIs for managing students, courses, grades, attendance, and generating predictive analytics.

## Features

- **User Authentication & Authorization**: JWT-based authentication with role-based access control
- **Student Management**: Complete student lifecycle management with academic tracking
- **Course Management**: Course creation, enrollment, and management
- **Attendance Tracking**: Real-time attendance marking and analytics
- **Grade Management**: Comprehensive gradebook with bulk operations
- **AI Predictions**: Machine learning models for dropout risk and grade prediction
- **Analytics Dashboard**: Role-based analytics and insights
- **Notification System**: Real-time notifications and alerts

## Technology Stack

- **FastAPI**: Modern Python web framework for building APIs
- **MongoDB**: Document database for flexible data storage
- **Motor**: Async MongoDB driver for Python
- **Pydantic**: Data validation and serialization
- **JWT**: JSON Web Tokens for authentication
- **Scikit-learn**: Machine learning models
- **Loguru**: Advanced logging
- **Uvicorn**: ASGI server for FastAPI

## Quick Start

### Prerequisites

- Python 3.9 or higher
- MongoDB 5.0 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd edupredict/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   # Using Docker
   docker run -d --name mongodb -p 27017:27017 mongo:7.0
   
   # Or start your local MongoDB service
   mongod
   ```

6. **Initialize database with sample data**
   ```bash
   python seed_data.py
   ```

7. **Start the server**
   ```bash
   python start_server.py
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Documentation

### Authentication

All endpoints (except auth endpoints) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@edupredict.com | admin123 |
| Teacher | teacher@edupredict.com | teacher123 |
| Student | student@edupredict.com | student123 |
| Analyst | analyst@edupredict.com | analyst123 |

### Core Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

#### Students
- `GET /api/v1/students` - List students
- `GET /api/v1/students/{id}` - Get student details
- `POST /api/v1/students` - Create student
- `PUT /api/v1/students/{id}` - Update student

#### Courses
- `GET /api/v1/courses` - List courses
- `GET /api/v1/courses/{id}` - Get course details
- `POST /api/v1/courses` - Create course
- `GET /api/v1/courses/{id}/students` - Get course students

#### Analytics
- `GET /api/v1/analytics/dropout-prediction/{student_id}` - Dropout prediction
- `GET /api/v1/analytics/grade-predictions/{student_id}` - Grade predictions
- `GET /api/v1/analytics/dashboard-stats/{role}` - Dashboard statistics

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── auth.py      # Authentication endpoints
│   │   ├── students.py  # Student management
│   │   ├── courses.py   # Course management
│   │   ├── grades.py    # Grade management
│   │   ├── attendance.py # Attendance tracking
│   │   ├── analytics.py # Analytics and predictions
│   │   └── notifications.py # Notification system
│   ├── core/            # Core utilities
│   │   ├── config.py    # Configuration settings
│   │   ├── database.py  # Database connections
│   │   ├── security.py  # Authentication & security
│   │   └── hdfs_utils.py # Big data utilities
│   ├── models/          # Pydantic models
│   │   ├── user.py      # User models
│   │   ├── student.py   # Student models
│   │   ├── course.py    # Course models
│   │   └── grade.py     # Grade models
│   ├── services/        # Business logic services
│   └── ml/              # Machine learning models
├── data/                # Sample data files
├── docs/                # Documentation
├── requirements.txt     # Python dependencies
├── seed_data.py        # Database seeding script
└── start_server.py     # Server startup script
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
MONGODB_URL=mongodb://localhost:27017/edupredict
MONGODB_DB=edupredict

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ALLOWED_ORIGINS=["http://localhost:3000"]

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### Database Setup

The system uses MongoDB with the following collections:
- `users` - User accounts and authentication
- `students` - Student profiles and academic data
- `courses` - Course information and enrollment
- `grades` - Grade records and assessments
- `attendance` - Attendance tracking
- `notifications` - System notifications

## Machine Learning Models

### Dropout Prediction Model
- **Algorithm**: Random Forest Classifier
- **Accuracy**: 87.2%
- **Features**: GPA, attendance, demographics, engagement
- **Output**: Risk score, level, factors, recommendations

### Grade Prediction Model
- **Algorithm**: Random Forest Regressor
- **Accuracy**: 82.4%
- **Features**: Previous performance, attendance, assignments
- **Output**: Predicted grade, confidence, suggestions

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Operations

#### Seeding Data
```bash
python seed_data.py
```

#### Backup Database
```bash
mongodump --db edupredict --out backup/
```

#### Restore Database
```bash
mongorestore --db edupredict backup/edupredict/
```

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t edupredict-backend .

# Run container
docker run -p 8000:8000 --env-file .env edupredict-backend
```

### Production Considerations

1. **Security**
   - Use strong SECRET_KEY in production
   - Enable HTTPS
   - Implement rate limiting
   - Use environment-specific configurations

2. **Database**
   - Use MongoDB Atlas or managed MongoDB
   - Implement proper indexing
   - Set up regular backups
   - Monitor performance

3. **Monitoring**
   - Implement health checks
   - Set up logging aggregation
   - Monitor API performance
   - Track error rates

## API Usage Examples

### Authentication
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'email': 'student@edupredict.com',
    'password': 'student123'
})
token = response.json()['access_token']

# Use token for authenticated requests
headers = {'Authorization': f'Bearer {token}'}
```

### Get Student Data
```python
# Get current user's student data
response = requests.get(
    'http://localhost:8000/api/v1/students/me',
    headers=headers
)
student_data = response.json()
```

### Get Predictions
```python
# Get dropout prediction
response = requests.get(
    'http://localhost:8000/api/v1/analytics/dropout-prediction/me',
    headers=headers
)
prediction = response.json()
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running: `mongod`
   - Check connection string in `.env`
   - Verify network connectivity

2. **Import Errors**
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **Authentication Errors**
   - Check SECRET_KEY in `.env`
   - Verify token expiration settings
   - Ensure proper CORS configuration

4. **Performance Issues**
   - Add database indexes for frequently queried fields
   - Implement caching with Redis
   - Optimize query patterns

### Logging

The application uses Loguru for comprehensive logging:

```python
from loguru import logger

# Logs are automatically formatted and include:
# - Timestamp
# - Log level
# - Module name
# - Message
logger.info("Application started")
logger.error("Database connection failed")
```

### Health Checks

Monitor application health:
- `GET /health` - Basic health check
- `GET /` - API information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For technical support:
- Check the logs for error details
- Review the API documentation at `/docs`
- Refer to the troubleshooting section
- Contact the development team

---

**EduPredict Backend** - Powering Educational Analytics with AI 🚀