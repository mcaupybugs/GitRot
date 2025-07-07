#!/bin/bash

# GitRot Development Startup Script
echo "🚀 Starting GitRot Development Environment..."

# Start FastAPI backend
echo "📡 Starting FastAPI backend on port 8000..."
cd /Users/vishalyadav/PersonalCode/GitRot
source gitrot/bin/activate
python fastapi_app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Next.js frontend
echo "🎨 Starting Next.js frontend on port 3000..."
cd gitrot-frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to handle cleanup when script is terminated
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Wait for both processes
wait
