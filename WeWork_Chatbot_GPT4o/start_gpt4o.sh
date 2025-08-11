#!/bin/bash

# WeWork Chatbot GPT-4o Startup Script

echo "🚀 Starting WeWork Chatbot with GPT-4o..."
echo "============================================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Conda first."
    exit 1
fi

# Check if environment exists
if ! conda env list | grep -q "wework-gpt4o"; then
    echo "📦 Creating conda environment..."
    conda create -n wework-gpt4o python=3.9 -y
fi

# Activate environment
echo "🔧 Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate wework-gpt4o

# Install dependencies
echo "📥 Installing dependencies..."
cd RAG
pip install -r requirements.txt

# Check for API key
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please create one from api_key_template.txt"
    echo "📋 Run: cp api_key_template.txt .env"
    echo "✏️  Then edit .env with your OpenAI API key"
    exit 1
fi

# Start backend
echo "🔥 Starting GPT-4o backend..."
# Use shared data folder if present
export WEWORK_DATA_DIR=${WEWORK_DATA_DIR:-"$(cd ../.. && pwd)/data/files"}
export WEWORK_URLS_FILE=${WEWORK_URLS_FILE:-"$(cd ../.. && pwd)/data/url_files/urls.txt"}
python flask_api.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
echo "🌐 Starting chatbot UI..."
cd ../Chatbot_UI
python3 server.py &
FRONTEND_PID=$!

echo ""
echo "✅ WeWork Chatbot is now running!"
echo "🔵 Backend (GPT-4o): http://localhost:5000"
echo "🔵 Frontend: http://localhost:8080"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "echo '🛑 Stopping servers...' && kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" SIGINT
wait
