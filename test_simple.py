"""
Test script for the simplified tracking system
"""

import os
import sys

def test_simplified_system():
    """Test the simplified tracking system components"""
    print("Testing Simplified Footstep Tracking System")
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
        import numpy as np
        print(f"   ✓ NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"   ✗ NumPy import failed: {e}")
        return False
    
    try:
        import tkinter as tk
        print("   ✓ Tkinter available")
    except ImportError as e:
        print(f"   ✗ Tkinter import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print(f"   ✓ Pillow available")
    except ImportError as e:
        print(f"   ✗ Pillow import failed: {e}")
        print("   Run: pip install pillow")
        return False
    
    # Test fallback tracker
    print("\n2. Testing fallback tracker...")
    try:
        from tracking.fallback_tracker import FallbackPersonTracker, BasicTracker
        tracker = FallbackPersonTracker()
        print("   ✓ Fallback tracker created successfully")
        
        # Test basic tracker
        basic = BasicTracker()
        print("   ✓ Basic tracker created successfully")
        
    except ImportError as e:
        print(f"   ✗ Fallback tracker import failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Fallback tracker error: {e}")
        return False
    
    # Test simple tracker
    print("\n3. Testing simple tracker module...")
    try:
        # Don't actually run the GUI, just test import
        import importlib.util
        spec = importlib.util.spec_from_file_location("simple_tracker", "simple_tracker.py")
        if spec and spec.loader:
            simple_tracker = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(simple_tracker)
            print("   ✓ Simple tracker module loads successfully")
        else:
            print("   ✗ Could not load simple_tracker.py")
            return False
            
    except Exception as e:
        print(f"   ✗ Simple tracker module error: {e}")
        return False
    
    # Test OpenCV video capabilities
    print("\n4. Testing OpenCV video capabilities...")
    try:
        # Test video capture creation (without opening a file)
        cap = cv2.VideoCapture()
        print("   ✓ VideoCapture can be created")
        cap.release()
        
        # Test basic image operations
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        print("   ✓ Basic image operations work")
        
        # Test template matching
        template = test_image[20:40, 20:40]
        result = cv2.matchTemplate(gray, cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED)
        print("   ✓ Template matching available")
        
    except Exception as e:
        print(f"   ✗ OpenCV video test failed: {e}")
        return False
    
    print("\n✓ All tests passed!")
    print("\nSimplified System Features:")
    print("- Basic person tracking using template matching")
    print("- Manual person selection with mouse")
    print("- Store section definition")
    print("- Path visualization")
    print("- Simple text report export")
    print("- Works with basic OpenCV installation")
    
    print("\nTo run the simplified system:")
    print("  python simple_tracker.py")
    print("  or double-click run_simple.bat")
    
    return True

if __name__ == "__main__":
    success = test_simplified_system()
    if not success:
        print("\n✗ Some tests failed. Please install missing dependencies.")
        print("\nBasic requirements:")
        print("  pip install opencv-python pillow")
    
    input("\nPress Enter to exit...")
