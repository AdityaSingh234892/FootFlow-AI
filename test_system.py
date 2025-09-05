"""
System Test Script for OpenCV Footstep Tracking System
This script tests all components and identifies any issues
"""

import sys
import os
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        print(f"  OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✓ Tkinter imported successfully")
    except ImportError as e:
        print(f"✗ Tkinter import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL/Pillow imported successfully")
    except ImportError as e:
        print(f"✗ PIL/Pillow import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ Matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ Matplotlib import failed: {e}")
        return False
    
    return True

def test_opencv_features():
    """Test OpenCV tracking features"""
    print("\nTesting OpenCV tracking features...")
    
    try:
        import cv2
        
        # Test tracker creation
        tracker_csrt = cv2.TrackerCSRT_create()
        print("✓ CSRT tracker creation successful")
        
        tracker_kcf = cv2.TrackerKCF_create()
        print("✓ KCF tracker creation successful")
        
        try:
            tracker_mosse = cv2.legacy.TrackerMOSSE_create()
            print("✓ MOSSE tracker creation successful")
        except AttributeError:
            print("⚠ MOSSE tracker not available (legacy module)")
        
        # Test video capture
        cap = cv2.VideoCapture(0)  # Try to access camera
        if cap.isOpened():
            print("✓ Video capture device accessible")
            cap.release()
        else:
            print("⚠ No camera detected (this is normal)")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenCV features test failed: {e}")
        return False

def test_custom_modules():
    """Test our custom modules"""
    print("\nTesting custom modules...")
    
    try:
        from tracking.person_tracker import PersonTracker
        tracker = PersonTracker()
        print("✓ PersonTracker module loaded")
    except Exception as e:
        print(f"✗ PersonTracker module failed: {e}")
        return False
    
    try:
        from tracking.path_visualizer import PathVisualizer
        visualizer = PathVisualizer()
        print("✓ PathVisualizer module loaded")
    except Exception as e:
        print(f"✗ PathVisualizer module failed: {e}")
        return False
    
    try:
        from store.section_manager import SectionManager
        manager = SectionManager()
        print("✓ SectionManager module loaded")
    except Exception as e:
        print(f"✗ SectionManager module failed: {e}")
        return False
    
    try:
        from store.visit_analyzer import VisitAnalyzer
        analyzer = VisitAnalyzer()
        print("✓ VisitAnalyzer module loaded")
    except Exception as e:
        print(f"✗ VisitAnalyzer module failed: {e}")
        return False
    
    try:
        from reporting.report_generator import ReportGenerator
        generator = ReportGenerator()
        print("✓ ReportGenerator module loaded")
    except Exception as e:
        print(f"⚠ ReportGenerator module failed (PDF features may not work): {e}")
    
    try:
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        print("✓ ConfigManager module loaded")
    except Exception as e:
        print(f"✗ ConfigManager module failed: {e}")
        return False
    
    return True

def test_main_application():
    """Test if main application can be instantiated"""
    print("\nTesting main application...")
    
    try:
        # Test without actually running the GUI
        import main
        print("✓ Main module imported successfully")
        
        # Try to create the application object (but don't run it)
        try:
            app = main.FootstepTrackingSystem()
            print("✓ FootstepTrackingSystem can be instantiated")
            
            # Test some basic methods
            app.reset_tracking_data()
            print("✓ Basic methods work")
            
            # Destroy the window without showing it
            app.root.destroy()
            print("✓ Application cleanup successful")
            
        except Exception as e:
            print(f"✗ Application instantiation failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Main module import failed: {e}")
        return False
    
    return True

def test_sample_data():
    """Test if sample data files exist and are valid"""
    print("\nTesting sample data...")
    
    # Check for sample layout file
    if os.path.exists("sample_store_layout.json"):
        try:
            import json
            with open("sample_store_layout.json", 'r') as f:
                layout = json.load(f)
            print("✓ Sample store layout file is valid JSON")
        except Exception as e:
            print(f"✗ Sample store layout file is invalid: {e}")
    else:
        print("⚠ Sample store layout file not found")
    
    # Check if demo can create sample video
    try:
        import demo
        print("✓ Demo module can be imported")
    except Exception as e:
        print(f"✗ Demo module failed: {e}")
    
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("OpenCV Footstep Tracking System - Comprehensive Test")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
        print("\n❌ CRITICAL: Basic imports failed. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    # Test OpenCV features
    if not test_opencv_features():
        all_tests_passed = False
        print("\n❌ CRITICAL: OpenCV features not working properly")
    
    # Test custom modules
    if not test_custom_modules():
        all_tests_passed = False
        print("\n❌ CRITICAL: Custom modules have issues")
    
    # Test main application
    if not test_main_application():
        all_tests_passed = False
        print("\n❌ CRITICAL: Main application cannot start")
    
    # Test sample data
    test_sample_data()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! The system should work properly.")
        print("\nTo start the application:")
        print("1. Run: python main.py")
        print("2. Or use: python launch.py")
        print("3. Or double-click: start.bat")
        print("\nTo create sample data for testing:")
        print("   python demo.py")
    else:
        print("❌ SOME TESTS FAILED. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Update OpenCV: pip install --upgrade opencv-python opencv-contrib-python")
        print("3. Check Python version (requires Python 3.7+)")
    
    return all_tests_passed

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except Exception as e:
        print(f"\n❌ Test script itself failed: {e}")
        print("Traceback:")
        traceback.print_exc()
        print("\nPlease check your Python installation and try again.")
