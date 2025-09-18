# EduPredict Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the EduPredict system in various environments, from development to production.

## Table of Contents

1. [Development Deployment](#development-deployment)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

## Development Deployment

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB 5.0+
- Git

### Backend Setup

1. **Clone and setup backend**
   ```bash
   git clone <repository-url>
   cd edupredict/backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup environment
   cp .env.example .env
   # Edit .env with your settings
   
   # Initialize database
   python seed_data.py
   
   # Start server
   python start_server.py
   ```

2. **Verify backend**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Frontend Setup

1. **Setup frontend**
   ```bash
   cd ../frontend
   
   # Install dependencies
   npm install
   
   # Setup environment
   echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env
   
   # Start development server
   npm start
   ```

2. **Verify frontend**
   - App: http://localhost:3000
   - Login with demo credentials

### Database Setup

1. **MongoDB Local Installation**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb
   
   # macOS
   brew install mongodb-community
   
   # Windows
   # Download from MongoDB website
   ```

2. **MongoDB with Docker**
   ```bash
   docker run -d --name mongodb -p 27017:27017 mongo:7.0
   ```

## Production Deployment

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- OS: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

**Recommended Requirements:**
- CPU: 8 cores
- RAM: 16GB
- Storage: 500GB SSD
- Load Balancer: Nginx/Apache
- SSL Certificate: Let's Encrypt

### Backend Production Setup

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python 3.9+
   sudo apt install python3.9 python3.9-venv python3.9-dev
   
   # Install system dependencies
   sudo apt install build-essential libssl-dev libffi-dev
   ```

2. **Application Setup**
   ```bash
   # Create application user
   sudo useradd -m -s /bin/bash edupredict
   sudo su - edupredict
   
   # Clone repository
   git clone <repository-url>
   cd edupredict/backend
   
   # Setup virtual environment
   python3.9 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Production environment
   cp .env.example .env.production
   # Configure production settings
   ```

3. **Production Environment Variables**
   ```env
   # .env.production
   DEBUG=false
   SECRET_KEY=your-production-secret-key-minimum-32-characters
   MONGODB_URL=mongodb://username:password@localhost:27017/edupredict
   CORS_ALLOWED_ORIGINS=["https://yourdomain.com"]
   ALLOWED_HOSTS=["yourdomain.com", "www.yourdomain.com"]
   LOG_LEVEL=WARNING
   ```

4. **Systemd Service**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/edupredict-backend.service
   ```

   ```ini
   [Unit]
   Description=EduPredict Backend API
   After=network.target mongodb.service
   
   [Service]
   Type=simple
   User=edupredict
   WorkingDirectory=/home/edupredict/edupredict/backend
   Environment=PATH=/home/edupredict/edupredict/backend/venv/bin
   EnvironmentFile=/home/edupredict/edupredict/backend/.env.production
   ExecStart=/home/edupredict/edupredict/backend/venv/bin/python start_server.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start service
   sudo systemctl daemon-reload
   sudo systemctl enable edupredict-backend
   sudo systemctl start edupredict-backend
   sudo systemctl status edupredict-backend
   ```

### Frontend Production Setup

1. **Build Application**
   ```bash
   cd ../frontend
   
   # Install dependencies
   npm ci --only=production
   
   # Build for production
   REACT_APP_API_URL=https://api.yourdomain.com/api/v1 npm run build
   ```

2. **Nginx Configuration**
   ```bash
   sudo nano /etc/nginx/sites-available/edupredict
   ```

   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       # Redirect HTTP to HTTPS
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name yourdomain.com www.yourdomain.com;
       
       # SSL Configuration
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
       
       # Frontend
       location / {
           root /home/edupredict/edupredict/frontend/build;
           index index.html;
           try_files $uri $uri/ /index.html;
           
           # Cache static assets
           location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
               expires 1y;
               add_header Cache-Control "public, immutable";
           }
       }
       
       # Backend API
       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # Timeouts
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }
       
       # Security headers
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-XSS-Protection "1; mode=block" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header Referrer-Policy "no-referrer-when-downgrade" always;
       add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/edupredict /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **SSL Certificate**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   
   # Auto-renewal
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Database Production Setup

1. **MongoDB Production Configuration**
   ```bash
   # Install MongoDB
   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
   sudo apt update
   sudo apt install -y mongodb-org
   
   # Configure MongoDB
   sudo nano /etc/mongod.conf
   ```

   ```yaml
   # /etc/mongod.conf
   storage:
     dbPath: /var/lib/mongodb
     journal:
       enabled: true
   
   systemLog:
     destination: file
     logAppend: true
     path: /var/log/mongodb/mongod.log
   
   net:
     port: 27017
     bindIp: 127.0.0.1
   
   security:
     authorization: enabled
   
   replication:
     replSetName: "rs0"
   ```

   ```bash
   # Start MongoDB
   sudo systemctl enable mongod
   sudo systemctl start mongod
   
   # Create admin user
   mongo
   > use admin
   > db.createUser({
       user: "admin",
       pwd: "secure_password",
       roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
     })
   > exit
   ```

## Docker Deployment

### Development with Docker Compose

1. **Docker Compose Setup**
   ```bash
   cd edupredict
   
   # Start all services
   docker-compose up -d
   
   # Initialize database
   docker-compose exec backend python seed_data.py
   
   # View logs
   docker-compose logs -f
   ```

### Production Docker Setup

1. **Production Docker Compose**
   ```yaml
   # docker-compose.prod.yml
   version: '3.8'
   
   services:
     mongodb:
       image: mongo:7.0
       restart: unless-stopped
       environment:
         MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER}
         MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
       volumes:
         - mongodb_data:/data/db
       networks:
         - edupredict-network
   
     backend:
       build:
         context: ./backend
         dockerfile: Dockerfile.prod
       restart: unless-stopped
       environment:
         - MONGODB_URL=mongodb://${MONGO_ROOT_USER}:${MONGO_ROOT_PASSWORD}@mongodb:27017/edupredict?authSource=admin
         - SECRET_KEY=${SECRET_KEY}
         - DEBUG=false
       depends_on:
         - mongodb
       networks:
         - edupredict-network
   
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile.prod
       restart: unless-stopped
       environment:
         - REACT_APP_API_URL=https://api.yourdomain.com/api/v1
       networks:
         - edupredict-network
   
     nginx:
       image: nginx:alpine
       restart: unless-stopped
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - backend
         - frontend
       networks:
         - edupredict-network
   
   volumes:
     mongodb_data:
   
   networks:
     edupredict-network:
       driver: bridge
   ```

## Cloud Deployment

### AWS Deployment

1. **EC2 Instance Setup**
   ```bash
   # Launch EC2 instance (t3.medium or larger)
   # Configure security groups (ports 22, 80, 443)
   # Attach Elastic IP
   
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Install Docker
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

2. **RDS MongoDB Setup**
   ```bash
   # Use Amazon DocumentDB (MongoDB-compatible)
   # Configure VPC and security groups
   # Update connection string in environment
   ```

### Azure Deployment

1. **Container Instances**
   ```bash
   # Use Azure Container Instances
   # Configure Azure Database for MongoDB
   # Set up Application Gateway for load balancing
   ```

### Google Cloud Deployment

1. **Cloud Run Setup**
   ```bash
   # Use Google Cloud Run for containers
   # Configure Cloud MongoDB Atlas
   # Set up Cloud Load Balancer
   ```

## Monitoring & Maintenance

### Application Monitoring

1. **Health Checks**
   ```bash
   # Backend health
   curl http://localhost:8000/health
   
   # Database connectivity
   curl http://localhost:8000/api/v1/auth/me
   ```

2. **Log Monitoring**
   ```bash
   # Backend logs
   tail -f /var/log/edupredict/backend.log
   
   # System logs
   sudo journalctl -u edupredict-backend -f
   
   # Nginx logs
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Performance Monitoring**
   ```bash
   # System resources
   htop
   
   # Database performance
   mongo --eval "db.stats()"
   
   # API response times
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/students
   ```

### Backup Strategy

1. **Database Backup**
   ```bash
   # Daily backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   mongodump --db edupredict --out /backup/mongodb_$DATE
   
   # Compress backup
   tar -czf /backup/mongodb_$DATE.tar.gz /backup/mongodb_$DATE
   rm -rf /backup/mongodb_$DATE
   
   # Keep only last 7 days
   find /backup -name "mongodb_*.tar.gz" -mtime +7 -delete
   ```

2. **Application Backup**
   ```bash
   # Code backup
   git archive --format=tar.gz --output=/backup/edupredict_$(date +%Y%m%d).tar.gz HEAD
   
   # Configuration backup
   cp .env.production /backup/env_$(date +%Y%m%d).backup
   ```

### Security Hardening

1. **Firewall Configuration**
   ```bash
   # UFW setup
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. **SSL/TLS Configuration**
   ```bash
   # Strong SSL configuration
   sudo nano /etc/nginx/snippets/ssl-params.conf
   ```

   ```nginx
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_prefer_server_ciphers on;
   ssl_dhparam /etc/nginx/dhparam.pem;
   ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
   ssl_ecdh_curve secp384r1;
   ssl_session_timeout 10m;
   ssl_session_cache shared:SSL:10m;
   ssl_session_tickets off;
   ssl_stapling on;
   ssl_stapling_verify on;
   ```

3. **Database Security**
   ```bash
   # MongoDB authentication
   mongo
   > use edupredict
   > db.createUser({
       user: "edupredict_user",
       pwd: "secure_password",
       roles: ["readWrite"]
     })
   ```

## Troubleshooting

### Common Issues

1. **Backend Won't Start**
   ```bash
   # Check Python version
   python --version
   
   # Check dependencies
   pip list
   
   # Check MongoDB connection
   mongo --eval "db.adminCommand('ismaster')"
   
   # Check logs
   tail -f logs/backend.log
   ```

2. **Frontend Build Errors**
   ```bash
   # Clear cache
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   
   # Check Node version
   node --version
   npm --version
   ```

3. **Database Connection Issues**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod
   
   # Check network connectivity
   telnet localhost 27017
   
   # Check authentication
   mongo -u admin -p --authenticationDatabase admin
   ```

4. **SSL Certificate Issues**
   ```bash
   # Check certificate validity
   sudo certbot certificates
   
   # Renew certificate
   sudo certbot renew --dry-run
   
   # Check Nginx configuration
   sudo nginx -t
   ```

### Performance Optimization

1. **Database Optimization**
   ```javascript
   // Create indexes
   db.users.createIndex({ email: 1 }, { unique: true })
   db.students.createIndex({ student_id: 1 }, { unique: true })
   db.grades.createIndex({ student_id: 1, course_id: 1 })
   db.attendance.createIndex({ student_id: 1, date: 1 })
   ```

2. **Application Optimization**
   ```bash
   # Use production WSGI server
   pip install gunicorn
   
   # Start with Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Frontend Optimization**
   ```bash
   # Optimize build
   npm run build
   
   # Analyze bundle size
   npm install -g webpack-bundle-analyzer
   npx webpack-bundle-analyzer build/static/js/*.js
   ```

### Monitoring Setup

1. **Application Monitoring**
   ```bash
   # Install monitoring tools
   pip install prometheus-client
   npm install @prometheus/client
   ```

2. **Log Aggregation**
   ```bash
   # ELK Stack setup
   # Elasticsearch + Logstash + Kibana
   # Or use cloud solutions like AWS CloudWatch
   ```

3. **Alerting**
   ```bash
   # Set up alerts for:
   # - High error rates
   # - Database connection failures
   # - High response times
   # - Disk space usage
   # - Memory usage
   ```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Setup**
   ```nginx
   upstream backend {
       server 127.0.0.1:8000;
       server 127.0.0.1:8001;
       server 127.0.0.1:8002;
   }
   
   server {
       location /api/ {
           proxy_pass http://backend;
       }
   }
   ```

2. **Database Scaling**
   ```bash
   # MongoDB Replica Set
   # Sharding for large datasets
   # Read replicas for analytics
   ```

### Vertical Scaling

1. **Resource Optimization**
   - Monitor CPU and memory usage
   - Optimize database queries
   - Implement caching strategies
   - Use CDN for static assets

## Maintenance Procedures

### Regular Maintenance

1. **Weekly Tasks**
   - Check system logs for errors
   - Monitor disk space usage
   - Review security logs
   - Update system packages

2. **Monthly Tasks**
   - Update application dependencies
   - Review and rotate logs
   - Performance analysis
   - Security audit

3. **Quarterly Tasks**
   - Full system backup
   - Disaster recovery testing
   - Security penetration testing
   - Capacity planning review

### Update Procedures

1. **Application Updates**
   ```bash
   # Backup current version
   git tag v$(date +%Y%m%d)
   
   # Pull updates
   git pull origin main
   
   # Update dependencies
   pip install -r requirements.txt
   npm install
   
   # Run migrations if any
   python migrate.py
   
   # Restart services
   sudo systemctl restart edupredict-backend
   ```

2. **Database Updates**
   ```bash
   # Backup before updates
   mongodump --db edupredict --out backup_before_update
   
   # Apply schema changes
   mongo edupredict < migrations/update_schema.js
   ```

## Support & Documentation

### Getting Help

- **Technical Issues**: Check logs and error messages
- **Performance Issues**: Review monitoring dashboards
- **Security Issues**: Follow incident response procedures
- **General Questions**: Refer to user documentation

### Documentation Links

- [API Documentation](docs/API_DOCUMENTATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Project Report](docs/PROJECT_REPORT.md)

---

**EduPredict Deployment** - Production-Ready Educational Analytics Platform 🚀