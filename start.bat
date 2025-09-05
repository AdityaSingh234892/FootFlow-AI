@echo off
echo OpenCV Human Footstep Tracking System
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Try to run the launcher
echo Starting the tracking system...
python launch.py

if errorlevel 1 (
    echo.
    echo Failed to start with launcher, trying direct method...
    python main_clean.py
)

if errorlevel 1 (
    echo.
    echo Failed to start the application.
    echo Please check the installation and dependencies.
    echo Try running: pip install -r requirements.txt
)

pause
