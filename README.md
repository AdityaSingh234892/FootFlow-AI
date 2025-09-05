# OpenCV Footstep Tracking System

A comprehensive Python application for tracking human movement in retail store video footage. The system provides two versions: a full-featured version with advanced tracking algorithms and a simplified version that works with basic OpenCV installation.

## Features

- **Manual Person Selection**: Click and drag to select individuals in video footage
- **Advanced Tracking**: Multiple tracking algorithms (CSRT, KCF, MOSSE) with fallback options
- **Path Visualization**: Real-time display of movement paths with colored trails
- **Store Section Mapping**: Define store sections and track customer visits
- **Visit Analysis**: Automatic detection of section entries and duration tracking
- **Comprehensive Reporting**: Export detailed reports in text or PDF format
- **User-Friendly GUI**: Intuitive Tkinter interface with video controls

## System Versions

### 1. Full System (main.py)
The complete system with all advanced features:
- Advanced OpenCV tracking algorithms (CSRT, KCF, MOSSE)
- PDF report generation with charts and analytics
- Comprehensive store layout management
- Advanced path analysis and visit statistics

**Requirements:**
```bash
pip install opencv-contrib-python numpy matplotlib pillow reportlab
```

### 2. Simplified System (simple_tracker.py)
A lightweight version that works with basic OpenCV:
- Template matching-based tracking
- Basic path visualization
- Section definition and visit tracking
- Simple text report export

**Requirements:**
```bash
pip install opencv-python pillow
```

## Quick Start

### Option 1: Use the Simplified System (Recommended for first-time users)
```bash
# Test the system
python test_simple.py

# Run the simplified tracker
python simple_tracker.py

# Or use the batch file (Windows)
run_simple.bat
```

### Option 2: Use the Full System
```bash
# Install all dependencies
python install_dependencies.py

# Test the full system
python test_system.py

# Run the full application
python main.py

# Or use the batch file (Windows)
start.bat
```
- JSON-based layout storage and loading

### Analytics and Insights
- Individual customer path analysis
- Section popularity metrics
- Shopping pattern recognition
- Heat map generation for popular areas
- Conversion rate analysis (entrance to checkout)
- Path efficiency calculations
- Common route identification

### Reporting System
- PDF reports with visualizations
- CSV data export for further analysis
- JSON export for data interchange
- Analytics dashboard with charts and metrics
- Customizable report templates

## Installation

1. **Clone or download the project**:
   ```bash
   cd wallmart3
   ```

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main_clean.py
   ```

## Required Dependencies

- `opencv-python` - Computer vision and tracking
- `opencv-contrib-python` - Additional OpenCV algorithms
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualizations
- `pandas` - Data analysis and manipulation
- `reportlab` - PDF report generation
- `Pillow` - Image processing
- `scipy` - Scientific computing
- `seaborn` - Statistical data visualization
- `tkinter` - GUI framework (usually included with Python)

## Usage Guide

### 1. Load Video
- Click "Load Video" to select a video file (MP4, AVI, MOV, MKV)
- The video will be displayed in the main canvas
- Use video controls for playback (Play/Pause, Stop, frame navigation)

### 2. Define Store Sections
- Click "Define Sections" to open the section definition tool
- Click points on the video to create polygon boundaries
- Press 'c' to close polygon, 's' to save section, 'r' to reset
- Load pre-defined layouts with "Load Default Layout"

### 3. Track People
- Click "Select Person" to enter tracking mode
- Draw a bounding box around the person you want to track
- The system will automatically track their movement
- Multiple people can be tracked simultaneously

### 4. View Real-time Analysis
- Toggle "Show/Hide Sections" to overlay section boundaries
- Watch real-time path visualization with colored trails
- Monitor active trackers in the tracker list
- View section visit information as it's detected

### 5. Generate Reports
- Click "Generate Report" to create a comprehensive PDF report
- Use "Export Data" to save tracking data in JSON or CSV format
- "Show Analytics" opens a dashboard with detailed metrics

## Project Structure

```
wallmart3/
├── main_clean.py              # Main application entry point
├── requirements.txt           # Python dependencies
├── sample_store_layout.json   # Example store layout
├── tracking/                  # Tracking modules
│   ├── person_tracker.py      # Person tracking algorithms
│   ├── path_visualizer.py     # Path visualization
│   └── __init__.py
├── store/                     # Store management modules
│   ├── section_manager.py     # Section definition and management
│   ├── visit_analyzer.py      # Visit analysis and metrics
│   └── __init__.py
├── ui/                        # User interface components
│   ├── control_panel.py       # UI control elements
│   └── __init__.py
├── reporting/                 # Report generation
│   ├── report_generator.py    # PDF and data export
│   └── __init__.py
└── utils/                     # Utility modules
    ├── config_manager.py      # Configuration management
    └── __init__.py
```

## Key Components

### PersonTracker
- Implements OpenCV tracking algorithms (CSRT, KCF, MOSSE)
- Handles multiple simultaneous trackers
- Provides tracker lifecycle management
- Supports tracker reinitialization for lost targets

### PathVisualizer
- Draws continuous footstep trails
- Color-codes different individuals
- Shows timestamps and direction changes
- Generates heat maps for popular areas
- Calculates path metrics and statistics

### SectionManager
- Interactive polygon-based section definition
- Hierarchical store layout management
- Point-in-polygon detection for section visits
- JSON-based layout persistence
- Pre-built store templates

### VisitAnalyzer
- Tracks section entry/exit events
- Calculates dwell times and visit patterns
- Identifies shopping behavior metrics
- Analyzes conversion rates and efficiency
- Generates timeline and sequence data

### ReportGenerator
- Creates comprehensive PDF reports
- Exports data in multiple formats
- Generates charts and visualizations
- Provides customizable report templates
- Includes executive summaries and recommendations

## Advanced Features

### Multi-Algorithm Tracking
The system supports three different tracking algorithms:
- **CSRT**: Best accuracy, slower performance
- **KCF**: Balanced accuracy and speed
- **MOSSE**: Fastest, lower accuracy

### Section Hierarchy
Define complex store layouts with:
- Departments (Electronics, Groceries, etc.)
- Sections within departments
- Individual shelves and product areas
- Custom polygon boundaries for each area

### Analytics Dashboard
Real-time metrics including:
- Customer flow analysis
- Section popularity rankings
- Average visit durations
- Path efficiency scores
- Heat map visualizations

### Export Capabilities
Multiple export formats:
- **PDF Reports**: Professional formatted reports with charts
- **JSON Data**: Complete tracking data for further analysis
- **CSV Files**: Spreadsheet-compatible format for data analysis

## Configuration

The system uses a configuration file (`config.json`) for customization:
- Tracking algorithm preferences
- Visualization settings
- Analysis parameters
- UI layout options
- Export formats

## Tips for Best Results

1. **Video Quality**: Use high-resolution videos with good lighting
2. **Camera Angle**: Overhead or angled views work best for tracking
3. **Person Selection**: Select the full body or torso for better tracking
4. **Section Definition**: Define clear, non-overlapping section boundaries
5. **Multiple Tracking**: Start with one person, then add more as needed

## Troubleshooting

### Common Issues
- **Tracking Lost**: Try different tracking algorithms or reinitialize tracker
- **Section Not Detected**: Check polygon boundaries and point-in-polygon logic
- **Video Won't Load**: Ensure video codec compatibility with OpenCV
- **Export Errors**: Check file permissions and available disk space

### Performance Optimization
- Use lower resolution videos for faster processing
- Limit the number of simultaneous trackers
- Adjust tracking algorithm based on performance needs
- Close unnecessary applications to free up system resources

## Future Enhancements

Potential improvements for future versions:
- Deep learning-based person detection and tracking
- Automatic person re-identification across occlusions
- Real-time analytics dashboard with live updates
- Integration with store POS systems for purchase correlation
- Mobile app for remote monitoring and control
- Cloud-based analytics and reporting platform

## License

This project is provided for educational and research purposes. Please ensure compliance with privacy laws and regulations when using in retail environments.

## Support

For questions, issues, or contributions, please refer to the project documentation or contact the development team.
