# EduPredict Testing Guide

## Overview

This comprehensive testing guide covers all aspects of testing the EduPredict system, including unit tests, integration tests, API testing, and end-to-end testing.

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [API Testing](#api-testing)
5. [Integration Testing](#integration-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Test Data Management](#test-data-management)

## Testing Strategy

### Testing Pyramid

```
    /\
   /  \     E2E Tests (Few)
  /____\    
 /      \   Integration Tests (Some)
/________\  Unit Tests (Many)
```

### Test Types

- **Unit Tests**: Individual functions and components
- **Integration Tests**: API endpoints and database operations
- **End-to-End Tests**: Complete user workflows
- **Performance Tests**: Load and stress testing
- **Security Tests**: Authentication and authorization

## Backend Testing

### Setup Test Environment

1. **Install Test Dependencies**
   ```bash
   cd backend
   pip install pytest pytest-asyncio pytest-cov httpx
   ```

2. **Test Configuration**
   ```python
   # tests/conftest.py
   import pytest
   import asyncio
   from httpx import AsyncClient
   from app.main import app
   from app.core.database import connect_to_mongo, close_mongo_connection
   
   @pytest.fixture(scope="session")
   def event_loop():
       loop = asyncio.get_event_loop_policy().new_event_loop()
       yield loop
       loop.close()
   
   @pytest.fixture(scope="session")
   async def test_app():
       await connect_to_mongo()
       yield app
       await close_mongo_connection()
   
   @pytest.fixture
   async def client(test_app):
       async with AsyncClient(app=test_app, base_url="http://test") as ac:
           yield ac
   ```

### Unit Tests

1. **Authentication Tests**
   ```python
   # tests/test_auth.py
   import pytest
   from app.core.security import verify_password, get_password_hash, create_access_token
   
   def test_password_hashing():
       password = "testpassword123"
       hashed = get_password_hash(password)
       assert verify_password(password, hashed)
       assert not verify_password("wrongpassword", hashed)
   
   def test_token_creation():
       data = {"sub": "user123", "email": "test@example.com"}
       token = create_access_token(data)
       assert isinstance(token, str)
       assert len(token) > 0
   ```

2. **Model Validation Tests**
   ```python
   # tests/test_models.py
   import pytest
   from pydantic import ValidationError
   from app.models.user import UserCreate
   from app.models.student import StudentCreate
   
   def test_user_model_validation():
       # Valid user
       user = UserCreate(
           email="test@example.com",
           password="password123",
           first_name="Test",
           last_name="User",
           role="student"
       )
       assert user.email == "test@example.com"
   
       # Invalid email
       with pytest.raises(ValidationError):
           UserCreate(
               email="invalid-email",
               password="password123",
               first_name="Test",
               last_name="User",
               role="student"
           )
   ```

3. **ML Model Tests**
   ```python
   # tests/test_ml_models.py
   import pytest
   from app.ml.dropout_predictor import DropoutPredictor
   
   def test_dropout_prediction():
       predictor = DropoutPredictor()
       
       # High-risk student
       high_risk_data = {
           'gpa': 1.8,
           'attendance_rate': 0.55,
           'total_credits': 40,
           'current_semester': 3
       }
       
       prediction = predictor.predict_dropout_risk(high_risk_data)
       assert prediction['risk_level'] in ['low', 'medium', 'high']
       assert 0 <= prediction['dropout_risk_score'] <= 1
   ```

### Integration Tests

1. **API Endpoint Tests**
   ```python
   # tests/test_api.py
   import pytest
   from httpx import AsyncClient
   
   @pytest.mark.asyncio
   async def test_login_endpoint(client: AsyncClient):
       response = await client.post("/api/v1/auth/login", json={
           "email": "student@edupredict.com",
           "password": "student123"
       })
       assert response.status_code == 200
       data = response.json()
       assert "access_token" in data
       assert data["token_type"] == "bearer"
   
   @pytest.mark.asyncio
   async def test_protected_endpoint(client: AsyncClient):
       # Login first
       login_response = await client.post("/api/v1/auth/login", json={
           "email": "student@edupredict.com",
           "password": "student123"
       })
       token = login_response.json()["access_token"]
       
       # Access protected endpoint
       headers = {"Authorization": f"Bearer {token}"}
       response = await client.get("/api/v1/auth/me", headers=headers)
       assert response.status_code == 200
   ```

2. **Database Tests**
   ```python
   # tests/test_database.py
   import pytest
   from app.core.database import get_users_collection
   from app.models.user import UserCreate
   
   @pytest.mark.asyncio
   async def test_user_crud():
       collection = await get_users_collection()
       
       # Create user
       user_data = {
           "email": "test@example.com",
           "first_name": "Test",
           "last_name": "User",
           "role": "student",
           "hashed_password": "hashed_password"
       }
       
       result = await collection.insert_one(user_data)
       assert result.inserted_id
       
       # Read user
       user = await collection.find_one({"_id": result.inserted_id})
       assert user["email"] == "test@example.com"
       
       # Update user
       await collection.update_one(
           {"_id": result.inserted_id},
           {"$set": {"first_name": "Updated"}}
       )
       
       updated_user = await collection.find_one({"_id": result.inserted_id})
       assert updated_user["first_name"] == "Updated"
       
       # Delete user
       await collection.delete_one({"_id": result.inserted_id})
   ```

### Running Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

## Frontend Testing

### Setup Test Environment

1. **Install Test Dependencies**
   ```bash
   cd frontend
   npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
   ```

### Component Tests

1. **Authentication Tests**
   ```javascript
   // src/components/__tests__/Login.test.js
   import React from 'react';
   import { render, screen, fireEvent, waitFor } from '@testing-library/react';
   import { BrowserRouter } from 'react-router-dom';
   import Login from '../Auth/Login';
   import { AuthProvider } from '../../contexts/AuthContext';
   
   const renderLogin = () => {
     return render(
       <BrowserRouter>
         <AuthProvider>
           <Login />
         </AuthProvider>
       </BrowserRouter>
     );
   };
   
   test('renders login form', () => {
     renderLogin();
     expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
     expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
     expect(screen.getByText('Sign in to EduPredict')).toBeInTheDocument();
   });
   
   test('validates required fields', async () => {
     renderLogin();
     
     const submitButton = screen.getByText('Sign in to EduPredict');
     fireEvent.click(submitButton);
     
     await waitFor(() => {
       expect(screen.getByText('Email is required')).toBeInTheDocument();
     });
   });
   ```

2. **Dashboard Tests**
   ```javascript
   // src/components/__tests__/StudentDashboard.test.js
   import React from 'react';
   import { render, screen, waitFor } from '@testing-library/react';
   import StudentDashboard from '../Student/Dashboard';
   import { AuthProvider } from '../../contexts/AuthContext';
   
   // Mock API calls
   jest.mock('../../services/api', () => ({
     analyticsAPI: {
       getDashboardStats: jest.fn(() => Promise.resolve({
         current_gpa: 3.2,
         attendance_rate: 87,
         risk_level: 'low'
       }))
     }
   }));
   
   test('displays student dashboard data', async () => {
     render(
       <AuthProvider>
         <StudentDashboard />
       </AuthProvider>
     );
   
     await waitFor(() => {
       expect(screen.getByText('3.2')).toBeInTheDocument();
       expect(screen.getByText('87%')).toBeInTheDocument();
     });
   });
   ```

### Context Tests

1. **AuthContext Tests**
   ```javascript
   // src/contexts/__tests__/AuthContext.test.js
   import React from 'react';
   import { renderHook, act } from '@testing-library/react';
   import { AuthProvider, useAuth } from '../AuthContext';
   
   const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;
   
   test('provides authentication state', () => {
     const { result } = renderHook(() => useAuth(), { wrapper });
     
     expect(result.current.user).toBeNull();
     expect(result.current.isAuthenticated).toBe(false);
     expect(typeof result.current.login).toBe('function');
     expect(typeof result.current.logout).toBe('function');
   });
   ```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test Login.test.js
```

## API Testing

### Postman Collection

1. **Create Postman Collection**
   ```json
   {
     "info": {
       "name": "EduPredict API",
       "description": "Complete API testing collection"
     },
     "auth": {
       "type": "bearer",
       "bearer": [
         {
           "key": "token",
           "value": "{{access_token}}",
           "type": "string"
         }
       ]
     },
     "event": [
       {
         "listen": "prerequest",
         "script": {
           "exec": [
             "// Auto-login if no token",
             "if (!pm.globals.get('access_token')) {",
             "  pm.sendRequest({",
             "    url: pm.environment.get('base_url') + '/auth/login',",
             "    method: 'POST',",
             "    header: {'Content-Type': 'application/json'},",
             "    body: {",
             "      mode: 'raw',",
             "      raw: JSON.stringify({",
             "        email: 'admin@edupredict.com',",
             "        password: 'admin123'",
             "      })",
             "    }",
             "  }, (err, res) => {",
             "    if (!err) {",
             "      pm.globals.set('access_token', res.json().access_token);",
             "    }",
             "  });",
             "}"
           ]
         }
       }
     ]
   }
   ```

### Automated API Tests

1. **Newman (Postman CLI)**
   ```bash
   # Install Newman
   npm install -g newman
   
   # Run collection
   newman run edupredict-api-tests.json -e environment.json
   ```

2. **Python API Tests**
   ```python
   # tests/test_api_integration.py
   import pytest
   import requests
   
   BASE_URL = "http://localhost:8000/api/v1"
   
   @pytest.fixture
   def auth_headers():
       response = requests.post(f"{BASE_URL}/auth/login", json={
           "email": "admin@edupredict.com",
           "password": "admin123"
       })
       token = response.json()["access_token"]
       return {"Authorization": f"Bearer {token}"}
   
   def test_get_students(auth_headers):
       response = requests.get(f"{BASE_URL}/students", headers=auth_headers)
       assert response.status_code == 200
       data = response.json()
       assert isinstance(data, list)
   
   def test_create_student(auth_headers):
       student_data = {
           "student_id": "TEST001",
           "user_id": "test_user_id",
           "first_name": "Test",
           "last_name": "Student",
           "email": "test.student@example.com",
           "department": "Computer Science",
           "program": "Bachelor of Science"
       }
       
       response = requests.post(
           f"{BASE_URL}/students", 
           json=student_data, 
           headers=auth_headers
       )
       assert response.status_code == 201
   ```

## Integration Testing

### Database Integration Tests

1. **MongoDB Integration**
   ```python
   # tests/test_database_integration.py
   import pytest
   from app.core.database import connect_to_mongo, get_users_collection
   
   @pytest.mark.asyncio
   async def test_database_connection():
       connected = await connect_to_mongo()
       assert connected == True
   
   @pytest.mark.asyncio
   async def test_collection_operations():
       collection = await get_users_collection()
       
       # Test insert
       doc = {"test": "data", "timestamp": "2024-01-01"}
       result = await collection.insert_one(doc)
       assert result.inserted_id
       
       # Test find
       found_doc = await collection.find_one({"_id": result.inserted_id})
       assert found_doc["test"] == "data"
       
       # Cleanup
       await collection.delete_one({"_id": result.inserted_id})
   ```

### Service Integration Tests

1. **Student Service Tests**
   ```python
   # tests/test_student_service.py
   import pytest
   from app.services.student_service import StudentService
   from app.models.student import StudentCreate
   
   @pytest.mark.asyncio
   async def test_student_service():
       service = StudentService()
       
       # Test create student
       student_data = StudentCreate(
           student_id="TEST001",
           user_id="test_user_id",
           first_name="Test",
           last_name="Student",
           department="Computer Science",
           program="Bachelor of Science"
       )
       
       created_student = await service.create_student(student_data)
       assert created_student.student_id == "TEST001"
       
       # Test get student
       retrieved_student = await service.get_student("TEST001")
       assert retrieved_student.student_id == "TEST001"
       
       # Cleanup
       await service.delete_student("TEST001")
   ```

## Performance Testing

### Load Testing with Locust

1. **Install Locust**
   ```bash
   pip install locust
   ```

2. **Load Test Script**
   ```python
   # tests/load_test.py
   from locust import HttpUser, task, between
   import json
   
   class EduPredictUser(HttpUser):
       wait_time = between(1, 3)
       
       def on_start(self):
           # Login and get token
           response = self.client.post("/api/v1/auth/login", json={
               "email": "student@edupredict.com",
               "password": "student123"
           })
           
           if response.status_code == 200:
               self.token = response.json()["access_token"]
               self.headers = {"Authorization": f"Bearer {self.token}"}
           else:
               self.token = None
               self.headers = {}
       
       @task(3)
       def view_dashboard(self):
           if self.token:
               self.client.get("/api/v1/analytics/dashboard-stats/student", 
                             headers=self.headers)
       
       @task(2)
       def view_grades(self):
           if self.token:
               self.client.get("/api/v1/grades?student_id=me", 
                             headers=self.headers)
       
       @task(1)
       def view_predictions(self):
           if self.token:
               self.client.get("/api/v1/analytics/dropout-prediction/me", 
                             headers=self.headers)
   ```

3. **Run Load Tests**
   ```bash
   # Start load test
   locust -f tests/load_test.py --host=http://localhost:8000
   
   # Command line load test
   locust -f tests/load_test.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 5m --headless
   ```

### Performance Benchmarks

1. **Response Time Targets**
   - Authentication: < 500ms
   - Dashboard data: < 2s
   - Analytics queries: < 5s
   - ML predictions: < 3s

2. **Throughput Targets**
   - Concurrent users: 100+
   - Requests per second: 50+
   - Database queries: 1000+ per minute

## Security Testing

### Authentication Tests

1. **JWT Security Tests**
   ```python
   # tests/test_security.py
   import pytest
   from app.core.security import create_access_token, get_current_user
   from jose import jwt
   
   def test_token_expiration():
       from datetime import datetime, timedelta
       
       # Create expired token
       expired_data = {
           "sub": "user123",
           "exp": datetime.utcnow() - timedelta(minutes=1)
       }
       
       expired_token = jwt.encode(expired_data, "secret", algorithm="HS256")
       
       # Test that expired token is rejected
       with pytest.raises(Exception):
           # This should fail
           pass
   
   def test_invalid_token():
       invalid_token = "invalid.token.here"
       
       with pytest.raises(Exception):
           # This should fail
           pass
   ```

2. **Authorization Tests**
   ```python
   # tests/test_authorization.py
   import pytest
   from httpx import AsyncClient
   
   @pytest.mark.asyncio
   async def test_role_based_access(client: AsyncClient):
       # Login as student
       student_response = await client.post("/api/v1/auth/login", json={
           "email": "student@edupredict.com",
           "password": "student123"
       })
       student_token = student_response.json()["access_token"]
       student_headers = {"Authorization": f"Bearer {student_token}"}
       
       # Try to access admin endpoint (should fail)
       admin_response = await client.get("/api/v1/users", headers=student_headers)
       assert admin_response.status_code == 403
   ```

### Input Validation Tests

1. **SQL Injection Prevention**
   ```python
   # tests/test_input_validation.py
   import pytest
   from httpx import AsyncClient
   
   @pytest.mark.asyncio
   async def test_sql_injection_prevention(client: AsyncClient, auth_headers):
       # Test malicious input
       malicious_input = "'; DROP TABLE users; --"
       
       response = await client.get(
           f"/api/v1/students?search={malicious_input}",
           headers=auth_headers
       )
       
       # Should not cause server error
       assert response.status_code in [200, 400, 422]
   ```

## Test Data Management

### Test Database Setup

1. **Separate Test Database**
   ```python
   # tests/conftest.py
   import os
   
   @pytest.fixture(scope="session", autouse=True)
   def setup_test_environment():
       # Use test database
       os.environ["MONGODB_DB"] = "edupredict_test"
       yield
       # Cleanup after tests
   ```

2. **Test Data Fixtures**
   ```python
   # tests/fixtures.py
   import pytest
   from app.core.database import get_users_collection, get_students_collection
   
   @pytest.fixture
   async def sample_user():
       collection = await get_users_collection()
       user_data = {
           "email": "test@example.com",
           "first_name": "Test",
           "last_name": "User",
           "role": "student",
           "hashed_password": "hashed_password",
           "is_active": True
       }
       
       result = await collection.insert_one(user_data)
       user_data["_id"] = result.inserted_id
       
       yield user_data
       
       # Cleanup
       await collection.delete_one({"_id": result.inserted_id})
   ```

### Data Seeding for Tests

1. **Test Data Seeder**
   ```python
   # tests/seed_test_data.py
   import asyncio
   from app.core.database import connect_to_mongo, get_users_collection
   from app.core.security import get_password_hash
   
   async def seed_test_data():
       await connect_to_mongo()
       collection = await get_users_collection()
       
       # Clear existing test data
       await collection.delete_many({"email": {"$regex": "test.*"}})
       
       # Insert test users
       test_users = [
           {
               "email": "test.student@example.com",
               "first_name": "Test",
               "last_name": "Student",
               "role": "student",
               "hashed_password": get_password_hash("password123"),
               "is_active": True
           },
           {
               "email": "test.teacher@example.com",
               "first_name": "Test",
               "last_name": "Teacher",
               "role": "teacher",
               "hashed_password": get_password_hash("password123"),
               "is_active": True
           }
       ]
       
       await collection.insert_many(test_users)
       print("Test data seeded successfully")
   
   if __name__ == "__main__":
       asyncio.run(seed_test_data())
   ```

## Continuous Integration

### GitHub Actions Workflow

1. **CI/CD Pipeline**
   ```yaml
   # .github/workflows/test.yml
   name: Test Suite
   
   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main ]
   
   jobs:
     backend-tests:
       runs-on: ubuntu-latest
       
       services:
         mongodb:
           image: mongo:7.0
           ports:
             - 27017:27017
       
       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.9'
       
       - name: Install dependencies
         run: |
           cd backend
           pip install -r requirements.txt
           pip install pytest pytest-asyncio pytest-cov
       
       - name: Run tests
         run: |
           cd backend
           pytest --cov=app --cov-report=xml
       
       - name: Upload coverage
         uses: codecov/codecov-action@v3
         with:
           file: ./backend/coverage.xml
   
     frontend-tests:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Node.js
         uses: actions/setup-node@v3
         with:
           node-version: '16'
           cache: 'npm'
           cache-dependency-path: frontend/package-lock.json
       
       - name: Install dependencies
         run: |
           cd frontend
           npm ci
       
       - name: Run tests
         run: |
           cd frontend
           npm test -- --coverage --watchAll=false
       
       - name: Build application
         run: |
           cd frontend
           npm run build
   ```

## Test Reporting

### Coverage Reports

1. **Backend Coverage**
   ```bash
   # Generate HTML coverage report
   pytest --cov=app --cov-report=html
   
   # View report
   open htmlcov/index.html
   ```

2. **Frontend Coverage**
   ```bash
   # Generate coverage report
   npm test -- --coverage --watchAll=false
   
   # View report
   open coverage/lcov-report/index.html
   ```

### Test Metrics

Track these key metrics:
- **Code Coverage**: Aim for 80%+ coverage
- **Test Pass Rate**: Maintain 100% pass rate
- **Test Execution Time**: Keep under 5 minutes
- **Flaky Test Rate**: Keep under 1%

## Best Practices

### Test Writing Guidelines

1. **Test Naming**
   ```python
   # Good test names
   def test_user_login_with_valid_credentials_returns_token():
       pass
   
   def test_student_creation_with_invalid_email_raises_validation_error():
       pass
   ```

2. **Test Structure (AAA Pattern)**
   ```python
   def test_example():
       # Arrange
       user_data = {"email": "test@example.com"}
       
       # Act
       result = create_user(user_data)
       
       # Assert
       assert result.email == "test@example.com"
   ```

3. **Test Independence**
   - Each test should be independent
   - Use fixtures for setup/teardown
   - Don't rely on test execution order

### Mock Guidelines

1. **External Dependencies**
   ```python
   # Mock external APIs
   @pytest.fixture
   def mock_external_api(monkeypatch):
       def mock_api_call(*args, **kwargs):
           return {"status": "success"}
       
       monkeypatch.setattr("app.services.external_api.call", mock_api_call)
   ```

2. **Database Mocking**
   ```python
   # Mock database for unit tests
   @pytest.fixture
   def mock_database(monkeypatch):
       async def mock_find_one(*args, **kwargs):
           return {"_id": "test_id", "email": "test@example.com"}
       
       monkeypatch.setattr("app.core.database.collection.find_one", mock_find_one)
   ```

## Troubleshooting Tests

### Common Test Issues

1. **Async Test Failures**
   ```python
   # Ensure proper async handling
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

2. **Database Test Cleanup**
   ```python
   # Always cleanup test data
   @pytest.fixture
   async def cleanup_test_data():
       yield
       # Cleanup after test
       await collection.delete_many({"email": {"$regex": "test.*"}})
   ```

3. **Frontend Test Debugging**
   ```javascript
   // Debug failing tests
   import { screen } from '@testing-library/react';
   
   test('debug test', () => {
     render(<Component />);
     screen.debug(); // Prints DOM structure
   });
   ```

## Test Automation

### Pre-commit Hooks

1. **Setup Pre-commit**
   ```bash
   pip install pre-commit
   
   # .pre-commit-config.yaml
   repos:
   - repo: local
     hooks:
     - id: pytest
       name: pytest
       entry: pytest
       language: python
       pass_filenames: false
       always_run: true
   ```

### Test Scheduling

1. **Automated Test Runs**
   ```bash
   # Cron job for nightly tests
   0 2 * * * cd /path/to/edupredict && ./run_full_test_suite.sh
   ```

---

**EduPredict Testing** - Ensuring Quality and Reliability 🧪