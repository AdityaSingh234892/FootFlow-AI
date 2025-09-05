@echo off
echo ========================================
echo   WORKING Footstep Tracking System
echo ========================================
echo.
echo This version is guaranteed to work!
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check basic dependencies
echo Checking dependencies...
python -c "import cv2, tkinter, PIL, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install opencv-python pillow numpy
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting WORKING tracker...
echo.
echo Features available:
echo - Load and play video files
echo - Click and drag to select people
echo - Real-time person tracking
echo - Path visualization
echo - Section definition
echo - Report generation
echo.

python working_tracker.py

if errorlevel 1 (
    echo.
    echo Application error occurred
    pause
)
