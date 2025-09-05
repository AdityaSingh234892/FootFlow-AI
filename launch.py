"""
Simple launcher for the Footstep Tracking System
This script handles dependencies and provides a clean startup experience
"""

import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'cv2',
        'numpy',
        'tkinter',
        'PIL',
        'matplotlib',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function"""
    print("OpenCV Human Footstep Tracking System")
    print("=" * 50)
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        response = input("Would you like to install them automatically? (y/n): ")
        
        if response.lower() == 'y':
            if install_dependencies():
                print("Dependencies installed successfully!")
            else:
                print("Failed to install dependencies. Please install manually:")
                print("pip install -r requirements.txt")
                return
        else:
            print("Please install the required packages and try again.")
            return
    
    # Start the application
    print("Starting the application...")
    
    try:
        # Import and run the main application
        from main_clean import FootstepTrackingSystem
        app = FootstepTrackingSystem()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("\nTrying to run with basic functionality...")
        
        # Fallback to basic version
        try:
            import main_clean
            print("Application started successfully!")
        except Exception as e2:
            print(f"Failed to start application: {e2}")
            print("\nPlease check the installation and try running 'python main_clean.py' directly.")

if __name__ == "__main__":
    main()
