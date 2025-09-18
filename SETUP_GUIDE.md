# EduPredict Setup Guide

## Quick Start (Recommended)

### Prerequisites
- Python 3.11+
- Node.js 16+
- MongoDB (local or cloud)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env if needed (default values work for local development)

# Seed the database with sample data
python seed_data.py

# Start the backend server
python start_server.py
```

The backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at: http://localhost:3000

### 3. Login Credentials

Use these demo accounts to explore different user roles:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@edupredict.com | admin123 |
| **Teacher** | teacher@edupredict.com | teacher123 |
| **Student** | student@edupredict.com | student123 |
| **Analyst** | analyst@edupredict.com | analyst123 |

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Start all services with Docker Compose
cd backend
docker-compose up -d

# Initialize database
docker-compose exec backend python seed_data.py

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## Features Overview

### 🎓 Student Features
- View academic performance and GPA trends
- Check attendance records across all courses
- AI-powered dropout risk assessment
- Grade predictions for current courses
- Personalized recommendations

### 👨‍🏫 Teacher Features
- Manage multiple classes and student rosters
- Mark attendance efficiently
- Enter and manage grades
- Identify at-risk students with AI insights
- Generate class performance analytics

### 👨‍💼 Admin Features
- Oversee institution-wide metrics
- Manage users, courses, and system settings
- Access comprehensive reporting tools
- Monitor system health and usage

### 📊 Analyst Features
- Advanced ML model management
- Generate custom analytics reports
- Access Tableau dashboard integration
- Perform deep-dive data analysis

## System Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ MongoDB
                                    ↓
                            AI/ML Models
                                    ↓
                         Analytics & Predictions
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running on localhost:27017
   - Check if the database name is correct in .env

2. **Frontend API Connection Error**
   - Verify backend is running on port 8000
   - Check REACT_APP_API_URL in frontend/.env

3. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

4. **Port Already in Use**
   - Change PORT in backend/.env
   - Update REACT_APP_API_URL accordingly

### Performance Tips

- Use MongoDB indexes for better query performance
- Enable Redis for caching (optional)
- Use Docker for consistent environments
- Monitor API response times in browser dev tools

## Next Steps

1. **Explore the System**: Login with different roles to see various features
2. **Add Your Data**: Use the data upload feature to import your own datasets
3. **Customize**: Modify the code to fit your specific requirements
4. **Deploy**: Use the Docker setup for production deployment

## Support

For technical support:
- Check the logs in terminal for error details
- Review the API documentation at http://localhost:8000/docs
- Refer to the comprehensive documentation in the `docs/` directory

---

**EduPredict** - Transforming Education with AI and Big Data Analytics 🚀