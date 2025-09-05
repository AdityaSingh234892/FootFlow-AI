"""
OpenCV Human Footstep Tracking and Store Section Analysis System - Clean Version
Main application entry point
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
from PIL import Image, ImageTk

# Import our custom modules
try:
    from tracking.person_tracker import PersonTracker
    from tracking.path_visualizer import PathVisualizer
    from store.section_manager import SectionManager
    from store.visit_analyzer import VisitAnalyzer
    from ui.control_panel import ControlPanel
    from reporting.report_generator import ReportGenerator
    from utils.config_manager import ConfigManager
except ImportError as e:
    print(f"Import error: {e}")
    # Create placeholder classes if imports fail
    class PersonTracker:
        def __init__(self): pass
    class PathVisualizer:
        def __init__(self): pass
        def get_person_color(self, pid): return (255, 0, 0)
        def draw_paths(self, frame, paths): return frame
    class SectionManager:
        def __init__(self): 
            self.sections = {}
        def get_sections_at_point(self, x, y): return []
        def draw_sections(self, frame): return frame
        def define_sections_interactive(self, frame): pass
        def load_layout(self, path): pass
    class VisitAnalyzer:
        def __init__(self): pass
        def record_visit(self, pid, section, frame, x, y): pass
    class ControlPanel:
        def __init__(self, parent, callbacks): pass
    class ReportGenerator:
        def __init__(self): pass
        def generate_comprehensive_report(self, paths, visits, sections, output): pass
    class ConfigManager:
        def __init__(self): pass

class FootstepTrackingSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Store Footstep Tracking & Analysis System")
        self.root.geometry("1400x900")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.person_tracker = PersonTracker()
        self.path_visualizer = PathVisualizer()
        self.section_manager = SectionManager()
        self.visit_analyzer = VisitAnalyzer()
        self.report_generator = ReportGenerator()
        
        # Video and tracking state
        self.video_cap = None
        self.current_frame = None
        self.is_playing = False
        self.current_frame_number = 0
        self.total_frames = 0
        self.fps = 30
        
        # Tracking data
        self.tracked_persons = {}
        self.tracking_paths = {}
        self.section_visits = {}
        self.show_sections = False
        self.selecting_person = False
        
        # UI setup
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main frames
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Video display frame
        self.video_frame = ttk.LabelFrame(self.main_frame, text="Video Display", padding=5)
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Control panel frame
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=5)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Create video canvas
        self.video_canvas = tk.Canvas(self.video_frame, bg='black', width=800, height=600)
        self.video_canvas.pack(expand=True, fill=tk.BOTH)
        self.video_canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Setup control panel
        self.setup_control_panel()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_control_panel(self):
        """Setup the control panel with all buttons and options"""
        # File operations
        file_frame = ttk.LabelFrame(self.control_frame, text="File Operations", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(file_frame, text="Load Video", command=self.load_video).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Load Store Layout", command=self.load_store_layout).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Save Session", command=self.save_session).pack(fill=tk.X, pady=2)
        
        # Video controls
        video_control_frame = ttk.LabelFrame(self.control_frame, text="Video Controls", padding=5)
        video_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(video_control_frame, text="Play/Pause", command=self.toggle_playback).pack(fill=tk.X, pady=2)
        ttk.Button(video_control_frame, text="Stop", command=self.stop_playback).pack(fill=tk.X, pady=2)
        
        # Frame navigation
        nav_frame = ttk.Frame(video_control_frame)
        nav_frame.pack(fill=tk.X, pady=2)
        ttk.Button(nav_frame, text="<<", command=self.prev_frame, width=5).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text=">>", command=self.next_frame, width=5).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(video_control_frame, from_=0, to=100, 
                                     orient=tk.HORIZONTAL, variable=self.progress_var,
                                     command=self.seek_frame)
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        # Tracking controls
        tracking_frame = ttk.LabelFrame(self.control_frame, text="Tracking Controls", padding=5)
        tracking_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(tracking_frame, text="Select Person", command=self.select_person_mode).pack(fill=tk.X, pady=2)
        ttk.Button(tracking_frame, text="Clear All Tracks", command=self.clear_all_tracks).pack(fill=tk.X, pady=2)
        
        # Tracking algorithm selection
        ttk.Label(tracking_frame, text="Tracking Algorithm:").pack(anchor=tk.W)
        self.tracker_var = tk.StringVar(value="CSRT")
        tracker_combo = ttk.Combobox(tracking_frame, textvariable=self.tracker_var, 
                                   values=["CSRT", "KCF", "MOSSE"], state="readonly")
        tracker_combo.pack(fill=tk.X, pady=2)
        
        # Active trackers list
        ttk.Label(tracking_frame, text="Active Trackers:").pack(anchor=tk.W, pady=(10, 0))
        self.tracker_listbox = tk.Listbox(tracking_frame, height=6)
        self.tracker_listbox.pack(fill=tk.X, pady=2)
        
        # Section management
        section_frame = ttk.LabelFrame(self.control_frame, text="Store Sections", padding=5)
        section_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(section_frame, text="Define Sections", command=self.define_sections).pack(fill=tk.X, pady=2)
        ttk.Button(section_frame, text="Show/Hide Sections", command=self.toggle_sections).pack(fill=tk.X, pady=2)
        
        # Analysis and reporting
        analysis_frame = ttk.LabelFrame(self.control_frame, text="Analysis & Reports", padding=5)
        analysis_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(analysis_frame, text="Generate Report", command=self.generate_report).pack(fill=tk.X, pady=2)
        ttk.Button(analysis_frame, text="Export Data", command=self.export_data).pack(fill=tk.X, pady=2)
        ttk.Button(analysis_frame, text="Show Analytics", command=self.show_analytics).pack(fill=tk.X, pady=2)
        
    def load_video(self):
        """Load video file for tracking"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.video_cap = cv2.VideoCapture(file_path)
            if not self.video_cap.isOpened():
                messagebox.showerror("Error", "Failed to open video file")
                return
                
            self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.video_cap.get(cv2.CAP_PROP_FPS) or 30
            
            # Reset tracking data
            self.reset_tracking_data()
            
            # Load first frame
            self.load_frame(0)
            self.update_status(f"Loaded video: {os.path.basename(file_path)} ({self.total_frames} frames)")
            
    def load_frame(self, frame_number):
        """Load and display specific frame"""
        if not self.video_cap:
            return
            
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.video_cap.read()
        
        if ret:
            self.current_frame = frame.copy()
            self.current_frame_number = frame_number
            
            # Update tracking
            self.update_tracking()
            
            # Draw visualizations
            display_frame = self.draw_visualizations(frame.copy())
            
            # Display frame
            self.display_frame(display_frame)
            
            # Update progress
            if self.total_frames > 0:
                progress = (frame_number / self.total_frames) * 100
                self.progress_var.set(progress)
                
    def update_tracking(self):
        """Update all active trackers"""
        if self.current_frame is None:
            return
            
        for person_id, tracker_data in list(self.tracked_persons.items()):
            tracker = tracker_data['tracker']
            success, bbox = tracker.update(self.current_frame)
            
            if success:
                x, y, w, h = bbox
                center_x = int(x + w/2)
                center_y = int(y + h/2)
                
                # Update path
                if person_id not in self.tracking_paths:
                    self.tracking_paths[person_id] = []
                    
                self.tracking_paths[person_id].append({
                    'frame': self.current_frame_number,
                    'position': (center_x, center_y),
                    'bbox': bbox,
                    'timestamp': self.current_frame_number / self.fps
                })
                
                # Check section visits
                self.check_section_visits(person_id, center_x, center_y)
                
            else:
                # Tracking lost - could implement re-identification here
                self.update_status(f"Lost tracking for Person {person_id}")
                
    def check_section_visits(self, person_id, x, y):
        """Check if person has entered/exited store sections"""
        current_sections = self.section_manager.get_sections_at_point(x, y)
        
        if person_id not in self.section_visits:
            self.section_visits[person_id] = []
            
        # Record section entries/exits
        for section in current_sections:
            self.visit_analyzer.record_visit(person_id, section, 
                                           self.current_frame_number, x, y)
                                           
    def draw_visualizations(self, frame):
        """Draw all visualizations on the frame"""
        # Draw section boundaries
        if self.show_sections:
            frame = self.section_manager.draw_sections(frame)
            
        # Draw tracking paths
        frame = self.path_visualizer.draw_paths(frame, self.tracking_paths)
        
        # Draw current bounding boxes
        for person_id, tracker_data in self.tracked_persons.items():
            if person_id in self.tracking_paths and self.tracking_paths[person_id]:
                last_point = self.tracking_paths[person_id][-1]
                bbox = last_point['bbox']
                color = self.path_visualizer.get_person_color(person_id)
                
                x, y, w, h = bbox
                cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), color, 2)
                cv2.putText(frame, f"Person {person_id}", (int(x), int(y-10)),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                          
        return frame
        
    def display_frame(self, frame):
        """Display frame on canvas"""
        if frame is None:
            return
            
        # Resize frame to fit canvas
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            frame_height, frame_width = frame.shape[:2]
            
            # Calculate scale to fit canvas while maintaining aspect ratio
            scale_x = canvas_width / frame_width
            scale_y = canvas_height / frame_height
            scale = min(scale_x, scale_y)
            
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB and then to PhotoImage
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image)
            
            # Clear canvas and display image
            self.video_canvas.delete("all")
            self.video_canvas.create_image(canvas_width//2, canvas_height//2, 
                                         image=photo, anchor=tk.CENTER)
            self.video_canvas.image = photo  # Keep a reference
            
    def on_canvas_click(self, event):
        """Handle canvas click for person selection"""
        if self.selecting_person:
            self.select_person_at_point(event.x, event.y)
            
    def select_person_mode(self):
        """Enter person selection mode"""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "Please load a video first")
            return
            
        self.selecting_person = True
        self.update_status("Click on a person in the video to start tracking")
        
        # Use selectROI for manual selection
        if self.current_frame is not None:
            bbox = cv2.selectROI("Select Person", self.current_frame, False)
            cv2.destroyWindow("Select Person")
            
            if bbox[2] > 0 and bbox[3] > 0:  # Valid selection
                self.start_tracking_person(bbox)
                
        self.selecting_person = False
        
    def start_tracking_person(self, bbox):
        """Start tracking a person with given bounding box"""
        person_id = len(self.tracked_persons) + 1
        
        # Create tracker
        tracker_type = self.tracker_var.get()
        try:
            if tracker_type == "CSRT":
                tracker = cv2.TrackerCSRT_create()
            elif tracker_type == "KCF":
                tracker = cv2.TrackerKCF_create()
            else:  # MOSSE
                try:
                    tracker = cv2.legacy.TrackerMOSSE_create()
                except AttributeError:
                    messagebox.showwarning("Warning", "MOSSE tracker not available, using KCF instead")
                    tracker = cv2.TrackerKCF_create()
        except AttributeError as e:
            messagebox.showerror("Error", f"Tracking not available: {e}\nPlease install opencv-contrib-python")
            return
            
        # Initialize tracker
        success = tracker.init(self.current_frame, bbox)
        
        if success:
            self.tracked_persons[person_id] = {
                'tracker': tracker,
                'start_frame': self.current_frame_number,
                'color': self.path_visualizer.get_person_color(person_id)
            }
            
            # Update tracker list
            self.tracker_listbox.insert(tk.END, f"Person {person_id}")
            
            self.update_status(f"Started tracking Person {person_id}")
        else:
            messagebox.showerror("Error", "Failed to initialize tracker")
            
    def toggle_playback(self):
        """Toggle video playback"""
        if not self.video_cap:
            messagebox.showwarning("Warning", "Please load a video first")
            return
            
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_video()
        else:
            self.update_status("Paused")
            
    def play_video(self):
        """Play video with tracking"""
        if not self.is_playing or not self.video_cap:
            return
            
        if self.current_frame_number < self.total_frames - 1:
            self.load_frame(self.current_frame_number + 1)
            self.root.after(int(1000 / self.fps), self.play_video)
        else:
            self.is_playing = False
            self.update_status("Video completed")
            
    def stop_playback(self):
        """Stop video playback"""
        self.is_playing = False
        self.load_frame(0)
        self.update_status("Stopped")
        
    def prev_frame(self):
        """Go to previous frame"""
        if self.current_frame_number > 0:
            self.load_frame(self.current_frame_number - 1)
            
    def next_frame(self):
        """Go to next frame"""
        if self.current_frame_number < self.total_frames - 1:
            self.load_frame(self.current_frame_number + 1)
            
    def seek_frame(self, value):
        """Seek to specific frame based on progress bar"""
        if self.total_frames > 0:
            frame_number = int((float(value) / 100) * self.total_frames)
            self.load_frame(frame_number)
            
    def clear_all_tracks(self):
        """Clear all tracking data"""
        self.reset_tracking_data()
        self.tracker_listbox.delete(0, tk.END)
        self.update_status("Cleared all tracks")
        
    def reset_tracking_data(self):
        """Reset all tracking data"""
        self.tracked_persons = {}
        self.tracking_paths = {}
        self.section_visits = {}
        
    def load_store_layout(self):
        """Load store layout configuration"""
        file_path = filedialog.askopenfilename(
            title="Select Store Layout File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.section_manager.load_layout(file_path)
            self.update_status(f"Loaded store layout: {os.path.basename(file_path)}")
            
    def define_sections(self):
        """Open section definition dialog"""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "Please load a video first")
            return
            
        # This would open a dialog for defining store sections
        self.section_manager.define_sections_interactive(self.current_frame)
        
    def toggle_sections(self):
        """Toggle section visibility"""
        self.show_sections = not self.show_sections
        if self.current_frame is not None:
            display_frame = self.draw_visualizations(self.current_frame.copy())
            self.display_frame(display_frame)
            
    def generate_report(self):
        """Generate comprehensive tracking report"""
        if not self.tracking_paths:
            messagebox.showwarning("Warning", "No tracking data available")
            return
            
        output_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if output_path:
            self.report_generator.generate_comprehensive_report(
                self.tracking_paths,
                self.section_visits,
                self.section_manager.sections,
                output_path
            )
            self.update_status(f"Report saved: {output_path}")
            
    def export_data(self):
        """Export tracking data"""
        if not self.tracking_paths:
            messagebox.showwarning("Warning", "No tracking data available")
            return
            
        output_path = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if output_path:
            # Export data logic here
            self.export_tracking_data(output_path)
            self.update_status(f"Data exported: {output_path}")
            
    def export_tracking_data(self, file_path):
        """Export tracking data to file"""
        data = {
            'tracking_paths': self.tracking_paths,
            'section_visits': self.section_visits,
            'sections': self.section_manager.sections,
            'video_info': {
                'total_frames': self.total_frames,
                'fps': self.fps,
                'export_timestamp': datetime.now().isoformat()
            }
        }
        
        if file_path.endswith('.json'):
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
    def show_analytics(self):
        """Show analytics dashboard"""
        if not self.tracking_paths:
            messagebox.showwarning("Warning", "No tracking data available")
            return
            
        # Open analytics window
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Store Analytics Dashboard")
        analytics_window.geometry("800x600")
        
        # Analytics implementation here
        self.create_analytics_dashboard(analytics_window)
        
    def create_analytics_dashboard(self, parent):
        """Create analytics dashboard"""
        # This would create various charts and analytics
        ttk.Label(parent, text="Analytics Dashboard", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Add analytics widgets here
        # - Path analysis
        # - Time spent in sections
        # - Popular routes
        # - Heat maps
        
    def save_session(self):
        """Save current tracking session"""
        if not self.tracking_paths:
            messagebox.showwarning("Warning", "No tracking data to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Session",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.export_tracking_data(file_path)
            self.update_status(f"Session saved: {file_path}")
            
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()
        
        # Cleanup
        if self.video_cap:
            self.video_cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = FootstepTrackingSystem()
    app.run()
