"""
Complete Working OpenCV Footstep Tracking System
Single file - no external dependencies except standard libraries
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
import threading
import time

class SimpleTracker:
    """Basic template matching tracker that works without opencv-contrib"""
    
    def __init__(self):
        self.template = None
        self.bbox = None
        self.confidence_threshold = 0.6
        
    def init(self, frame, bbox):
        """Initialize tracker with template"""
        try:
            x, y, w, h = [int(v) for v in bbox]
            if w > 10 and h > 10 and x >= 0 and y >= 0:
                self.template = frame[y:y+h, x:x+w]
                self.bbox = (x, y, w, h)
                return True
        except:
            pass
        return False
        
    def update(self, frame):
        """Update tracker position using template matching"""
        if self.template is None or self.template.size == 0:
            return False, self.bbox
            
        try:
            # Convert to grayscale for template matching
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > self.confidence_threshold:
                x, y = max_loc
                w, h = self.template.shape[1], self.template.shape[0]
                self.bbox = (x, y, w, h)
                return True, self.bbox
            else:
                return False, self.bbox
                
        except Exception as e:
            print(f"Tracking error: {e}")
            return False, self.bbox

class WorkingFootstepTracker:
    """Complete working footstep tracking system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Working Footstep Tracking System")
        self.root.geometry("1200x800")
        
        # Video and tracking state
        self.video_cap = None
        self.current_frame = None
        self.is_playing = False
        self.current_frame_number = 0
        self.total_frames = 0
        self.fps = 30
        
        # Tracking data
        self.trackers = {}
        self.person_paths = {}
        self.next_person_id = 1
        self.tracking_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
        ]
        
        # Store sections
        self.store_sections = {}
        self.section_visits = {}
        self.show_sections = True
        
        # Selection state
        self.selecting_person = False
        self.selection_start = None
        self.current_selection = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - video display
        video_frame = ttk.LabelFrame(main_frame, text="Video Display")
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video canvas
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=640, height=480)
        self.video_canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Bind mouse events for person selection
        self.video_canvas.bind("<Button-1>", self.on_mouse_click)
        self.video_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.video_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Right side - controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File operations
        file_frame = ttk.LabelFrame(control_frame, text="File Operations")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(file_frame, text="Load Video", command=self.load_video).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Save Report", command=self.save_report).pack(fill=tk.X, pady=2)
        
        # Video controls
        video_control_frame = ttk.LabelFrame(control_frame, text="Video Controls")
        video_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(video_control_frame, text="Play/Pause", command=self.toggle_playback).pack(fill=tk.X, pady=2)
        ttk.Button(video_control_frame, text="Stop", command=self.stop_video).pack(fill=tk.X, pady=2)
        
        # Frame navigation
        nav_frame = ttk.Frame(video_control_frame)
        nav_frame.pack(fill=tk.X, pady=2)
        ttk.Button(nav_frame, text="◀◀", command=self.prev_frame, width=6).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="▶▶", command=self.next_frame, width=6).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(video_control_frame, from_=0, to=100, 
                                     orient=tk.HORIZONTAL, variable=self.progress_var,
                                     command=self.seek_video)
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        # Tracking controls
        tracking_frame = ttk.LabelFrame(control_frame, text="Person Tracking")
        tracking_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(tracking_frame, text="Select Person to Track", 
                  command=self.start_person_selection).pack(fill=tk.X, pady=2)
        ttk.Button(tracking_frame, text="Clear All Tracks", 
                  command=self.clear_all_tracks).pack(fill=tk.X, pady=2)
        
        # Active trackers list
        ttk.Label(tracking_frame, text="Active Trackers:").pack(anchor=tk.W)
        self.tracker_listbox = tk.Listbox(tracking_frame, height=4)
        self.tracker_listbox.pack(fill=tk.X, pady=2)
        
        # Section management
        section_frame = ttk.LabelFrame(control_frame, text="Store Sections")
        section_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(section_frame, text="Define Section", 
                  command=self.define_section).pack(fill=tk.X, pady=2)
        ttk.Button(section_frame, text="Toggle Section Display", 
                  command=self.toggle_section_display).pack(fill=tk.X, pady=2)
        
        # Sections list
        ttk.Label(section_frame, text="Defined Sections:").pack(anchor=tk.W)
        self.section_listbox = tk.Listbox(section_frame, height=3)
        self.section_listbox.pack(fill=tk.X, pady=2)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Load a video to begin")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
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
                if self.video_cap:
                    self.video_cap.release()
                    
                self.video_cap = cv2.VideoCapture(file_path)
                
                if not self.video_cap.isOpened():
                    messagebox.showerror("Error", "Could not open video file")
                    return
                
                self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.video_cap.get(cv2.CAP_PROP_FPS) or 30
                
                # Reset everything
                self.current_frame_number = 0
                self.is_playing = False
                self.clear_all_tracks()
                
                # Load first frame
                self.load_frame(0)
                
                self.status_var.set(f"Loaded: {os.path.basename(file_path)} ({self.total_frames} frames)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load video: {str(e)}")
                
    def load_frame(self, frame_number):
        """Load and display specific frame"""
        if not self.video_cap:
            return
            
        frame_number = max(0, min(frame_number, self.total_frames - 1))
        
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.video_cap.read()
        
        if ret:
            self.current_frame = frame.copy()
            self.current_frame_number = frame_number
            
            # Update all trackers
            self.update_trackers()
            
            # Display frame with overlays
            self.display_frame()
            
            # Update progress bar
            if self.total_frames > 0:
                progress = (frame_number / self.total_frames) * 100
                self.progress_var.set(progress)
                
    def update_trackers(self):
        """Update all active trackers"""
        if self.current_frame is None:
            return
            
        for person_id, tracker_data in list(self.trackers.items()):
            tracker = tracker_data['tracker']
            success, bbox = tracker.update(self.current_frame)
            
            if success:
                x, y, w, h = bbox
                center_x = int(x + w/2)
                center_y = int(y + h/2)
                
                # Update path
                if person_id not in self.person_paths:
                    self.person_paths[person_id] = []
                    
                self.person_paths[person_id].append({
                    'frame': self.current_frame_number,
                    'x': center_x,
                    'y': center_y,
                    'timestamp': self.current_frame_number / self.fps
                })
                
                # Update tracker data
                tracker_data['bbox'] = bbox
                tracker_data['last_seen'] = self.current_frame_number
                
                # Check section visits
                self.check_section_visits(person_id, center_x, center_y)
                
            else:
                # Mark as lost
                tracker_data['lost_frames'] = tracker_data.get('lost_frames', 0) + 1
                
                # Remove if lost for too long
                if tracker_data['lost_frames'] > 30:
                    self.remove_tracker(person_id)
                    
    def check_section_visits(self, person_id, x, y):
        """Check if person is in any defined sections"""
        for section_name, points in self.store_sections.items():
            if len(points) > 2:
                inside = self.point_in_polygon(x, y, points)
                
                if inside:
                    # Record visit
                    if person_id not in self.section_visits:
                        self.section_visits[person_id] = {}
                    if section_name not in self.section_visits[person_id]:
                        self.section_visits[person_id][section_name] = []
                    
                    # Add visit entry
                    self.section_visits[person_id][section_name].append({
                        'frame': self.current_frame_number,
                        'timestamp': self.current_frame_number / self.fps
                    })
                    
    def point_in_polygon(self, x, y, polygon):
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
                    
    def display_frame(self):
        """Display current frame with all overlays"""
        if self.current_frame is None:
            return
            
        # Create display frame
        display_frame = self.current_frame.copy()
        
        # Draw store sections
        if self.show_sections:
            for section_name, points in self.store_sections.items():
                if len(points) > 2:
                    pts = np.array(points, np.int32)
                    cv2.polylines(display_frame, [pts], True, (0, 255, 255), 2)
                    
                    # Add section label
                    if points:
                        cv2.putText(display_frame, section_name, points[0], 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw tracking paths and current positions
        for person_id, path in self.person_paths.items():
            if len(path) > 1:
                color = self.tracking_colors[person_id % len(self.tracking_colors)]
                
                # Draw path
                for i in range(1, len(path)):
                    pt1 = (path[i-1]['x'], path[i-1]['y'])
                    pt2 = (path[i]['x'], path[i]['y'])
                    cv2.line(display_frame, pt1, pt2, color, 2)
                
                # Draw current position if tracker is active
                if person_id in self.trackers:
                    tracker_data = self.trackers[person_id]
                    if 'bbox' in tracker_data:
                        x, y, w, h = tracker_data['bbox']
                        cv2.rectangle(display_frame, (int(x), int(y)), 
                                    (int(x+w), int(y+h)), color, 2)
                        cv2.putText(display_frame, f"Person {person_id}", 
                                  (int(x), int(y-10)), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.6, color, 2)
        
        # Draw current selection if selecting
        if self.current_selection:
            x, y, w, h = self.current_selection
            cv2.rectangle(display_frame, (int(x), int(y)), 
                         (int(x+w), int(y+h)), (255, 255, 255), 2)
        
        # Convert and display
        self.show_frame_on_canvas(display_frame)
        
    def show_frame_on_canvas(self, frame):
        """Display frame on the canvas"""
        # Get canvas dimensions
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Resize frame to fit canvas
            h, w = frame.shape[:2]
            scale = min(canvas_width / w, canvas_height / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            resized_frame = cv2.resize(frame, (new_w, new_h))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image)
            
            # Display on canvas
            self.video_canvas.delete("all")
            x = (canvas_width - new_w) // 2
            y = (canvas_height - new_h) // 2
            self.video_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.video_canvas.image = photo  # Keep reference
            
            # Store scale for mouse coordinate conversion
            self.scale_factor = scale
            self.offset_x = x
            self.offset_y = y
            
    def on_mouse_click(self, event):
        """Handle mouse click for person selection"""
        if self.selecting_person and self.current_frame is not None:
            # Convert canvas coordinates to frame coordinates
            frame_x = int((event.x - self.offset_x) / self.scale_factor)
            frame_y = int((event.y - self.offset_y) / self.scale_factor)
            
            self.selection_start = (frame_x, frame_y)
            
    def on_mouse_drag(self, event):
        """Handle mouse drag for selection rectangle"""
        if self.selecting_person and self.selection_start:
            # Convert canvas coordinates to frame coordinates
            frame_x = int((event.x - self.offset_x) / self.scale_factor)
            frame_y = int((event.y - self.offset_y) / self.scale_factor)
            
            x1, y1 = self.selection_start
            x2, y2 = frame_x, frame_y
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            self.current_selection = (x, y, w, h)
            self.display_frame()
            
    def on_mouse_release(self, event):
        """Handle mouse release to finalize selection"""
        if self.selecting_person and self.current_selection:
            x, y, w, h = self.current_selection
            
            if w > 20 and h > 20:  # Minimum size
                self.create_tracker(self.current_selection)
            else:
                messagebox.showwarning("Selection Too Small", 
                                     "Please select a larger area around the person")
            
            self.current_selection = None
            self.selecting_person = False
            self.status_var.set("Person selection completed")
            
    def start_person_selection(self):
        """Start person selection mode"""
        if self.current_frame is None:
            messagebox.showwarning("No Video", "Please load a video first")
            return
            
        self.selecting_person = True
        self.status_var.set("Click and drag to select a person to track")
        
    def create_tracker(self, bbox):
        """Create new tracker for selected person"""
        person_id = self.next_person_id
        self.next_person_id += 1
        
        # Create tracker
        tracker = SimpleTracker()
        success = tracker.init(self.current_frame, bbox)
        
        if success:
            self.trackers[person_id] = {
                'tracker': tracker,
                'bbox': bbox,
                'start_frame': self.current_frame_number,
                'last_seen': self.current_frame_number,
                'lost_frames': 0
            }
            
            # Initialize path
            x, y, w, h = bbox
            center_x = int(x + w/2)
            center_y = int(y + h/2)
            
            self.person_paths[person_id] = [{
                'frame': self.current_frame_number,
                'x': center_x,
                'y': center_y,
                'timestamp': self.current_frame_number / self.fps
            }]
            
            # Update UI
            self.tracker_listbox.insert(tk.END, f"Person {person_id}")
            self.status_var.set(f"Started tracking Person {person_id}")
            
        else:
            messagebox.showerror("Tracking Error", "Failed to initialize tracker")
            
    def remove_tracker(self, person_id):
        """Remove tracker"""
        if person_id in self.trackers:
            del self.trackers[person_id]
            
            # Update listbox
            for i in range(self.tracker_listbox.size()):
                if self.tracker_listbox.get(i) == f"Person {person_id}":
                    self.tracker_listbox.delete(i)
                    break
                    
    def clear_all_tracks(self):
        """Clear all tracking data"""
        self.trackers.clear()
        self.person_paths.clear()
        self.section_visits.clear()
        self.tracker_listbox.delete(0, tk.END)
        self.next_person_id = 1
        self.status_var.set("All tracks cleared")
        
    def toggle_playback(self):
        """Toggle video playback"""
        if not self.video_cap:
            messagebox.showwarning("No Video", "Please load a video first")
            return
            
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_video()
        else:
            self.status_var.set("Paused")
            
    def play_video(self):
        """Play video continuously"""
        if self.is_playing and self.video_cap:
            if self.current_frame_number < self.total_frames - 1:
                self.load_frame(self.current_frame_number + 1)
                self.root.after(int(1000 / self.fps), self.play_video)
            else:
                self.is_playing = False
                self.status_var.set("Video playback completed")
                
    def stop_video(self):
        """Stop video playback"""
        self.is_playing = False
        self.load_frame(0)
        self.status_var.set("Video stopped")
        
    def prev_frame(self):
        """Go to previous frame"""
        if self.current_frame_number > 0:
            self.load_frame(self.current_frame_number - 1)
            
    def next_frame(self):
        """Go to next frame"""
        if self.current_frame_number < self.total_frames - 1:
            self.load_frame(self.current_frame_number + 1)
            
    def seek_video(self, value):
        """Seek to specific position"""
        if self.total_frames > 0:
            frame_number = int((float(value) / 100) * self.total_frames)
            self.load_frame(frame_number)
            
    def define_section(self):
        """Define a store section"""
        if self.current_frame is None:
            messagebox.showwarning("No Video", "Please load a video first")
            return
            
        section_name = tk.simpledialog.askstring("Section Name", "Enter section name:")
        if section_name:
            # Simple section definition - you can enhance this
            messagebox.showinfo("Section Definition", 
                               f"Section '{section_name}' will be defined.\n"
                               f"This is a simplified version - you can enhance it to draw polygons.")
            
            # For now, create a simple rectangular section
            h, w = self.current_frame.shape[:2]
            self.store_sections[section_name] = [
                (w//4, h//4), (3*w//4, h//4), (3*w//4, 3*h//4), (w//4, 3*h//4)
            ]
            
            self.section_listbox.insert(tk.END, section_name)
            
    def toggle_section_display(self):
        """Toggle section display"""
        self.show_sections = not self.show_sections
        if self.current_frame is not None:
            self.display_frame()
            
    def save_report(self):
        """Save tracking report"""
        if not self.person_paths:
            messagebox.showwarning("No Data", "No tracking data to save")
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
                    
                    # Person tracking summary
                    f.write("Tracked Persons:\n")
                    f.write("-" * 30 + "\n")
                    for person_id, path in self.person_paths.items():
                        f.write(f"Person {person_id}:\n")
                        f.write(f"  Total tracking points: {len(path)}\n")
                        if path:
                            duration = path[-1]['timestamp'] - path[0]['timestamp']
                            f.write(f"  Duration: {duration:.1f} seconds\n")
                            f.write(f"  Start position: ({path[0]['x']}, {path[0]['y']})\n")
                            f.write(f"  End position: ({path[-1]['x']}, {path[-1]['y']})\n")
                        f.write("\n")
                    
                    # Section visits
                    if self.section_visits:
                        f.write("Section Visits:\n")
                        f.write("-" * 30 + "\n")
                        for person_id, sections in self.section_visits.items():
                            f.write(f"Person {person_id}:\n")
                            for section_name, visits in sections.items():
                                f.write(f"  {section_name}: {len(visits)} visits\n")
                            f.write("\n")
                    
                    # Store sections
                    if self.store_sections:
                        f.write("Defined Store Sections:\n")
                        f.write("-" * 30 + "\n")
                        for section_name in self.store_sections:
                            f.write(f"  {section_name}\n")
                
                messagebox.showinfo("Success", f"Report saved to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")
                
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing"""
        if self.video_cap:
            self.video_cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()

# Import simpledialog
import tkinter.simpledialog

if __name__ == "__main__":
    try:
        app = WorkingFootstepTracker()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
