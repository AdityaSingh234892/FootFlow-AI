"""
Installation script for OpenCV Footstep Tracking System
This script installs all required dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("OpenCV Footstep Tracking System - Installation Script")
    print("=" * 60)
    
    # Required packages
    packages = [
        "opencv-python>=4.8.1",
        "opencv-contrib-python>=4.8.1", 
        "numpy>=1.24.3",
        "matplotlib>=3.7.2",
        "pandas>=2.0.3",
        "reportlab>=4.0.4",
        "Pillow>=10.0.0",
        "scipy>=1.11.1",
        "seaborn>=0.12.2"
    ]
    
    print("Installing required packages...")
    
    failed_packages = []
    
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Failed to install {package}")
            failed_packages.append(package)
    
    print("\n" + "=" * 60)
    
    if not failed_packages:
        print("🎉 All packages installed successfully!")
        print("\nThe system is ready to use. You can now run:")
        print("  python main.py")
        print("  or")
        print("  python launch.py")
        
        # Test the installation
        print("\nRunning system test...")
        try:
            subprocess.run([sys.executable, "test_system.py"], check=False)
        except FileNotFoundError:
            print("Test script not found, but installation completed.")
            
    else:
        print("❌ Some packages failed to install:")
        for package in failed_packages:
            print(f"  - {package}")
        
        print("\nTry installing manually:")
        print("  pip install -r requirements.txt")
        print("\nOr install individual packages:")
        for package in failed_packages:
            print(f"  pip install {package}")

if __name__ == "__main__":
    main()
