#!/bin/bash

echo "🚀 Setting up Finance Dashboard..."

# Backend setup
echo "📦 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

echo "✅ Backend setup complete!"

# Frontend setup
echo "📦 Setting up React frontend..."
cd ../frontend

# Install Node dependencies
npm install

echo "✅ Frontend setup complete!"

# Create missing directories
mkdir -p src/components/ui

echo "🎉 Setup complete! To run the application:"
echo ""
echo "Backend (Terminal 1):"
echo "cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Frontend (Terminal 2):"
echo "cd frontend && npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser" 