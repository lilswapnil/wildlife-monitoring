#!/bin/bash
# Helper script to run the Wildlife Monitoring Dashboard
# This script activates the virtual environment and runs the FastAPI app

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Run the FastAPI app
echo "🚀 Starting Wildlife Monitoring Dashboard..."
echo "📊 Open your browser to: http://localhost:5009"
echo "   (Using port 5009 for FastAPI)"
echo ""
python app.py

