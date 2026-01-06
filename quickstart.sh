#!/bin/bash

# C4 Enterprise Platform - Quick Start Script
# This script sets up and starts the entire platform

set -e

echo "🚀 C4 Enterprise Platform - Quick Start"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter after you've added your API key to backend/.env..."
fi

# Check if API key is set
if grep -q "your-key-here" backend/.env; then
    echo "❌ Please set your ANTHROPIC_API_KEY in backend/.env"
    exit 1
fi

echo "✓ Environment configuration found"
echo ""

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T backend python init_db.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "Happy diagramming! 🎨"
