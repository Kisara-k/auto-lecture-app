@echo off
echo Starting Auto Lecture App Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file and add your OpenAI API key
    pause
)

REM Start the FastAPI server
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
python main.py
