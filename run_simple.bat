@echo off
echo Starting Simplified Footstep Tracking System...
echo.
echo This version works with basic OpenCV and doesn't require external dependencies
echo (except Pillow for image display)
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install basic requirements if needed
echo Checking dependencies...
python -c "import cv2, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing basic requirements...
    pip install opencv-python pillow
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting application...
python simple_tracker.py

if errorlevel 1 (
    echo.
    echo Application exited with error
    pause
)
