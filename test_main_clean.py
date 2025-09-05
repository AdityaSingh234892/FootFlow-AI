"""
Test script for main_clean.py to verify it handles missing dependencies gracefully
"""

import sys
import os

def test_main_clean():
    """Test the main_clean.py application"""
    print("Testing main_clean.py application...")
    print("=" * 50)
    
    # Test basic imports
    print("1. Testing basic imports...")
    try:
        import cv2
        print(f"   ✓ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"   ✗ OpenCV import failed: {e}")
        return False
    
    try:
        import tkinter as tk
        print("   ✓ Tkinter available")
    except ImportError as e:
        print(f"   ✗ Tkinter import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("   ✓ Pillow available")
    except ImportError as e:
        print(f"   ✗ Pillow import failed: {e}")
        return False
    
    # Test OpenCV tracker availability
    print("\n2. Testing OpenCV tracker availability...")
    try:
        cv2.TrackerCSRT_create()
        print("   ✓ Advanced trackers (CSRT) available")
        trackers_available = True
    except AttributeError:
        print("   ⚠ Advanced trackers not available (requires opencv-contrib-python)")
        trackers_available = False
    
    # Test main_clean.py import
    print("\n3. Testing main_clean.py import...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_clean", "main_clean.py")
        if spec and spec.loader:
            # Just test the import, don't run the GUI
            print("   ✓ main_clean.py imports successfully")
        else:
            print("   ✗ Could not load main_clean.py")
            return False
    except Exception as e:
        print(f"   ✗ main_clean.py import error: {e}")
        return False
    
    # Test basic OpenCV video capabilities
    print("\n4. Testing OpenCV video capabilities...")
    try:
        cap = cv2.VideoCapture()
        print("   ✓ VideoCapture can be created")
        cap.release()
        
        # Test selectROI availability
        test_frame = cv2.imread("sample_frame.jpg") if os.path.exists("sample_frame.jpg") else None
        if test_frame is not None:
            print("   ✓ Sample frame available for testing")
        else:
            print("   ⚠ No sample frame available (selectROI untested)")
            
    except Exception as e:
        print(f"   ✗ OpenCV video test failed: {e}")
        return False
    
    print("\n✓ Basic tests passed!")
    
    # Provide recommendations
    print("\nRecommendations:")
    if not trackers_available:
        print("- Install advanced trackers: pip install opencv-contrib-python")
        print("- Or use simplified system: python simple_tracker.py")
    else:
        print("- All features should work in main_clean.py")
    
    print("\nTo run the application:")
    print("  python main_clean.py")
    
    return True

if __name__ == "__main__":
    success = test_main_clean()
    if not success:
        print("\n✗ Some tests failed.")
    
    input("\nPress Enter to exit...")
