#!/bin/bash

# C4 Platform - Full Stack Startup Script
# Starts both Django backend and React frontend

set -e

echo "🚀 Starting C4 Platform Full Stack Application"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if backend-django exists
if [ ! -d "backend-django" ]; then
    echo -e "${RED}❌ backend-django directory not found!${NC}"
    exit 1
fi

# Check if frontend exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend directory not found!${NC}"
    exit 1
fi

# ============================================
# BACKEND SETUP
# ============================================
echo "📦 Setting up Django Backend..."

# Check if virtual environment exists
if [ ! -d "backend-django/venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd backend-django
    python -m venv venv
    cd ..
fi

# Check if .env exists
if [ ! -f "backend-django/.env" ]; then
    echo -e "${RED}❌ backend-django/.env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your API key"
    exit 1
fi

# Activate virtual environment and check dependencies
cd backend-django
source venv/bin/activate

if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -q -r requirements.txt
fi

cd ..

# ============================================
# FRONTEND SETUP
# ============================================
echo "📦 Setting up React Frontend..."

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Check if frontend .env exists
if [ ! -f "frontend/.env" ]; then
    echo -e "${RED}❌ frontend/.env file not found!${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ Setup complete! Starting servers..."
echo "================================================"
echo ""

# ============================================
# CLEANUP EXISTING PROCESSES
# ============================================
echo "🧹 Cleaning up existing processes..."

# Kill any process on port 8001
if lsof -ti:8001 >/dev/null 2>&1; then
    echo "  Killing process on port 8001..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Kill any process on port 5173
if lsof -ti:5173 >/dev/null 2>&1; then
    echo "  Killing process on port 5173..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "✅ Ports cleared"
echo ""

# ============================================
# START BACKEND
# ============================================
echo -e "${GREEN}🔧 Starting Django Backend on http://localhost:8001${NC}"
cd backend-django
source venv/bin/activate
python manage.py runserver 8001 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check backend.log for errors${NC}"
    cat backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# ============================================
# START FRONTEND
# ============================================
echo -e "${GREEN}⚛️  Starting React Frontend on http://localhost:5173${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start. Check frontend.log for errors${NC}"
    cat frontend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo "================================================"
echo "🎉 C4 Platform is running!"
echo "================================================"
echo ""
echo "📍 Frontend:        http://localhost:5173"
echo "📍 Backend API:     http://localhost:8001/api"
echo "📍 API Docs:        http://localhost:8001/api/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running and monitor processes
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend process died unexpectedly${NC}"
        echo "Check backend.log for errors"
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend process died unexpectedly${NC}"
        echo "Check frontend.log for errors"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 5
done
