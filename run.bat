@echo off
REM Helper script to run the Wildlife Monitoring Dashboard (Windows)
REM This script activates the virtual environment and runs the Flask app

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the Flask app
echo Starting Wildlife Monitoring Dashboard...
echo Open your browser to: http://localhost:5001
echo.
python app.py

