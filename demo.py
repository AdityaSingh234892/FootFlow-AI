"""
Demo script to test the footstep tracking system with sample data
"""

import cv2
import numpy as np
import json
from datetime import datetime

def create_sample_video():
    """Create a simple sample video for testing"""
    # Create a blank video with moving objects
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('sample_video.mp4', fourcc, 20.0, (640, 480))
    
    for frame_num in range(200):  # 10 seconds at 20 fps
        # Create blank frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 240  # Light gray background
        
        # Draw store sections as rectangles
        cv2.rectangle(frame, (50, 50), (200, 150), (200, 200, 255), 2)  # Electronics
        cv2.rectangle(frame, (250, 50), (400, 150), (200, 255, 200), 2)  # Groceries
        cv2.rectangle(frame, (450, 50), (600, 150), (255, 200, 200), 2)  # Clothing
        cv2.rectangle(frame, (50, 200), (600, 250), (255, 255, 200), 2)  # Checkout
        
        # Add section labels
        cv2.putText(frame, "Electronics", (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, "Groceries", (260, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, "Clothing", (460, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, "Checkout", (300, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Simulate moving people as colored circles
        # Person 1: Moves from entrance through electronics to groceries
        if frame_num < 100:
            x1 = 100 + (frame_num * 3)
            y1 = 300 - (frame_num * 1)
        else:
            x1 = 400
            y1 = 200 - ((frame_num - 100) * 1)
        cv2.circle(frame, (int(x1), int(y1)), 15, (255, 0, 0), -1)  # Blue person
        cv2.putText(frame, "P1", (int(x1-10), int(y1+5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Person 2: Moves from entrance to clothing
        if frame_num > 50 and frame_num < 150:
            x2 = 100 + ((frame_num - 50) * 4)
            y2 = 350 - ((frame_num - 50) * 2)
            cv2.circle(frame, (int(x2), int(y2)), 15, (0, 255, 0), -1)  # Green person
            cv2.putText(frame, "P2", (int(x2-10), int(y2+5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Add frame number
        cv2.putText(frame, f"Frame: {frame_num}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        out.write(frame)
    
    out.release()
    print("Sample video 'sample_video.mp4' created successfully!")

def create_sample_tracking_data():
    """Create sample tracking data for testing reports"""
    tracking_data = {
        "tracking_paths": {
            "1": [
                {"frame": i, "position": [100 + i*3, 300 - i], "timestamp": i*0.05, "bbox": [90 + i*3, 290 - i, 20, 20]}
                for i in range(100)
            ],
            "2": [
                {"frame": i+50, "position": [100 + i*4, 350 - i*2], "timestamp": (i+50)*0.05, "bbox": [90 + i*4, 340 - i*2, 20, 20]}
                for i in range(80)
            ]
        },
        "section_visits": {
            "1": [
                {"section": "Electronics", "entry_frame": 20, "exit_frame": 40, "duration_frames": 20},
                {"section": "Groceries", "entry_frame": 60, "exit_frame": 90, "duration_frames": 30}
            ],
            "2": [
                {"section": "Clothing", "entry_frame": 70, "exit_frame": 120, "duration_frames": 50}
            ]
        },
        "video_info": {
            "total_frames": 200,
            "fps": 20,
            "export_timestamp": datetime.now().isoformat()
        }
    }
    
    with open('sample_tracking_data.json', 'w') as f:
        json.dump(tracking_data, f, indent=2)
    
    print("Sample tracking data 'sample_tracking_data.json' created successfully!")

def run_demo():
    """Run a complete demo of the system"""
    print("OpenCV Footstep Tracking System Demo")
    print("=" * 40)
    
    # Create sample data
    print("1. Creating sample video...")
    create_sample_video()
    
    print("2. Creating sample tracking data...")
    create_sample_tracking_data()
    
    print("3. Demo files created:")
    print("   - sample_video.mp4: Test video with moving people")
    print("   - sample_tracking_data.json: Sample tracking results")
    print("   - sample_store_layout.json: Store layout configuration")
    
    print("\n4. To run the main application:")
    print("   python main_clean.py")
    
    print("\n5. Demo workflow:")
    print("   a) Load 'sample_video.mp4' in the application")
    print("   b) Load 'sample_store_layout.json' for store sections")
    print("   c) Click 'Select Person' and draw boxes around the moving circles")
    print("   d) Watch the tracking and path visualization")
    print("   e) Generate reports to see analytics")
    
    print("\nDemo setup complete!")

if __name__ == "__main__":
    run_demo()
