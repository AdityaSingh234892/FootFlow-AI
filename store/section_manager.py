"""
Section Manager Module
Handles store layout, section definitions, and boundary management
"""

import cv2
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import tkinter as tk
from tkinter import ttk, messagebox

class SectionManager:
    def __init__(self):
        self.sections = {}
        self.section_colors = {
            'Electronics': (255, 100, 100),
            'Groceries': (100, 255, 100),
            'Clothing': (100, 100, 255),
            'Pharmacy': (255, 255, 100),
            'Home & Garden': (255, 100, 255),
            'Sports': (100, 255, 255),
            'Automotive': (200, 150, 100),
            'Books': (150, 200, 100),
            'Toys': (100, 150, 200),
            'Cosmetics': (200, 100, 150),
            'Food Court': (150, 100, 200),
            'Checkout': (255, 200, 100),
            'Entrance': (100, 200, 255),
            'Exit': (200, 255, 100),
            'Restroom': (128, 128, 128),
        }
        
    def define_section(self, name: str, polygon_points: List[Tuple[int, int]], 
                      category: str = "General", shelf_info: Optional[Dict] = None):
        """Define a new store section"""
        self.sections[name] = {
            'polygon': polygon_points,
            'category': category,
            'color': self._get_section_color(category),
            'shelf_info': shelf_info or {},
            'subsections': {}
        }
        
    def _get_section_color(self, category: str) -> Tuple[int, int, int]:
        """Get color for section category"""
        if category in self.section_colors:
            return self.section_colors[category]
        else:
            # Generate a random color
            import random
            return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            
    def load_layout(self, file_path: str):
        """Load store layout from JSON file"""
        try:
            with open(file_path, 'r') as f:
                layout_data = json.load(f)
                
            self.sections = {}
            for section_name, section_data in layout_data.get('sections', {}).items():
                self.sections[section_name] = {
                    'polygon': section_data['polygon'],
                    'category': section_data.get('category', 'General'),
                    'color': tuple(section_data.get('color', [100, 100, 100])),
                    'shelf_info': section_data.get('shelf_info', {}),
                    'subsections': section_data.get('subsections', {})
                }
                
        except Exception as e:
            print(f"Error loading layout: {e}")
            
    def save_layout(self, file_path: str):
        """Save current layout to JSON file"""
        try:
            layout_data = {
                'sections': {}
            }
            
            for section_name, section_data in self.sections.items():
                layout_data['sections'][section_name] = {
                    'polygon': section_data['polygon'],
                    'category': section_data['category'],
                    'color': list(section_data['color']),
                    'shelf_info': section_data['shelf_info'],
                    'subsections': section_data['subsections']
                }
                
            with open(file_path, 'w') as f:
                json.dump(layout_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving layout: {e}")
            
    def get_sections_at_point(self, x: int, y: int) -> List[str]:
        """Get all sections that contain the given point"""
        containing_sections = []
        
        for section_name, section_data in self.sections.items():
            if self._point_in_polygon(x, y, section_data['polygon']):
                containing_sections.append(section_name)
                
        return containing_sections
        
    def _point_in_polygon(self, x: int, y: int, polygon: List[Tuple[int, int]]) -> bool:
        """Check if point is inside polygon using ray casting algorithm"""
        if len(polygon) < 3:
            return False
            
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
        
    def draw_sections(self, frame: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """Draw all sections on the frame"""
        overlay = frame.copy()
        
        for section_name, section_data in self.sections.items():
            polygon = np.array(section_data['polygon'], np.int32)
            color = section_data['color']
            
            # Fill polygon
            cv2.fillPoly(overlay, [polygon], color)
            
            # Draw outline
            cv2.polylines(frame, [polygon], True, color, 2)
            
            # Draw section label
            self._draw_section_label(frame, section_name, polygon, color)
            
        # Blend overlay with original frame
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
        
    def _draw_section_label(self, frame: np.ndarray, section_name: str, 
                           polygon: np.ndarray, color: Tuple[int, int, int]):
        """Draw section name label"""
        # Calculate centroid of polygon
        centroid_x = int(np.mean(polygon[:, 0]))
        centroid_y = int(np.mean(polygon[:, 1]))
        
        # Draw text background
        text_size = cv2.getTextSize(section_name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_bg_pt1 = (centroid_x - text_size[0] // 2 - 5, centroid_y - text_size[1] // 2 - 5)
        text_bg_pt2 = (centroid_x + text_size[0] // 2 + 5, centroid_y + text_size[1] // 2 + 5)
        
        cv2.rectangle(frame, text_bg_pt1, text_bg_pt2, (0, 0, 0), -1)
        cv2.rectangle(frame, text_bg_pt1, text_bg_pt2, color, 2)
        
        # Draw text
        text_pos = (centroid_x - text_size[0] // 2, centroid_y + text_size[1] // 2)
        cv2.putText(frame, section_name, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
    def define_sections_interactive(self, frame: np.ndarray):
        """Interactive section definition using GUI"""
        SectionDefinitionDialog(self, frame)
        
    def add_shelf_to_section(self, section_name: str, shelf_id: str, 
                           shelf_polygon: List[Tuple[int, int]], product_info: Dict):
        """Add shelf information to a section"""
        if section_name not in self.sections:
            return False
            
        if 'shelves' not in self.sections[section_name]:
            self.sections[section_name]['shelves'] = {}
            
        self.sections[section_name]['shelves'][shelf_id] = {
            'polygon': shelf_polygon,
            'products': product_info
        }
        
        return True
        
    def get_section_info(self, section_name: str) -> Optional[Dict]:
        """Get detailed information about a section"""
        return self.sections.get(section_name)
        
    def create_default_walmart_layout(self, frame_width: int, frame_height: int):
        """Create a default Walmart-style store layout"""
        # Define typical Walmart sections
        sections_layout = {
            'Entrance': {
                'polygon': [(0, 0), (frame_width//4, 0), (frame_width//4, frame_height//8), (0, frame_height//8)],
                'category': 'Entrance'
            },
            'Electronics': {
                'polygon': [(frame_width//4, 0), (frame_width//2, 0), (frame_width//2, frame_height//3), (frame_width//4, frame_height//3)],
                'category': 'Electronics'
            },
            'Groceries': {
                'polygon': [(0, frame_height//3), (frame_width//2, frame_height//3), (frame_width//2, frame_height*2//3), (0, frame_height*2//3)],
                'category': 'Groceries'
            },
            'Clothing': {
                'polygon': [(frame_width//2, 0), (frame_width*3//4, 0), (frame_width*3//4, frame_height//2), (frame_width//2, frame_height//2)],
                'category': 'Clothing'
            },
            'Pharmacy': {
                'polygon': [(frame_width*3//4, 0), (frame_width, 0), (frame_width, frame_height//4), (frame_width*3//4, frame_height//4)],
                'category': 'Pharmacy'
            },
            'Home & Garden': {
                'polygon': [(frame_width//2, frame_height//2), (frame_width, frame_height//2), (frame_width, frame_height*3//4), (frame_width//2, frame_height*3//4)],
                'category': 'Home & Garden'
            },
            'Checkout': {
                'polygon': [(0, frame_height*2//3), (frame_width//2, frame_height*2//3), (frame_width//2, frame_height), (0, frame_height)],
                'category': 'Checkout'
            },
            'Exit': {
                'polygon': [(frame_width//2, frame_height*3//4), (frame_width, frame_height*3//4), (frame_width, frame_height), (frame_width//2, frame_height)],
                'category': 'Exit'
            }
        }
        
        for section_name, section_data in sections_layout.items():
            self.define_section(
                section_name, 
                section_data['polygon'], 
                section_data['category']
            )

class SectionDefinitionDialog:
    def __init__(self, section_manager: SectionManager, frame: np.ndarray):
        self.section_manager = section_manager
        self.frame = frame.copy()
        self.current_polygon = []
        self.drawing = False
        
        # Create dialog window
        self.window = tk.Toplevel()
        self.window.title("Define Store Sections")
        self.window.geometry("400x500")
        
        self.setup_ui()
        self.setup_opencv_window()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        # Section name entry
        ttk.Label(self.window, text="Section Name:").pack(pady=5)
        self.section_name_var = tk.StringVar()
        ttk.Entry(self.window, textvariable=self.section_name_var, width=30).pack(pady=5)
        
        # Category selection
        ttk.Label(self.window, text="Category:").pack(pady=5)
        self.category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(self.window, textvariable=self.category_var,
                                    values=list(self.section_manager.section_colors.keys()),
                                    state="readonly")
        category_combo.pack(pady=5)
        
        # Instructions
        instructions = """
Instructions:
1. Enter section name and select category
2. Click on the video to define polygon points
3. Press 'c' to close polygon
4. Press 's' to save section
5. Press 'r' to reset current polygon
6. Press 'q' to quit
        """
        ttk.Label(self.window, text=instructions, justify=tk.LEFT).pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Load Default Layout", 
                  command=self.load_default_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Layout", 
                  command=self.save_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Done", 
                  command=self.close_dialog).pack(side=tk.LEFT, padx=5)
        
        # Current sections list
        ttk.Label(self.window, text="Current Sections:").pack(pady=(20, 5))
        self.sections_listbox = tk.Listbox(self.window, height=8)
        self.sections_listbox.pack(fill=tk.X, padx=10, pady=5)
        
        self.update_sections_list()
        
    def setup_opencv_window(self):
        """Setup OpenCV window for drawing"""
        cv2.namedWindow("Define Sections", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Define Sections", self.mouse_callback)
        self.update_display()
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for polygon drawing"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_polygon.append((x, y))
            self.update_display()
            
    def update_display(self):
        """Update the OpenCV display"""
        display_frame = self.frame.copy()
        
        # Draw existing sections
        display_frame = self.section_manager.draw_sections(display_frame)
        
        # Draw current polygon being defined
        if len(self.current_polygon) > 0:
            for i, point in enumerate(self.current_polygon):
                cv2.circle(display_frame, point, 5, (0, 255, 255), -1)
                if i > 0:
                    cv2.line(display_frame, self.current_polygon[i-1], point, (0, 255, 255), 2)
                    
        # Draw instructions
        cv2.putText(display_frame, "Click to add points, 'c' to close, 's' to save, 'r' to reset, 'q' to quit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                   
        cv2.imshow("Define Sections", display_frame)
        
        # Handle keyboard events
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and len(self.current_polygon) > 2:
            # Close polygon
            cv2.line(display_frame, self.current_polygon[-1], self.current_polygon[0], (0, 255, 255), 2)
            cv2.imshow("Define Sections", display_frame)
            
        elif key == ord('s'):
            self.save_current_section()
            
        elif key == ord('r'):
            self.current_polygon = []
            self.update_display()
            
        elif key == ord('q'):
            self.close_dialog()
            
    def save_current_section(self):
        """Save the current polygon as a section"""
        if len(self.current_polygon) < 3:
            messagebox.showwarning("Warning", "Need at least 3 points to define a section")
            return
            
        section_name = self.section_name_var.get().strip()
        if not section_name:
            messagebox.showwarning("Warning", "Please enter a section name")
            return
            
        category = self.category_var.get()
        
        self.section_manager.define_section(section_name, self.current_polygon, category)
        
        # Reset for next section
        self.current_polygon = []
        self.section_name_var.set("")
        
        self.update_sections_list()
        self.update_display()
        
        messagebox.showinfo("Success", f"Section '{section_name}' saved successfully!")
        
    def update_sections_list(self):
        """Update the sections list display"""
        self.sections_listbox.delete(0, tk.END)
        for section_name in self.section_manager.sections.keys():
            self.sections_listbox.insert(tk.END, section_name)
            
    def load_default_layout(self):
        """Load default layout"""
        height, width = self.frame.shape[:2]
        self.section_manager.create_default_walmart_layout(width, height)
        self.update_sections_list()
        self.update_display()
        
    def save_layout(self):
        """Save current layout to file"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Save Layout",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            self.section_manager.save_layout(file_path)
            messagebox.showinfo("Success", "Layout saved successfully!")
            
    def close_dialog(self):
        """Close the dialog"""
        cv2.destroyWindow("Define Sections")
        self.window.destroy()
