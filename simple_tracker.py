"""
Simplified OpenCV Footstep Tracking System
Works with basic OpenCV installation - no external dependencies required
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading
import time

# Import our fallback tracker
from tracking.fallback_tracker import FallbackPersonTracker

class SimplifiedFootstepTracker:
    """Simplified footstep tracking system that works without external dependencies"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simplified Footstep Tracking System")
        self.root.geometry("800x600")
        
        # Core data
        self.current_video = None
        self.current_frame = None
        self.frame_count = 0
        self.fps = 30
        self.playing = False
        self.frame_index = 0
        
        # Tracking data
        self.tracker = FallbackPersonTracker()
        self.person_paths = {}  # person_id -> list of (x, y, frame) points
        self.store_sections = {}  # section_name -> list of (x, y) points
        self.section_visits = {}  # person_id -> list of (section, entry_frame, exit_frame)
        
        # UI state
        self.selection_mode = False
        self.current_selection = None
        self.defining_section = False
        self.section_points = []
        self.section_name = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="Load Video", command=self.load_video).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Play/Pause", command=self.toggle_playback).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Select Person", command=self.start_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Define Section", command=self.start_section_definition).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Report", command=self.export_simple_report).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Video display frame
        self.video_frame = tk.Frame(main_frame, bg='black', height=400)
        self.video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Status and info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(info_frame, text="Ready - Load a video to begin")
        self.status_label.pack(side=tk.LEFT)
        
        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.pack(side=tk.RIGHT)
        
    def load_video(self):
        """Load video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_video = cv2.VideoCapture(file_path)
                self.frame_count = int(self.current_video.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.current_video.get(cv2.CAP_PROP_FPS) or 30
                
                # Read first frame
                ret, frame = self.current_video.read()
                if ret:
                    self.current_frame = frame
                    self.frame_index = 0
                    self.display_frame()
                    self.status_label.config(text=f"Video loaded: {os.path.basename(file_path)}")
                    self.info_label.config(text=f"Frames: {self.frame_count} | FPS: {self.fps:.1f}")
                else:
                    messagebox.showerror("Error", "Could not read video file")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load video: {str(e)}")
                
    def display_frame(self):
        """Display current frame in the UI"""
        if self.current_frame is None:
            return
            
        # Create a copy for display
        display_frame = self.current_frame.copy()
        
        # Draw tracking information
        self.draw_tracking_info(display_frame)
        
        # Convert to RGB for tkinter
        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        
        # Resize to fit display
        height, width = frame_rgb.shape[:2]
        display_width = self.video_frame.winfo_width() or 640
        display_height = self.video_frame.winfo_height() or 480
        
        if display_width > 1 and display_height > 1:
            scale = min(display_width / width, display_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
        
        # Convert to PhotoImage and display
        from PIL import Image, ImageTk
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)
        
        # Clear and create label
        for widget in self.video_frame.winfo_children():
            widget.destroy()
            
        label = tk.Label(self.video_frame, image=photo, bg='black')
        label.image = photo  # Keep a reference
        label.pack(expand=True)
        
        # Bind mouse events for selection
        label.bind("<Button-1>", self.on_mouse_click)
        label.bind("<B1-Motion>", self.on_mouse_drag)
        label.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Update progress
        if self.frame_count > 0:
            progress = (self.frame_index / self.frame_count) * 100
            self.progress_var.set(progress)
            
    def draw_tracking_info(self, frame):
        """Draw tracking paths and sections on frame"""
        # Draw store sections
        for section_name, points in self.store_sections.items():
            if len(points) > 2:
                pts = np.array(points, np.int32)
                cv2.polylines(frame, [pts], True, (0, 255, 255), 2)
                # Add section label
                if points:
                    cv2.putText(frame, section_name, points[0], 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw person paths
        for person_id, path in self.person_paths.items():
            if len(path) > 1:
                color = self.tracker.trackers.get(person_id, {}).get('color', (0, 255, 0))
                
                # Draw path line
                for i in range(1, len(path)):
                    pt1 = (int(path[i-1][0]), int(path[i-1][1]))
                    pt2 = (int(path[i][0]), int(path[i][1]))
                    cv2.line(frame, pt1, pt2, color, 2)
                
                # Draw current position
                if path:
                    current_pos = (int(path[-1][0]), int(path[-1][1]))
                    cv2.circle(frame, current_pos, 8, color, -1)
                    cv2.putText(frame, f"Person {person_id}", 
                              (current_pos[0] + 10, current_pos[1] - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw current selection
        if self.current_selection:
            x, y, w, h = self.current_selection
            cv2.rectangle(frame, (int(x), int(y)), 
                         (int(x + w), int(y + h)), (255, 255, 255), 2)
            
    def start_selection(self):
        """Start person selection mode"""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "Please load a video first")
            return
            
        self.selection_mode = True
        self.status_label.config(text="Click and drag to select a person to track")
        
    def on_mouse_click(self, event):
        """Handle mouse click events"""
        if self.selection_mode:
            self.selection_start = (event.x, event.y)
            
        elif self.defining_section:
            # Add point for section definition
            self.section_points.append((event.x, event.y))
            self.status_label.config(text=f"Section points: {len(self.section_points)} (right-click to finish)")
            
    def on_mouse_drag(self, event):
        """Handle mouse drag events"""
        if self.selection_mode and hasattr(self, 'selection_start'):
            # Update current selection rectangle
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            self.current_selection = (x, y, w, h)
            self.display_frame()
            
    def on_mouse_release(self, event):
        """Handle mouse release events"""
        if self.selection_mode and hasattr(self, 'selection_start') and self.current_selection:
            # Finalize person selection
            bbox = self.current_selection
            person_id = self.tracker.add_person(self.current_frame, bbox)
            
            if person_id > 0:
                self.person_paths[person_id] = []
                self.status_label.config(text=f"Tracking Person {person_id}")
                messagebox.showinfo("Success", f"Started tracking Person {person_id}")
            else:
                messagebox.showerror("Error", "Failed to initialize tracker")
                
            self.selection_mode = False
            self.current_selection = None
            delattr(self, 'selection_start')
            
    def start_section_definition(self):
        """Start section definition mode"""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "Please load a video first")
            return
            
        section_name = tk.simpledialog.askstring("Section Name", "Enter section name:")
        if section_name:
            self.section_name = section_name
            self.defining_section = True
            self.section_points = []
            self.status_label.config(text=f"Click to define points for section '{section_name}' (right-click to finish)")
            
    def toggle_playback(self):
        """Toggle video playback"""
        if self.current_video is None:
            messagebox.showwarning("Warning", "Please load a video first")
            return
            
        self.playing = not self.playing
        
        if self.playing:
            self.play_video()
            
    def play_video(self):
        """Play video and update tracking"""
        if not self.playing or self.current_video is None:
            return
            
        ret, frame = self.current_video.read()
        if ret:
            self.current_frame = frame
            self.frame_index += 1
            
            # Update trackers
            if self.tracker.get_active_trackers():
                tracking_results = self.tracker.update_trackers(frame)
                
                # Update paths
                for person_id, result in tracking_results.items():
                    if result['success']:
                        center = result['center']
                        if person_id not in self.person_paths:
                            self.person_paths[person_id] = []
                        self.person_paths[person_id].append((center[0], center[1], self.frame_index))
                        
                        # Check section visits
                        self.check_section_visits(person_id, center)
            
            self.display_frame()
            
            # Schedule next frame
            delay = int(1000 / self.fps)
            self.root.after(delay, self.play_video)
        else:
            # End of video
            self.playing = False
            self.status_label.config(text="Video playback finished")
            
    def check_section_visits(self, person_id: int, position: Tuple[int, int]):
        """Check if person is visiting any store sections"""
        x, y = position
        
        for section_name, points in self.store_sections.items():
            if len(points) > 2:
                # Simple point-in-polygon check
                inside = self.point_in_polygon(x, y, points)
                
                # Track visits (simplified - just log when person is in section)
                if inside:
                    if person_id not in self.section_visits:
                        self.section_visits[person_id] = []
                    
                    # Add visit if not already recorded for this frame range
                    last_visit = None
                    if self.section_visits[person_id]:
                        last_visit = self.section_visits[person_id][-1]
                    
                    if not last_visit or last_visit[0] != section_name:
                        self.section_visits[person_id].append((section_name, self.frame_index, self.frame_index))
                        
    def point_in_polygon(self, x: int, y: int, polygon: List[Tuple[int, int]]) -> bool:
        """Check if point is inside polygon using ray casting"""
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
        
    def export_simple_report(self):
        """Export a simple text report"""
        if not self.person_paths and not self.section_visits:
            messagebox.showwarning("Warning", "No tracking data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Footstep Tracking Report\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    # Person paths
                    f.write("Person Movement Paths:\n")
                    f.write("-" * 30 + "\n")
                    for person_id, path in self.person_paths.items():
                        f.write(f"Person {person_id}: {len(path)} tracking points\n")
                        if path:
                            start_frame = path[0][2]
                            end_frame = path[-1][2]
                            duration = (end_frame - start_frame) / self.fps
                            f.write(f"  Duration: {duration:.1f} seconds\n")
                            f.write(f"  Start: ({path[0][0]}, {path[0][1]})\n")
                            f.write(f"  End: ({path[-1][0]}, {path[-1][1]})\n")
                        f.write("\n")
                    
                    # Section visits
                    f.write("Section Visits:\n")
                    f.write("-" * 30 + "\n")
                    for person_id, visits in self.section_visits.items():
                        f.write(f"Person {person_id}:\n")
                        for section, entry_frame, exit_frame in visits:
                            entry_time = entry_frame / self.fps
                            f.write(f"  {section} at {entry_time:.1f}s\n")
                        f.write("\n")
                    
                    # Store sections
                    f.write("Defined Store Sections:\n")
                    f.write("-" * 30 + "\n")
                    for section_name, points in self.store_sections.items():
                        f.write(f"{section_name}: {len(points)} boundary points\n")
                    
                messagebox.showinfo("Success", f"Report exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
                
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing"""
        if self.current_video:
            self.current_video.release()
        self.root.destroy()

if __name__ == "__main__":
    try:
        # Import required dependencies
        import tkinter.simpledialog
        from PIL import Image, ImageTk
        
        app = SimplifiedFootstepTracker()
        app.run()
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install pillow")
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
