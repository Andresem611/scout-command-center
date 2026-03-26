#!/bin/bash
# deploy.sh - Deploy Scout Command Center

echo "🎯 Scout Command Center Deployment"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "scout_data.json" ]; then
    echo "❌ scout_data.json not found. Run from workspace directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install fastapi uvicorn streamlit requests -q

# Start API server
echo "🚀 Starting API server..."
pkill -f "api_server.py" 2>/dev/null
nohup python3 api_server.py > api_server.log 2>&1 &
sleep 2

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API server running on http://localhost:8000"
else
    echo "⚠️  API server may not be running. Check api_server.log"
fi

# Start Streamlit
echo "🎨 Starting Streamlit app..."
echo "Streamlit will be available at: http://localhost:8501"
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
