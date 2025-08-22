# EduPredict Installation Guide

This guide will help you set up the EduPredict system on your local machine or server.

## Prerequisites

### Required Software
- **Python 3.9+** - Backend development
- **Node.js 16+** - Frontend development
- **Docker & Docker Compose** - Containerization (recommended)
- **MongoDB** - Primary database
- **Redis** - Caching and background tasks

### Optional (for full big data features)
- **Hadoop 3.x** - Distributed storage (HDFS)
- **Apache Impala** - Big data queries
- **Tableau Desktop/Server** - Advanced visualization

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest way to get started with all services.

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EduPredict
   ```

2. **Create environment file**
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` with your configuration:
   ```env
   SECRET_KEY=your-super-secret-key-here
   MONGODB_URL=mongodb://admin:password123@mongodb:27017/edupredict?authSource=admin
   REDIS_URL=redis://redis:6379
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec backend python scripts/setup.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Method 2: Manual Installation

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
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
   # Edit .env file with your configuration
   ```

5. **Start MongoDB and Redis**
   ```bash
   # Using Docker
   docker run -d --name mongodb -p 27017:27017 mongo:7.0
   docker run -d --name redis -p 6379:6379 redis:7.2-alpine
   ```

6. **Initialize database**
   ```bash
   python scripts/setup.py
   ```

7. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

### Method 3: Production Deployment

#### Using Docker Compose for Production

1. **Create production environment file**
   ```bash
   cp backend/.env.example backend/.env.production
   ```
   
   Configure production settings:
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   MONGODB_URL=mongodb://username:password@your-mongodb-host:27017/edupredict
   ALLOWED_HOSTS=["https://yourdomain.com"]
   ```

2. **Use production Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### Manual Production Setup

1. **Set up reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Set up SSL certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

## Big Data Components Setup (Optional)

### Hadoop/HDFS Setup

1. **Download and install Hadoop**
   ```bash
   wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
   tar -xzf hadoop-3.3.6.tar.gz
   sudo mv hadoop-3.3.6 /opt/hadoop
   ```

2. **Configure Hadoop**
   ```bash
   export HADOOP_HOME=/opt/hadoop
   export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
   ```

3. **Start Hadoop services**
   ```bash
   start-dfs.sh
   start-yarn.sh
   ```

### Impala Setup

1. **Install Impala** (using Cloudera distribution)
   ```bash
   # Follow Cloudera Impala installation guide
   # Or use Docker image
   docker run -d --name impala -p 21050:21050 apache/impala:4.1.0
   ```

### Tableau Integration

1. **Install Tableau Desktop/Server**
2. **Configure data connections**
   - MongoDB connection for real-time data
   - Impala connection for big data queries
3. **Import dashboard templates** from `tableau/` directory

## Verification

### Test Backend API
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "service": "EduPredict API"}
```

### Test Frontend
Open http://localhost:3000 in your browser

### Test Database Connection
```bash
# Connect to MongoDB
docker exec -it edupredict-mongodb mongosh
use edupredict
db.users.find()
```

### Test Sample Login
Use these credentials to test the system:
- **Admin**: admin@edupredict.com / admin123
- **Teacher**: teacher@edupredict.com / teacher123
- **Student**: student@edupredict.com / student123
- **Analyst**: analyst@edupredict.com / analyst123

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or change port in configuration
   ```

2. **MongoDB connection issues**
   ```bash
   # Check MongoDB status
   docker logs edupredict-mongodb
   # Restart MongoDB
   docker restart edupredict-mongodb
   ```

3. **Frontend build issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   # Delete node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Python dependency issues**
   ```bash
   # Upgrade pip
   pip install --upgrade pip
   # Install with no cache
   pip install --no-cache-dir -r requirements.txt
   ```

### Performance Optimization

1. **Database indexing**
   - Indexes are automatically created by the setup script
   - Monitor query performance and add additional indexes as needed

2. **Caching**
   - Redis is used for session storage and caching
   - Configure cache TTL based on your needs

3. **Background tasks**
   - Celery workers handle ML model training and predictions
   - Scale workers based on load

## Next Steps

1. **Configure email notifications** in `.env` file
2. **Set up monitoring** with tools like Prometheus/Grafana
3. **Configure backup** for MongoDB and user data
4. **Set up CI/CD pipeline** for automated deployments
5. **Train ML models** with your actual data

For more detailed configuration options, see the [Configuration Guide](CONFIGURATION.md).
