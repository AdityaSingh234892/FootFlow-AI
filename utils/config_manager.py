"""
Configuration Manager Module
Handles application configuration and settings
"""

import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self.load_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration settings"""
        return {
            'tracking': {
                'default_algorithm': 'CSRT',
                'max_lost_frames': 30,
                'path_thickness': 3,
                'point_radius': 5
            },
            'visualization': {
                'show_timestamps': True,
                'show_section_boundaries': True,
                'path_fade_alpha': 0.7,
                'section_overlay_alpha': 0.3
            },
            'analysis': {
                'min_visit_duration': 1.0,  # seconds
                'section_transition_threshold': 10,  # pixels
                'path_smoothing': True
            },
            'export': {
                'default_format': 'pdf',
                'include_charts': True,
                'chart_dpi': 150
            },
            'ui': {
                'window_width': 1400,
                'window_height': 900,
                'video_canvas_width': 800,
                'video_canvas_height': 600
            }
        }
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._merge_config(self.config, loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def _merge_config(self, default: Dict, loaded: Dict):
        """Merge loaded config with default config"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
                
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value
        
    def get_tracking_config(self) -> Dict:
        """Get tracking-related configuration"""
        return self.config.get('tracking', {})
        
    def get_visualization_config(self) -> Dict:
        """Get visualization-related configuration"""
        return self.config.get('visualization', {})
        
    def get_analysis_config(self) -> Dict:
        """Get analysis-related configuration"""
        return self.config.get('analysis', {})
        
    def get_export_config(self) -> Dict:
        """Get export-related configuration"""
        return self.config.get('export', {})
        
    def get_ui_config(self) -> Dict:
        """Get UI-related configuration"""
        return self.config.get('ui', {})
