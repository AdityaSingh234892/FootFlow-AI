"""
Basic Manual Tracking System - Works without opencv-contrib-python
This provides basic tracking functionality when advanced trackers are not available
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional

class BasicTracker:
    """Basic template matching tracker as fallback"""
    
    def __init__(self):
        self.template = None
        self.bbox = None
        self.last_position = None
        
    def init(self, frame: np.ndarray, bbox: Tuple[float, float, float, float]) -> bool:
        """Initialize tracker with template"""
        x, y, w, h = bbox
        x, y, w, h = int(x), int(y), int(w), int(h)
        
        if w > 0 and h > 0:
            self.template = frame[y:y+h, x:x+w]
            self.bbox = (x, y, w, h)
            self.last_position = (x + w//2, y + h//2)
            return True
        return False
        
    def update(self, frame: np.ndarray) -> Tuple[bool, Tuple[float, float, float, float]]:
        """Update tracker position using template matching"""
        if self.template is None:
            return False, (0, 0, 0, 0)
            
        try:
            # Template matching
            result = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.5:  # Confidence threshold
                x, y = max_loc
                w, h = self.template.shape[1], self.template.shape[0]
                self.bbox = (x, y, w, h)
                self.last_position = (x + w//2, y + h//2)
                return True, self.bbox
            else:
                # If template matching fails, return last known position
                return False, self.bbox
                
        except Exception as e:
            print(f"Tracking error: {e}")
            return False, self.bbox

class FallbackPersonTracker:
    """Fallback person tracker that works without opencv-contrib-python"""
    
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
        self.use_opencv_trackers = self._check_opencv_trackers()
        
    def _check_opencv_trackers(self) -> bool:
        """Check if OpenCV trackers are available"""
        try:
            cv2.TrackerCSRT_create()
            return True
        except AttributeError:
            print("OpenCV contrib trackers not available, using basic tracking")
            return False
            
    def create_tracker(self, tracker_type: str = "CSRT"):
        """Create a new tracker instance"""
        if self.use_opencv_trackers:
            try:
                if tracker_type == "CSRT":
                    return cv2.TrackerCSRT_create()
                elif tracker_type == "KCF":
                    return cv2.TrackerKCF_create()
                elif tracker_type == "MOSSE":
                    try:
                        return cv2.legacy.TrackerMOSSE_create()
                    except AttributeError:
                        return cv2.TrackerKCF_create()
                else:
                    return cv2.TrackerCSRT_create()
            except AttributeError:
                pass
                
        # Fallback to basic tracker
        return BasicTracker()
        
    def add_person(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                   tracker_type: str = "CSRT") -> int:
        """Add a new person to track"""
        person_id = self.next_id
        self.next_id += 1
        
        tracker = self.create_tracker(tracker_type)
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
