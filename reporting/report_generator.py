"""
Report Generator Module
Generates comprehensive reports from tracking data
"""

import json
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import base64

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        custom_styles = {}
        
        custom_styles['CustomTitle'] = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB')
        )
        
        custom_styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#A23B72')
        )
        
        return custom_styles
        
    def generate_comprehensive_report(self, tracking_paths: Dict, section_visits: Dict, 
                                    sections: Dict, output_path: str):
        """Generate a comprehensive PDF report"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("Store Footstep Tracking & Analysis Report", 
                         self.custom_styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        metadata = self._generate_metadata(tracking_paths, section_visits, sections)
        story.extend(self._create_metadata_section(metadata))
        
        # Executive summary
        story.extend(self._create_executive_summary(tracking_paths, section_visits))
        
        # Individual person analysis
        story.extend(self._create_person_analysis(tracking_paths, section_visits))
        
        # Section popularity analysis
        story.extend(self._create_section_analysis(section_visits, sections))
        
        # Path analysis and heat maps
        story.extend(self._create_path_analysis(tracking_paths))
        
        # Recommendations
        story.extend(self._create_recommendations(tracking_paths, section_visits))
        
        # Build PDF
        doc.build(story)
        
    def _generate_metadata(self, tracking_paths: Dict, section_visits: Dict, sections: Dict) -> Dict:
        """Generate report metadata"""
        total_people = len(tracking_paths)
        total_sections = len(sections)
        total_visits = sum(len(visits) for visits in section_visits.values())
        
        return {
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_people_tracked': total_people,
            'total_sections_defined': total_sections,
            'total_section_visits': total_visits,
            'analysis_period': 'Video Analysis Session'
        }
        
    def _create_metadata_section(self, metadata: Dict) -> List:
        """Create metadata section for report"""
        elements = []
        
        elements.append(Paragraph("Report Information", self.custom_styles['SectionHeader']))
        
        metadata_data = [
            ['Report Generated:', metadata['generation_time']],
            ['Total People Tracked:', str(metadata['total_people_tracked'])],
            ['Total Sections Defined:', str(metadata['total_sections_defined'])],
            ['Total Section Visits:', str(metadata['total_section_visits'])],
            ['Analysis Period:', metadata['analysis_period']]
        ]
        
        table = Table(metadata_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
        
    def _create_executive_summary(self, tracking_paths: Dict, section_visits: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.custom_styles['SectionHeader']))
        
        # Calculate key metrics
        total_people = len(tracking_paths)
        avg_path_length = np.mean([len(path) for path in tracking_paths.values()]) if tracking_paths else 0
        
        # Most popular sections
        section_popularity = {}
        for visits in section_visits.values():
            for visit in visits:
                section = visit.get('section', 'Unknown')
                section_popularity[section] = section_popularity.get(section, 0) + 1
                
        most_popular = max(section_popularity.items(), key=lambda x: x[1]) if section_popularity else ("None", 0)
        
        summary_text = f"""
        <para>This report analyzes the movement patterns of {total_people} individuals tracked through the store. 
        The analysis reveals valuable insights about customer behavior, section popularity, and shopping patterns.</para>
        
        <para><b>Key Findings:</b></para>
        <para>• Average path length: {avg_path_length:.1f} tracking points per person</para>
        <para>• Most popular section: {most_popular[0]} ({most_popular[1]} visits)</para>
        <para>• Total section transitions recorded: {sum(len(visits) for visits in section_visits.values())}</para>
        """
        
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
        
    def _create_person_analysis(self, tracking_paths: Dict, section_visits: Dict) -> List:
        """Create individual person analysis section"""
        elements = []
        
        elements.append(Paragraph("Individual Customer Analysis", self.custom_styles['SectionHeader']))
        
        for person_id, path in tracking_paths.items():
            if not path:
                continue
                
            # Calculate metrics for this person
            total_distance = self._calculate_path_distance(path)
            duration = (path[-1]['timestamp'] - path[0]['timestamp']) if len(path) > 1 else 0
            sections_visited = len(set(visit['section'] for visit in section_visits.get(person_id, [])))
            
            person_data = [
                ['Person ID:', f"Person {person_id}"],
                ['Total Distance Traveled:', f"{total_distance:.1f} pixels"],
                ['Total Time Tracked:', f"{duration:.1f} seconds"],
                ['Sections Visited:', str(sections_visited)],
                ['Path Points Recorded:', str(len(path))]
            ]
            
            elements.append(Paragraph(f"Person {person_id} Details", self.styles['Heading3']))
            
            table = Table(person_data, colWidths=[2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 10))
            
        return elements
        
    def _calculate_path_distance(self, path: List[Dict]) -> float:
        """Calculate total distance for a path"""
        if len(path) < 2:
            return 0.0
            
        total_distance = 0.0
        for i in range(1, len(path)):
            p1 = path[i-1]['position']
            p2 = path[i]['position']
            distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_distance += distance
            
        return total_distance
        
    def _create_section_analysis(self, section_visits: Dict, sections: Dict) -> List:
        """Create section popularity analysis"""
        elements = []
        
        elements.append(Paragraph("Section Analysis", self.custom_styles['SectionHeader']))
        
        # Calculate section statistics
        section_stats = {}
        for person_id, visits in section_visits.items():
            for visit in visits:
                section = visit.get('section', 'Unknown')
                if section not in section_stats:
                    section_stats[section] = {'visits': 0, 'unique_visitors': set(), 'total_time': 0}
                
                section_stats[section]['visits'] += 1
                section_stats[section]['unique_visitors'].add(person_id)
                section_stats[section]['total_time'] += visit.get('duration_frames', 0) / 30.0  # Convert to seconds
                
        # Create table data
        table_data = [['Section', 'Total Visits', 'Unique Visitors', 'Avg. Time (sec)']]
        
        for section, stats in sorted(section_stats.items(), key=lambda x: x[1]['visits'], reverse=True):
            unique_count = len(stats['unique_visitors'])
            avg_time = stats['total_time'] / stats['visits'] if stats['visits'] > 0 else 0
            
            table_data.append([
                section,
                str(stats['visits']),
                str(unique_count),
                f"{avg_time:.1f}"
            ])
            
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("No section visit data available.", self.styles['Normal']))
            
        elements.append(Spacer(1, 20))
        
        return elements
        
    def _create_path_analysis(self, tracking_paths: Dict) -> List:
        """Create path analysis section"""
        elements = []
        
        elements.append(Paragraph("Path Analysis", self.custom_styles['SectionHeader']))
        
        if not tracking_paths:
            elements.append(Paragraph("No path data available for analysis.", self.styles['Normal']))
            return elements
            
        # Generate path statistics chart
        chart_buffer = self._generate_path_statistics_chart(tracking_paths)
        if chart_buffer:
            elements.append(Image(chart_buffer, width=6*inch, height=4*inch))
            elements.append(Spacer(1, 10))
            
        # Path efficiency analysis
        efficiency_text = self._analyze_path_efficiency(tracking_paths)
        elements.append(Paragraph(efficiency_text, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
        
    def _generate_path_statistics_chart(self, tracking_paths: Dict):
        """Generate path statistics chart"""
        try:
            # Calculate path lengths
            path_lengths = [len(path) for path in tracking_paths.values() if path]
            
            if not path_lengths:
                return None
                
            plt.figure(figsize=(10, 6))
            plt.hist(path_lengths, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Distribution of Path Lengths')
            plt.xlabel('Number of Tracking Points')
            plt.ylabel('Number of People')
            plt.grid(True, alpha=0.3)
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None
            
    def _analyze_path_efficiency(self, tracking_paths: Dict) -> str:
        """Analyze path efficiency"""
        if not tracking_paths:
            return "No path data available for efficiency analysis."
            
        total_paths = len(tracking_paths)
        avg_length = np.mean([len(path) for path in tracking_paths.values() if path])
        
        efficiency_analysis = f"""
        <para><b>Path Efficiency Analysis:</b></para>
        <para>• Total paths analyzed: {total_paths}</para>
        <para>• Average path length: {avg_length:.1f} tracking points</para>
        <para>• Path complexity varies among customers, indicating different shopping behaviors and preferences.</para>
        """
        
        return efficiency_analysis
        
    def _create_recommendations(self, tracking_paths: Dict, section_visits: Dict) -> List:
        """Create recommendations section"""
        elements = []
        
        elements.append(Paragraph("Recommendations", self.custom_styles['SectionHeader']))
        
        recommendations = [
            "Monitor high-traffic areas for potential congestion and optimize layout accordingly.",
            "Place popular items in easily accessible locations to improve customer flow.",
            "Consider the placement of complementary products near frequently visited sections.",
            "Analyze customer dwell time in sections to optimize product placement and promotional strategies.",
            "Use path analysis to identify potential improvements in store navigation and signage."
        ]
        
        rec_text = "<para><b>Based on the tracking analysis, we recommend:</b></para>"
        for i, rec in enumerate(recommendations, 1):
            rec_text += f"<para>{i}. {rec}</para>"
            
        elements.append(Paragraph(rec_text, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
        
    def export_csv_data(self, tracking_paths: Dict, section_visits: Dict, output_path: str):
        """Export tracking data to CSV format"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Person_ID', 'Frame', 'X_Position', 'Y_Position', 'Timestamp', 'Section_Visits'])
                
                # Write data
                for person_id, path in tracking_paths.items():
                    for point in path:
                        # Get sections at this frame for this person
                        sections_at_frame = []
                        if person_id in section_visits:
                            for visit in section_visits[person_id]:
                                if (visit.get('entry_frame', 0) <= point['frame'] <= 
                                    visit.get('exit_frame', float('inf'))):
                                    sections_at_frame.append(visit['section'])
                        
                        writer.writerow([
                            person_id,
                            point['frame'],
                            point['position'][0],
                            point['position'][1],
                            point['timestamp'],
                            ';'.join(sections_at_frame)
                        ])
                        
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            
    def export_json_data(self, tracking_paths: Dict, section_visits: Dict, 
                        sections: Dict, output_path: str):
        """Export tracking data to JSON format"""
        try:
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_people': len(tracking_paths),
                    'total_sections': len(sections)
                },
                'tracking_paths': tracking_paths,
                'section_visits': section_visits,
                'sections': sections,
                'analytics': self._generate_analytics_summary(tracking_paths, section_visits)
            }
            
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, default=str)
                
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            
    def _generate_analytics_summary(self, tracking_paths: Dict, section_visits: Dict) -> Dict:
        """Generate analytics summary for export"""
        summary = {
            'total_tracking_points': sum(len(path) for path in tracking_paths.values()),
            'total_section_visits': sum(len(visits) for visits in section_visits.values()),
            'average_path_length': 0,
            'section_popularity': {},
            'person_statistics': {}
        }
        
        # Calculate average path length
        if tracking_paths:
            summary['average_path_length'] = np.mean([len(path) for path in tracking_paths.values()])
            
        # Section popularity
        for visits in section_visits.values():
            for visit in visits:
                section = visit.get('section', 'Unknown')
                summary['section_popularity'][section] = summary['section_popularity'].get(section, 0) + 1
                
        # Person statistics
        for person_id, path in tracking_paths.items():
            if path:
                summary['person_statistics'][person_id] = {
                    'path_length': len(path),
                    'duration': path[-1]['timestamp'] - path[0]['timestamp'] if len(path) > 1 else 0,
                    'sections_visited': len(set(visit['section'] for visit in section_visits.get(person_id, [])))
                }
                
        return summary
