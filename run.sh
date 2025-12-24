#!/bin/bash

echo "===================================="
echo "BMI Health Tracker - Starting Server"
echo "===================================="
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi

python3 --version

echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo
echo "Starting Flask development server..."
echo
echo "Server will run at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo

python3 app.py
