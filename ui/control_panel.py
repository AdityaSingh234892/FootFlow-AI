"""
Control Panel Module
UI components for the tracking system
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

class ControlPanel:
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the control panel UI"""
        # This is a placeholder - the main UI is handled in main.py
        pass
