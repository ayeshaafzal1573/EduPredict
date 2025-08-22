# EduPredict - System Diagrams and Flowcharts

## Table of Contents
1. [System Architecture Diagram](#1-system-architecture-diagram)
2. [Data Flow Diagrams](#2-data-flow-diagrams)
3. [Process Flowcharts](#3-process-flowcharts)
4. [Database Schema Diagrams](#4-database-schema-diagrams)
5. [User Journey Flowcharts](#5-user-journey-flowcharts)
6. [Machine Learning Pipeline Diagrams](#6-machine-learning-pipeline-diagrams)

---

## 1. System Architecture Diagram

### 1.1 High-Level Architecture
```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Browser]
        Mobile[Mobile App]
    end
    
    subgraph "Presentation Layer"
        React[React Frontend<br/>TailwindCSS]
        Dashboard[Role-based Dashboards]
    end
    
    subgraph "API Gateway"
        FastAPI[FastAPI Server<br/>Python 3.11]
        Auth[JWT Authentication]
        CORS[CORS Middleware]
    end
    
    subgraph "Business Logic"
        UserSvc[User Service]
        StudentSvc[Student Service]
        CourseSvc[Course Service]
        AnalyticsSvc[Analytics Service]
        NotificationSvc[Notification Service]
    end
    
    subgraph "ML/AI Layer"
        DropoutModel[Dropout Prediction<br/>Random Forest]
        GradeModel[Grade Prediction<br/>Random Forest]
        MLPipeline[ML Training Pipeline]
    end
    
    subgraph "Data Layer"
        MongoDB[(MongoDB<br/>Transactional Data)]
        HDFS[(Hadoop HDFS<br/>Big Data)]
        Redis[(Redis<br/>Cache)]
    end
    
    subgraph "Big Data Processing"
        Impala[Apache Impala<br/>SQL Queries]
        Hadoop[Hadoop Ecosystem]
    end
    
    subgraph "Visualization"
        Tableau[Tableau Dashboards]
        Charts[React Charts]
    end
    
    Web --> React
    Mobile --> React
    React --> FastAPI
    FastAPI --> Auth
    FastAPI --> UserSvc
    FastAPI --> StudentSvc
    FastAPI --> CourseSvc
    FastAPI --> AnalyticsSvc
    FastAPI --> NotificationSvc
    
    AnalyticsSvc --> DropoutModel
    AnalyticsSvc --> GradeModel
    MLPipeline --> DropoutModel
    MLPipeline --> GradeModel
    
    UserSvc --> MongoDB
    StudentSvc --> MongoDB
    CourseSvc --> MongoDB
    AnalyticsSvc --> Redis
    
    AnalyticsSvc --> Impala
    Impala --> HDFS
    Hadoop --> HDFS
    
    Tableau --> MongoDB
    Tableau --> Impala
    Charts --> FastAPI
```

### 1.2 Deployment Architecture
```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end
    
    subgraph "Frontend Servers"
        FE1[React App 1]
        FE2[React App 2]
    end
    
    subgraph "Backend Servers"
        BE1[FastAPI Server 1]
        BE2[FastAPI Server 2]
        BE3[FastAPI Server 3]
    end
    
    subgraph "Database Cluster"
        MongoDB1[(MongoDB Primary)]
        MongoDB2[(MongoDB Secondary)]
        MongoDB3[(MongoDB Arbiter)]
    end
    
    subgraph "Big Data Cluster"
        NameNode[Hadoop NameNode]
        DataNode1[DataNode 1]
        DataNode2[DataNode 2]
        DataNode3[DataNode 3]
    end
    
    subgraph "Cache Layer"
        Redis1[(Redis Master)]
        Redis2[(Redis Slave)]
    end
    
    LB --> FE1
    LB --> FE2
    LB --> BE1
    LB --> BE2
    LB --> BE3
    
    BE1 --> MongoDB1
    BE2 --> MongoDB1
    BE3 --> MongoDB1
    MongoDB1 --> MongoDB2
    MongoDB1 --> MongoDB3
    
    BE1 --> Redis1
    BE2 --> Redis1
    BE3 --> Redis1
    Redis1 --> Redis2
    
    BE1 --> NameNode
    BE2 --> NameNode
    BE3 --> NameNode
    NameNode --> DataNode1
    NameNode --> DataNode2
    NameNode --> DataNode3
```

---

## 2. Data Flow Diagrams

### 2.1 Level 0 - Context Diagram
```mermaid
graph LR
    Student[Student]
    Teacher[Teacher]
    Admin[Administrator]
    Analyst[Data Analyst]
    
    EduPredict[EduPredict System]
    
    ExtDB[(External Data Sources)]
    Email[Email System]
    Tableau[Tableau Server]
    
    Student --> EduPredict
    Teacher --> EduPredict
    Admin --> EduPredict
    Analyst --> EduPredict
    
    EduPredict --> Student
    EduPredict --> Teacher
    EduPredict --> Admin
    EduPredict --> Analyst
    
    ExtDB --> EduPredict
    EduPredict --> Email
    EduPredict --> Tableau
```

### 2.2 Level 1 - System Overview
```mermaid
graph TB
    subgraph "External Entities"
        Users[Users<br/>Students, Teachers, Admins, Analysts]
        ExtSys[External Systems<br/>LMS, SIS, Email]
    end
    
    subgraph "EduPredict System"
        Auth[1.0<br/>Authentication<br/>& Authorization]
        DataMgmt[2.0<br/>Data Management<br/>& Storage]
        Analytics[3.0<br/>Analytics<br/>& Predictions]
        Reporting[4.0<br/>Reporting<br/>& Visualization]
        Notifications[5.0<br/>Notifications<br/>& Alerts]
    end
    
    subgraph "Data Stores"
        UserDB[(D1: User Database)]
        StudentDB[(D2: Student Database)]
        CourseDB[(D3: Course Database)]
        AnalyticsDB[(D4: Analytics Database)]
        BigDataStore[(D5: Big Data Store)]
    end
    
    Users --> Auth
    Auth --> Users
    Auth --> DataMgmt
    DataMgmt --> UserDB
    DataMgmt --> StudentDB
    DataMgmt --> CourseDB
    DataMgmt --> Analytics
    Analytics --> AnalyticsDB
    Analytics --> BigDataStore
    Analytics --> Reporting
    Reporting --> Users
    Analytics --> Notifications
    Notifications --> ExtSys
    Notifications --> Users
```

### 2.3 Level 2 - Detailed Data Flow
```mermaid
graph TB
    subgraph "Data Input"
        StudentData[Student Data Input]
        AttendanceData[Attendance Records]
        GradeData[Grade Information]
        CourseData[Course Details]
    end
    
    subgraph "Data Processing"
        Validation[Data Validation<br/>& Cleaning]
        Transformation[Data Transformation<br/>& Normalization]
        FeatureEng[Feature Engineering<br/>for ML Models]
    end
    
    subgraph "Analytics Engine"
        DropoutPred[Dropout Risk<br/>Prediction]
        GradePred[Grade<br/>Prediction]
        TrendAnalysis[Trend<br/>Analysis]
    end
    
    subgraph "Output Generation"
        Dashboards[Interactive<br/>Dashboards]
        Reports[Automated<br/>Reports]
        Alerts[Risk<br/>Alerts]
    end
    
    StudentData --> Validation
    AttendanceData --> Validation
    GradeData --> Validation
    CourseData --> Validation
    
    Validation --> Transformation
    Transformation --> FeatureEng
    
    FeatureEng --> DropoutPred
    FeatureEng --> GradePred
    FeatureEng --> TrendAnalysis
    
    DropoutPred --> Dashboards
    DropoutPred --> Alerts
    GradePred --> Dashboards
    GradePred --> Reports
    TrendAnalysis --> Dashboards
    TrendAnalysis --> Reports
```

---

## 3. Process Flowcharts

### 3.1 User Authentication Flow
```mermaid
flowchart TD
    Start([User Access System]) --> LoginPage[Display Login Page]
    LoginPage --> EnterCreds[User Enters Credentials]
    EnterCreds --> ValidateCreds{Validate Credentials}
    
    ValidateCreds -->|Invalid| ErrorMsg[Display Error Message]
    ErrorMsg --> LoginPage
    
    ValidateCreds -->|Valid| CheckActive{User Account Active?}
    CheckActive -->|No| DeactivatedMsg[Account Deactivated Message]
    DeactivatedMsg --> LoginPage
    
    CheckActive -->|Yes| GenerateToken[Generate JWT Token]
    GenerateToken --> SetSession[Set User Session]
    SetSession --> CheckRole{Determine User Role}
    
    CheckRole -->|Student| StudentDash[Redirect to Student Dashboard]
    CheckRole -->|Teacher| TeacherDash[Redirect to Teacher Dashboard]
    CheckRole -->|Admin| AdminDash[Redirect to Admin Dashboard]
    CheckRole -->|Analyst| AnalystDash[Redirect to Analyst Dashboard]
    
    StudentDash --> End([User Logged In])
    TeacherDash --> End
    AdminDash --> End
    AnalystDash --> End
```

### 3.2 Dropout Prediction Process
```mermaid
flowchart TD
    Start([Prediction Request]) --> GetStudentID[Extract Student ID]
    GetStudentID --> FetchData[Fetch Student Data from Database]
    FetchData --> CheckData{Data Available?}
    
    CheckData -->|No| NoDataError[Return No Data Error]
    NoDataError --> End([End Process])
    
    CheckData -->|Yes| PrepareFeatures[Prepare Feature Vector]
    PrepareFeatures --> LoadModel[Load Trained ML Model]
    LoadModel --> MakePrediction[Generate Prediction]
    MakePrediction --> CalculateRisk[Calculate Risk Score]
    CalculateRisk --> IdentifyFactors[Identify Risk Factors]
    IdentifyFactors --> GenerateRecommendations[Generate Recommendations]
    GenerateRecommendations --> FormatResponse[Format Response]
    FormatResponse --> CheckRiskLevel{High Risk?}
    
    CheckRiskLevel -->|Yes| TriggerAlert[Trigger Alert Notification]
    CheckRiskLevel -->|No| LogPrediction[Log Prediction]
    
    TriggerAlert --> LogPrediction
    LogPrediction --> ReturnResult[Return Prediction Result]
    ReturnResult --> End
```

### 3.3 Grade Entry and Processing Flow
```mermaid
flowchart TD
    Start([Teacher Enters Grade]) --> ValidateInput{Validate Input Data}
    
    ValidateInput -->|Invalid| ValidationError[Display Validation Error]
    ValidationError --> Start
    
    ValidateInput -->|Valid| CheckPermissions{Teacher Has Permission?}
    CheckPermissions -->|No| PermissionError[Display Permission Error]
    PermissionError --> End([End Process])
    
    CheckPermissions -->|Yes| SaveGrade[Save Grade to Database]
    SaveGrade --> UpdateGPA[Recalculate Student GPA]
    UpdateGPA --> UpdateCredits[Update Credit Hours]
    UpdateCredits --> TriggerAnalytics[Trigger Analytics Update]
    TriggerAnalytics --> CheckGradeThreshold{Grade Below Threshold?}
    
    CheckGradeThreshold -->|Yes| GenerateAlert[Generate Low Grade Alert]
    CheckGradeThreshold -->|No| LogActivity[Log Activity]
    
    GenerateAlert --> NotifyStudent[Notify Student]
    NotifyStudent --> NotifyAdvisor[Notify Academic Advisor]
    NotifyAdvisor --> LogActivity
    
    LogActivity --> UpdateDashboard[Update Dashboard Metrics]
    UpdateDashboard --> Success[Display Success Message]
    Success --> End
```

### 3.4 Data Processing Pipeline Flow
```mermaid
flowchart TD
    Start([Data Ingestion]) --> DataSource{Data Source Type}
    
    DataSource -->|Real-time| StreamProcessor[Stream Processing]
    DataSource -->|Batch| BatchProcessor[Batch Processing]
    
    StreamProcessor --> ValidateStream[Validate Stream Data]
    BatchProcessor --> ValidateBatch[Validate Batch Data]
    
    ValidateStream --> TransformStream[Transform Stream Data]
    ValidateBatch --> TransformBatch[Transform Batch Data]
    
    TransformStream --> MergeData[Merge with Existing Data]
    TransformBatch --> MergeData
    
    MergeData --> QualityCheck{Data Quality Check}
    QualityCheck -->|Fail| DataCleanup[Data Cleanup & Correction]
    DataCleanup --> QualityCheck
    
    QualityCheck -->|Pass| StoreData[Store in Database]
    StoreData --> IndexData[Update Search Indexes]
    IndexData --> TriggerML[Trigger ML Pipeline]
    TriggerML --> UpdateCache[Update Cache]
    UpdateCache --> NotifyServices[Notify Dependent Services]
    NotifyServices --> End([Data Processing Complete])
```
