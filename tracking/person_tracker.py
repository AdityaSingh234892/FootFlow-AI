"""
Person Tracker Module
Handles tracking of individuals using OpenCV tracking algorithms
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional

class PersonTracker:
    def __init__(self):
        self.trackers = {}
        self.next_id = 1
        self.tracking_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (255, 192, 203), # Pink
            (0, 128, 0),    # Dark Green
        ]
        
    def create_tracker(self, tracker_type: str = "CSRT"):
        """Create a new tracker instance"""
        try:
            if tracker_type == "CSRT":
                return cv2.TrackerCSRT_create()
            elif tracker_type == "KCF":
                return cv2.TrackerKCF_create()
            elif tracker_type == "MOSSE":
                try:
                    return cv2.legacy.TrackerMOSSE_create()
                except AttributeError:
                    # Fallback to KCF if MOSSE not available
                    print("MOSSE tracker not available, using KCF instead")
                    return cv2.TrackerKCF_create()
            else:
                return cv2.TrackerCSRT_create()  # Default to CSRT
        except AttributeError as e:
            print(f"Tracker {tracker_type} not available: {e}")
            # Try a basic KCF tracker as fallback
            try:
                return cv2.TrackerKCF_create()
            except AttributeError:
                print("No OpenCV trackers available. Please install opencv-contrib-python")
                return None
            
    def add_person(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                   tracker_type: str = "CSRT") -> int:
        """Add a new person to track"""
        person_id = self.next_id
        self.next_id += 1
        
        tracker = self.create_tracker(tracker_type)
        if tracker is None:
            print("Failed to create tracker - tracking not available")
            return -1
            
        success = tracker.init(frame, bbox)
        
        if success:
            self.trackers[person_id] = {
                'tracker': tracker,
                'active': True,
                'bbox': bbox,
                'color': self.tracking_colors[person_id % len(self.tracking_colors)],
                'tracker_type': tracker_type,
                'lost_frames': 0
            }
            return person_id
        else:
            return -1
            
    def update_trackers(self, frame: np.ndarray) -> Dict[int, Dict]:
        """Update all active trackers"""
        results = {}
        
        for person_id, tracker_data in list(self.trackers.items()):
            if not tracker_data['active']:
                continue
                
            tracker = tracker_data['tracker']
            success, bbox = tracker.update(frame)
            
            if success:
                tracker_data['bbox'] = bbox
                tracker_data['lost_frames'] = 0
                results[person_id] = {
                    'bbox': bbox,
                    'center': self._get_center(bbox),
                    'color': tracker_data['color'],
                    'success': True
                }
            else:
                tracker_data['lost_frames'] += 1
                
                # Deactivate tracker if lost for too many frames
                if tracker_data['lost_frames'] > 30:  # 1 second at 30fps
                    tracker_data['active'] = False
                    
                results[person_id] = {
                    'bbox': tracker_data['bbox'],
                    'center': self._get_center(tracker_data['bbox']),
                    'color': tracker_data['color'],
                    'success': False
                }
                
        return results
        
    def _get_center(self, bbox: Tuple[float, float, float, float]) -> Tuple[int, int]:
        """Get center point of bounding box"""
        x, y, w, h = bbox
        return (int(x + w/2), int(y + h/2))
        
    def remove_person(self, person_id: int):
        """Remove a person from tracking"""
        if person_id in self.trackers:
            self.trackers[person_id]['active'] = False
            
    def clear_all(self):
        """Clear all trackers"""
        self.trackers.clear()
        self.next_id = 1
        
    def get_active_trackers(self) -> List[int]:
        """Get list of active tracker IDs"""
        return [pid for pid, data in self.trackers.items() if data['active']]
        
    def get_tracker_info(self, person_id: int) -> Optional[Dict]:
        """Get information about a specific tracker"""
        return self.trackers.get(person_id)
        
    def reinitialize_tracker(self, person_id: int, frame: np.ndarray, 
                           bbox: Tuple[int, int, int, int]) -> bool:
        """Reinitialize a lost tracker"""
        if person_id not in self.trackers:
            return False
            
        tracker_data = self.trackers[person_id]
        new_tracker = self.create_tracker(tracker_data['tracker_type'])
        success = new_tracker.init(frame, bbox)
        
        if success:
            tracker_data['tracker'] = new_tracker
            tracker_data['bbox'] = bbox
            tracker_data['active'] = True
            tracker_data['lost_frames'] = 0
            return True
            
        return False
