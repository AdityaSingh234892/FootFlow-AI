"""
Path Visualizer Module
Handles visualization of tracking paths and footsteps
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple
import math

class PathVisualizer:
    def __init__(self):
        self.person_colors = {
            1: (255, 0, 0),    # Red
            2: (0, 255, 0),    # Green
            3: (0, 0, 255),    # Blue
            4: (255, 255, 0),  # Yellow
            5: (255, 0, 255),  # Magenta
            6: (0, 255, 255),  # Cyan
            7: (255, 165, 0),  # Orange
            8: (128, 0, 128),  # Purple
            9: (255, 192, 203), # Pink
            10: (0, 128, 0),   # Dark Green
        }
        self.path_thickness = 3
        self.point_radius = 5
        self.timestamp_font = cv2.FONT_HERSHEY_SIMPLEX
        self.timestamp_scale = 0.4
        
    def get_person_color(self, person_id: int) -> Tuple[int, int, int]:
        """Get color for a specific person"""
        if person_id in self.person_colors:
            return self.person_colors[person_id]
        else:
            # Generate a color based on person_id
            hue = (person_id * 137) % 360  # Use golden angle for good distribution
            color = self._hsv_to_bgr(hue, 255, 255)
            self.person_colors[person_id] = color
            return color
            
    def _hsv_to_bgr(self, h: float, s: int, v: int) -> Tuple[int, int, int]:
        """Convert HSV to BGR color"""
        h = h / 360.0
        s = s / 255.0
        v = v / 255.0
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
            
        return (int(b * 255), int(g * 255), int(r * 255))
        
    def draw_paths(self, frame: np.ndarray, tracking_paths: Dict) -> np.ndarray:
        """Draw all tracking paths on the frame"""
        for person_id, path_points in tracking_paths.items():
            if len(path_points) < 2:
                continue
                
            color = self.get_person_color(person_id)
            self._draw_person_path(frame, path_points, color, person_id)
            
        return frame
        
    def _draw_person_path(self, frame: np.ndarray, path_points: List[Dict], 
                         color: Tuple[int, int, int], person_id: int):
        """Draw path for a specific person"""
        if len(path_points) < 2:
            return
            
        # Draw lines connecting consecutive points
        for i in range(1, len(path_points)):
            pt1 = path_points[i-1]['position']
            pt2 = path_points[i]['position']
            
            # Calculate alpha based on point age (fade older points)
            alpha = min(1.0, (len(path_points) - i) / max(1, len(path_points) * 0.7))
            faded_color = tuple(int(c * alpha) for c in color)
            
            cv2.line(frame, pt1, pt2, faded_color, self.path_thickness)
            
        # Draw points at key locations
        self._draw_key_points(frame, path_points, color)
        
        # Draw timestamps at intervals
        self._draw_timestamps(frame, path_points, color)
        
        # Draw current position with larger circle
        if path_points:
            current_pos = path_points[-1]['position']
            cv2.circle(frame, current_pos, self.point_radius + 2, color, -1)
            cv2.circle(frame, current_pos, self.point_radius + 4, (255, 255, 255), 2)
            
            # Draw person ID near current position
            text_pos = (current_pos[0] + 10, current_pos[1] - 10)
            cv2.putText(frame, f"P{person_id}", text_pos, self.timestamp_font, 
                       0.6, color, 2)
                       
    def _draw_key_points(self, frame: np.ndarray, path_points: List[Dict], 
                        color: Tuple[int, int, int]):
        """Draw key points along the path (direction changes, stops)"""
        if len(path_points) < 3:
            return
            
        for i in range(1, len(path_points) - 1):
            # Check for significant direction changes
            if self._is_direction_change(path_points, i):
                pos = path_points[i]['position']
                cv2.circle(frame, pos, self.point_radius, color, -1)
                cv2.circle(frame, pos, self.point_radius + 2, (255, 255, 255), 1)
                
    def _is_direction_change(self, path_points: List[Dict], index: int, 
                           threshold: float = 45.0) -> bool:
        """Check if there's a significant direction change at given index"""
        if index <= 0 or index >= len(path_points) - 1:
            return False
            
        # Get three consecutive points
        p1 = path_points[index - 1]['position']
        p2 = path_points[index]['position']
        p3 = path_points[index + 1]['position']
        
        # Calculate vectors
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # Calculate angle between vectors
        angle = self._angle_between_vectors(v1, v2)
        
        return abs(angle) > threshold
        
    def _angle_between_vectors(self, v1: Tuple[float, float], 
                             v2: Tuple[float, float]) -> float:
        """Calculate angle between two vectors in degrees"""
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        magnitude1 = math.sqrt(v1[0]**2 + v1[1]**2)
        magnitude2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
            
        cos_angle = dot_product / (magnitude1 * magnitude2)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
        
        angle_rad = math.acos(cos_angle)
        return math.degrees(angle_rad)
        
    def _draw_timestamps(self, frame: np.ndarray, path_points: List[Dict], 
                        color: Tuple[int, int, int]):
        """Draw timestamps at intervals along the path"""
        if len(path_points) < 10:
            return
            
        # Draw timestamp every 30 points (approximately every second at 30fps)
        interval = max(30, len(path_points) // 10)
        
        for i in range(0, len(path_points), interval):
            point = path_points[i]
            timestamp = point['timestamp']
            pos = point['position']
            
            # Format timestamp as MM:SS
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Draw timestamp with background
            text_size = cv2.getTextSize(time_str, self.timestamp_font, 
                                      self.timestamp_scale, 1)[0]
            text_pos = (pos[0] - text_size[0] // 2, pos[1] - 10)
            bg_pos = (text_pos[0] - 2, text_pos[1] - text_size[1] - 2)
            bg_size = (text_size[0] + 4, text_size[1] + 4)
            
            cv2.rectangle(frame, bg_pos, 
                         (bg_pos[0] + bg_size[0], bg_pos[1] + bg_size[1]), 
                         (0, 0, 0), -1)
            cv2.putText(frame, time_str, text_pos, self.timestamp_font, 
                       self.timestamp_scale, color, 1)
                       
    def draw_path_metrics(self, frame: np.ndarray, tracking_paths: Dict, 
                         position: Tuple[int, int] = (10, 30)):
        """Draw path metrics overlay"""
        y_offset = position[1]
        
        for person_id, path_points in tracking_paths.items():
            if not path_points:
                continue
                
            color = self.get_person_color(person_id)
            
            # Calculate metrics
            total_distance = self._calculate_path_distance(path_points)
            duration = path_points[-1]['timestamp'] - path_points[0]['timestamp']
            
            # Format metrics text
            distance_text = f"P{person_id}: {total_distance:.1f}px"
            duration_text = f"Time: {duration:.1f}s"
            
            # Draw metrics
            cv2.putText(frame, distance_text, (position[0], y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, duration_text, (position[0] + 150, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            y_offset += 25
            
    def _calculate_path_distance(self, path_points: List[Dict]) -> float:
        """Calculate total distance traveled along path"""
        if len(path_points) < 2:
            return 0.0
            
        total_distance = 0.0
        for i in range(1, len(path_points)):
            p1 = path_points[i-1]['position']
            p2 = path_points[i]['position']
            distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_distance += distance
            
        return total_distance
        
    def create_path_heatmap(self, frame_shape: Tuple[int, int], 
                           tracking_paths: Dict) -> np.ndarray:
        """Create a heatmap showing popular paths"""
        height, width = frame_shape[:2]
        heatmap = np.zeros((height, width), dtype=np.float32)
        
        for person_id, path_points in tracking_paths.items():
            for point in path_points:
                x, y = point['position']
                if 0 <= x < width and 0 <= y < height:
                    # Add gaussian blob around each point
                    self._add_gaussian_blob(heatmap, x, y, radius=20, intensity=1.0)
                    
        # Normalize and convert to color
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
            
        # Convert to color heatmap
        heatmap_color = cv2.applyColorMap((heatmap * 255).astype(np.uint8), 
                                        cv2.COLORMAP_JET)
        
        return heatmap_color
        
    def _add_gaussian_blob(self, heatmap: np.ndarray, x: int, y: int, 
                          radius: int, intensity: float):
        """Add a gaussian blob to the heatmap"""
        height, width = heatmap.shape
        
        # Create gaussian kernel
        kernel_size = radius * 2 + 1
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        
        for i in range(kernel_size):
            for j in range(kernel_size):
                dx = i - radius
                dy = j - radius
                distance = math.sqrt(dx**2 + dy**2)
                if distance <= radius:
                    kernel[i, j] = intensity * math.exp(-(distance**2) / (2 * (radius/3)**2))
                    
        # Apply kernel to heatmap
        start_x = max(0, x - radius)
        end_x = min(width, x + radius + 1)
        start_y = max(0, y - radius)
        end_y = min(height, y + radius + 1)
        
        kernel_start_x = max(0, radius - x)
        kernel_end_x = kernel_start_x + (end_x - start_x)
        kernel_start_y = max(0, radius - y)
        kernel_end_y = kernel_start_y + (end_y - start_y)
        
        if kernel_end_x > kernel_start_x and kernel_end_y > kernel_start_y:
            heatmap[start_y:end_y, start_x:end_x] += kernel[kernel_start_y:kernel_end_y, 
                                                           kernel_start_x:kernel_end_x]
