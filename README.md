# EduPredict - AI-Powered Student Performance & Dropout Prediction System

## 🎯 Overview
EduPredict is a comprehensive academic performance prediction system that leverages machine learning to predict student dropout risk and academic performance. The system integrates multiple technologies including Python, Hadoop, Impala, MongoDB, Tableau, and React to provide real-time insights for educational institutions.

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python FastAPI
- **Frontend**: React + TailwindCSS
- **Databases**: MongoDB Atlas (transactional), Hadoop HDFS (big data)
- **Analytics**: Impala (big data queries), Tableau (visualization)
- **ML**: scikit-learn, pandas, numpy
- **Authentication**: JWT with role-based access

### System Components
1. **Authentication Service** - JWT-based auth with roles (Student, Teacher, Admin, Analyst)
2. **Data Management** - MongoDB for real-time data, HDFS for historical logs
3. **Analytics Engine** - ML models for dropout prediction and grade forecasting
4. **Notification System** - Email and in-app alerts
5. **Visualization** - Tableau dashboards and React charts

## 📁 Project Structure
```
EduPredict/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core configurations
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   ├── ml/                # Machine learning models
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── utils/             # Utility functions
│   │   └── styles/            # CSS/Tailwind styles
│   └── package.json           # Node dependencies
├── data/                      # Data files and scripts
│   ├── sample_data/           # Sample datasets
│   ├── hadoop_scripts/        # Hadoop/HDFS scripts
│   └── impala_queries/        # Impala SQL queries
├── tableau/                   # Tableau workbooks and configs
├── docker/                    # Docker configurations
├── docs/                      # Documentation
└── scripts/                   # Setup and deployment scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB Atlas account
- Hadoop cluster (or local setup)
- Impala server
- Tableau Desktop/Server

### Installation
1. Clone the repository
2. Setup backend: `cd backend && pip install -r requirements.txt`
3. Setup frontend: `cd frontend && npm install`
4. Configure environment variables
5. Run the application

## 👥 User Roles
- **Student**: View grades, attendance, performance predictions
- **Teacher**: Mark attendance, update grades, view student risk alerts
- **Admin**: Manage users, system configuration, overall analytics
- **Analyst**: Advanced analytics, Tableau dashboards, ML model management

## 📊 Features
- Real-time student performance tracking
- Dropout risk prediction using ML
- Grade forecasting
- Attendance management
- Role-based dashboards
- Email and in-app notifications
- Tableau integration for advanced analytics
- Big data processing with Hadoop/Impala

## 🔧 Development
See `/docs` folder for detailed setup instructions, API documentation, and development guidelines.

## 📈 Analytics
The system provides:
- Predictive analytics for student outcomes
- Performance trend analysis
- Risk factor identification
- Intervention recommendations
"# EduPredict" 
