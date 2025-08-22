#!/bin/bash

# EduPredict Quick Start Script
# This script sets up the entire EduPredict system with one command

set -e

echo "🚀 EduPredict Quick Start Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if ports are available
check_ports() {
    local ports=(3000 8000 27017 6379 9870 21050)
    local busy_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            busy_ports+=($port)
        fi
    done
    
    if [ ${#busy_ports[@]} -ne 0 ]; then
        print_warning "The following ports are busy: ${busy_ports[*]}"
        print_warning "Please stop services using these ports or modify docker-compose.yml"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Create environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i.bak "s/your-super-secret-key-change-in-production/$SECRET_KEY/" backend/.env
        rm backend/.env.bak
        
        print_success "Environment file created with random secret key"
    else
        print_warning "Environment file already exists, skipping..."
    fi
}

# Start services with Docker Compose
start_services() {
    print_status "Starting all services with Docker Compose..."
    
    # Pull latest images
    docker-compose pull
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "All services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for MongoDB
    print_status "Waiting for MongoDB..."
    while ! docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
        sleep 2
    done
    print_success "MongoDB is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    while ! docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for Backend
    print_status "Waiting for Backend API..."
    while ! curl -s http://localhost:8000/health >/dev/null 2>&1; do
        sleep 5
    done
    print_success "Backend API is ready"
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    while ! curl -s http://localhost:3000 >/dev/null 2>&1; do
        sleep 5
    done
    print_success "Frontend is ready"
}

# Initialize database with sample data
initialize_database() {
    print_status "Initializing database with sample data..."
    
    docker-compose exec backend python scripts/setup.py
    
    print_success "Database initialized with sample data"
}

# Display final information
show_completion_info() {
    echo
    echo "🎉 EduPredict Setup Complete!"
    echo "============================="
    echo
    echo "🌐 Access URLs:"
    echo "   Frontend:        http://localhost:3000"
    echo "   Backend API:     http://localhost:8000"
    echo "   API Docs:        http://localhost:8000/api/docs"
    echo "   MongoDB:         mongodb://localhost:27017"
    echo "   Hadoop UI:       http://localhost:9870"
    echo
    echo "👤 Sample Login Credentials:"
    echo "   Admin:    admin@edupredict.com / admin123"
    echo "   Teacher:  teacher@edupredict.com / teacher123"
    echo "   Student:  student@edupredict.com / student123"
    echo "   Analyst:  analyst@edupredict.com / analyst123"
    echo
    echo "📚 Next Steps:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Login with any of the sample credentials"
    echo "   3. Explore the different role-based dashboards"
    echo "   4. Check the API documentation at http://localhost:8000/api/docs"
    echo "   5. Review the documentation in the docs/ folder"
    echo
    echo "🛠️  Useful Commands:"
    echo "   View logs:           docker-compose logs -f"
    echo "   Stop services:       docker-compose down"
    echo "   Restart services:    docker-compose restart"
    echo "   Update services:     docker-compose pull && docker-compose up -d"
    echo
    echo "📖 For more information, see:"
    echo "   - docs/INSTALLATION.md"
    echo "   - docs/API_DOCUMENTATION.md"
    echo "   - docs/USER_GUIDE.md"
    echo
}

# Main execution
main() {
    echo "Starting EduPredict setup process..."
    echo
    
    # Check prerequisites
    check_docker
    check_ports
    
    # Setup
    setup_environment
    start_services
    wait_for_services
    initialize_database
    
    # Complete
    show_completion_info
}

# Handle script interruption
trap 'print_error "Setup interrupted. Run docker-compose down to clean up."; exit 1' INT

# Run main function
main

print_success "Setup completed successfully! 🎉"
