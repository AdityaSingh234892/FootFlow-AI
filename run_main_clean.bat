@echo off
echo Starting Main Footstep Tracking System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check basic dependencies
echo Checking dependencies...
python -c "import cv2, tkinter, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing basic requirements...
    pip install opencv-python pillow
    if errorlevel 1 (
        echo Error: Failed to install basic dependencies
        pause
        exit /b 1
    )
)

REM Check for advanced tracking capabilities
python -c "import cv2; cv2.TrackerCSRT_create()" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================
    echo WARNING: Advanced tracking not available
    echo ============================================
    echo.
    echo The application will run with limited functionality.
    echo For full features, install: pip install opencv-contrib-python
    echo.
    echo Alternatives:
    echo 1. Install full features: pip install opencv-contrib-python
    echo 2. Use simplified tracker: run_simple.bat
    echo.
    echo Press any key to continue with limited features...
    pause >nul
)

echo Starting main application...
python main_clean.py

if errorlevel 1 (
    echo.
    echo Application exited with error
    echo.
    echo If you got "Failed to initialize tracker" error:
    echo 1. Install: pip install opencv-contrib-python
    echo 2. Or use: python simple_tracker.py
    echo.
    pause
)
