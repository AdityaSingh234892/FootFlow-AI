"""
Visit Analyzer Module
Analyzes customer visits to different store sections
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

class VisitAnalyzer:
    def __init__(self):
        self.visits = {}  # person_id -> list of visits
        self.current_sections = {}  # person_id -> current sections
        self.section_entries = {}  # person_id -> section -> entry_time
        
    def record_visit(self, person_id: int, sections: List[str], 
                    frame_number: int, x: int, y: int):
        """Record a visit to sections"""
        if person_id not in self.visits:
            self.visits[person_id] = []
            self.current_sections[person_id] = set()
            self.section_entries[person_id] = {}
            
        current_sections_set = set(sections)
        previous_sections = self.current_sections[person_id]
        
        # Check for new section entries
        new_sections = current_sections_set - previous_sections
        for section in new_sections:
            self.section_entries[person_id][section] = frame_number
            
        # Check for section exits
        exited_sections = previous_sections - current_sections_set
        for section in exited_sections:
            if section in self.section_entries[person_id]:
                entry_frame = self.section_entries[person_id][section]
                duration = frame_number - entry_frame
                
                visit_record = {
                    'section': section,
                    'entry_frame': entry_frame,
                    'exit_frame': frame_number,
                    'duration_frames': duration,
                    'entry_position': self._get_position_at_frame(person_id, entry_frame),
                    'exit_position': (x, y),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.visits[person_id].append(visit_record)
                del self.section_entries[person_id][section]
                
        self.current_sections[person_id] = current_sections_set
        
    def _get_position_at_frame(self, person_id: int, frame_number: int) -> Tuple[int, int]:
        """Get position of person at specific frame (placeholder implementation)"""
        # This would need to be connected to the tracking data
        return (0, 0)
        
    def get_person_visits(self, person_id: int) -> List[Dict]:
        """Get all visits for a specific person"""
        return self.visits.get(person_id, [])
        
    def get_section_visitors(self, section_name: str) -> List[int]:
        """Get all persons who visited a specific section"""
        visitors = set()
        for person_id, visits in self.visits.items():
            for visit in visits:
                if visit['section'] == section_name:
                    visitors.add(person_id)
        return list(visitors)
        
    def calculate_time_in_section(self, person_id: int, section_name: str, fps: float = 30.0) -> float:
        """Calculate total time spent by person in section (in seconds)"""
        total_frames = 0
        
        if person_id in self.visits:
            for visit in self.visits[person_id]:
                if visit['section'] == section_name:
                    total_frames += visit['duration_frames']
                    
        return total_frames / fps
        
    def get_popular_sections(self) -> List[Tuple[str, int]]:
        """Get sections ordered by popularity (number of visitors)"""
        section_counts = {}
        
        for person_id, visits in self.visits.items():
            visited_sections = set()
            for visit in visits:
                visited_sections.add(visit['section'])
            
            for section in visited_sections:
                section_counts[section] = section_counts.get(section, 0) + 1
                
        return sorted(section_counts.items(), key=lambda x: x[1], reverse=True)
        
    def get_average_visit_duration(self, section_name: str, fps: float = 30.0) -> float:
        """Get average visit duration for a section"""
        durations = []
        
        for person_id, visits in self.visits.items():
            for visit in visits:
                if visit['section'] == section_name:
                    durations.append(visit['duration_frames'] / fps)
                    
        return sum(durations) / len(durations) if durations else 0.0
        
    def analyze_shopping_patterns(self, person_id: int) -> Dict:
        """Analyze shopping patterns for a specific person"""
        if person_id not in self.visits:
            return {}
            
        visits = self.visits[person_id]
        if not visits:
            return {}
            
        # Sort visits by entry time
        sorted_visits = sorted(visits, key=lambda x: x['entry_frame'])
        
        analysis = {
            'total_sections_visited': len(set(v['section'] for v in visits)),
            'total_visits': len(visits),
            'visit_sequence': [v['section'] for v in sorted_visits],
            'section_durations': {},
            'most_visited_section': None,
            'shopping_efficiency': 0.0,
            'backtracking_score': 0.0
        }
        
        # Calculate time spent per section
        section_times = {}
        for visit in visits:
            section = visit['section']
            duration = visit['duration_frames']
            section_times[section] = section_times.get(section, 0) + duration
            
        analysis['section_durations'] = section_times
        
        # Find most visited section
        if section_times:
            analysis['most_visited_section'] = max(section_times.items(), key=lambda x: x[1])
            
        # Calculate backtracking (visiting same section multiple times)
        unique_visits = len(set(v['section'] for v in visits))
        total_visits = len(visits)
        analysis['backtracking_score'] = (total_visits - unique_visits) / total_visits if total_visits > 0 else 0
        
        return analysis
        
    def generate_visit_timeline(self, person_id: int, fps: float = 30.0) -> List[Dict]:
        """Generate chronological timeline of visits"""
        if person_id not in self.visits:
            return []
            
        visits = self.visits[person_id]
        timeline = []
        
        for visit in sorted(visits, key=lambda x: x['entry_frame']):
            entry_time = visit['entry_frame'] / fps
            exit_time = visit['exit_frame'] / fps
            duration = visit['duration_frames'] / fps
            
            timeline.append({
                'section': visit['section'],
                'entry_time_seconds': entry_time,
                'exit_time_seconds': exit_time,
                'duration_seconds': duration,
                'entry_time_formatted': self._format_time(entry_time),
                'exit_time_formatted': self._format_time(exit_time),
                'duration_formatted': self._format_duration(duration)
            })
            
        return timeline
        
    def _format_time(self, seconds: float) -> str:
        """Format time in MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
            
    def export_analytics_data(self) -> Dict:
        """Export all analytics data for reporting"""
        return {
            'visits': self.visits,
            'summary': {
                'total_people_tracked': len(self.visits),
                'total_visits_recorded': sum(len(visits) for visits in self.visits.values()),
                'sections_analytics': self._get_sections_analytics(),
                'popular_sections': self.get_popular_sections(),
                'export_timestamp': datetime.now().isoformat()
            }
        }
        
    def _get_sections_analytics(self) -> Dict:
        """Get comprehensive analytics for all sections"""
        sections_analytics = {}
        
        # Get all unique sections
        all_sections = set()
        for visits in self.visits.values():
            for visit in visits:
                all_sections.add(visit['section'])
                
        for section in all_sections:
            visitors = self.get_section_visitors(section)
            avg_duration = self.get_average_visit_duration(section)
            
            # Calculate total visits to this section
            total_visits = 0
            for visits in self.visits.values():
                total_visits += sum(1 for v in visits if v['section'] == section)
                
            sections_analytics[section] = {
                'total_visitors': len(visitors),
                'total_visits': total_visits,
                'average_duration_seconds': avg_duration,
                'visitor_ids': visitors
            }
            
        return sections_analytics
        
    def get_heat_map_data(self, section_name: Optional[str] = None) -> Dict:
        """Get data for generating heat maps"""
        heat_map_data = {
            'entry_points': [],
            'exit_points': [],
            'high_traffic_areas': []
        }
        
        for person_id, visits in self.visits.items():
            for visit in visits:
                if section_name is None or visit['section'] == section_name:
                    heat_map_data['entry_points'].append(visit['entry_position'])
                    heat_map_data['exit_points'].append(visit['exit_position'])
                    
        return heat_map_data
        
    def calculate_conversion_metrics(self, entry_section: str = "Entrance", 
                                   checkout_section: str = "Checkout") -> Dict:
        """Calculate conversion metrics (entrance to checkout)"""
        total_entries = len(self.get_section_visitors(entry_section))
        total_checkouts = len(self.get_section_visitors(checkout_section))
        
        conversion_rate = (total_checkouts / total_entries * 100) if total_entries > 0 else 0
        
        return {
            'total_entries': total_entries,
            'total_checkouts': total_checkouts,
            'conversion_rate_percent': conversion_rate,
            'bounce_rate_percent': 100 - conversion_rate
        }
        
    def find_common_paths(self, min_support: int = 2) -> List[Tuple[List[str], int]]:
        """Find common shopping paths (frequent sequences)"""
        all_paths = []
        
        for person_id, visits in self.visits.items():
            if len(visits) > 1:
                path = [v['section'] for v in sorted(visits, key=lambda x: x['entry_frame'])]
                all_paths.append(path)
                
        # Find frequent subsequences
        common_paths = {}
        
        for path in all_paths:
            for length in range(2, len(path) + 1):
                for start in range(len(path) - length + 1):
                    subpath = tuple(path[start:start + length])
                    common_paths[subpath] = common_paths.get(subpath, 0) + 1
                    
        # Filter by minimum support
        frequent_paths = [(list(path), count) for path, count in common_paths.items() 
                         if count >= min_support]
        
        return sorted(frequent_paths, key=lambda x: x[1], reverse=True)
