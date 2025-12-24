@echo off
echo ====================================
echo BMI Health Tracker - Starting Server
echo ====================================
echo.
echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo Python is installed. Checking dependencies...
python -c "import flask" > nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Flask development server...
echo.
echo Server will run at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
