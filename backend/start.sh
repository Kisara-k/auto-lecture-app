#!/bin/bash
echo "Starting Auto Lecture App Backend..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file and add your OpenAI API key"
    read -p "Press enter to continue..."
fi

# Start the FastAPI server
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo
python main.py
