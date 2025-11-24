# DJI Video to 3D Map Pipeline

A comprehensive Windows application for processing DJI Mini 3 drone videos and creating georeferenced 3D maps using photogrammetry.

## Features

### Core Functionality
- **Video Frame Extraction**: Extract frames from DJI Mini 3 `.MP4` videos at configurable rates using FFmpeg
- **SRT Telemetry Parsing**: Extract GPS coordinates, altitude, gimbal pitch/yaw, and camera settings from DJI `.SRT` files
- **Intelligent Synchronization**: Synchronize video frames with telemetry data using:
  - Linear interpolation for GPS coordinates and altitude
  - Circular interpolation for angular values (yaw) to handle 359° → 0° transitions
- **Flight Classification**: Automatically classify flight type:
  - **Nadir Mapping**: Gimbal at -90°, low yaw variation
  - **Orbit/Structure**: Oblique gimbal angle, high yaw variation
- **EXIF Geotagging**: Inject GPS and camera metadata into images using ExifTool
- **WebODM Integration**: Create 3D georeferenced models using open-source WebODM
- **Export Options**: Save results to local folders or Google Drive

### User Interface
- Clean tabbed interface for step-by-step workflow
- Drag-and-drop file selection
- Real-time processing log
- Progress indicators
- Error handling and validation

## Requirements

### System Requirements
- Windows 10 or later
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space for processing

### Software Dependencies
- **FFmpeg**: Required for video frame extraction
  - Download from: https://ffmpeg.org/download.html
  - Add to system PATH
- **ExifTool**: Bundled with the application
- **WebODM**: Local or remote instance
  - Quick start: https://github.com/OpenDroneMap/WebODM

## Installation

### Option 1: Download Pre-built Executable
1. Go to [Releases](https://github.com/Paisano7780/Video-SRT_to_3D_Map/releases)
2. Download the latest `DJI_3D_Mapper.exe`
3. Install FFmpeg and add to PATH
4. Run the application

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/Paisano7780/Video-SRT_to_3D_Map.git
cd Video-SRT_to_3D_Map

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (add to PATH)
# Download from https://ffmpeg.org/

# Run application
python main_app.py
```

## Usage Guide

### Step 1: Prepare Your Files
1. Copy video files (`.MP4`) and telemetry files (`.SRT`) from your DJI Mini 3 drone
2. Ensure files have matching names (e.g., `DJI_0001.MP4` and `DJI_0001.SRT`)

### Step 2: Input Files
1. Open the application
2. Navigate to **"1. Input Files"** tab
3. Select video file (SRT will auto-detect if named correctly)
4. Choose buffer directory for geotagged images

### Step 3: Processing
1. Go to **"2. Processing"** tab
2. Set frame extraction rate (default: 1 fps recommended)
3. Click **"Start Processing Pipeline"**
4. Wait for completion (time depends on video length)

The pipeline will:
- Extract frames from video
- Parse telemetry from SRT
- Synchronize and interpolate GPS data
- Classify flight type
- Inject EXIF metadata into images

### Step 4: WebODM Integration
1. Go to **"3. WebODM"** tab
2. Enter WebODM connection details:
   - URL: `http://localhost:8000` (default for local)
   - Username: `admin` (default)
   - Password: `admin` (default)
3. Click **"Test Connection"** to verify
4. Click **"Create 3D Map"**
5. Wait for processing (can take 30 minutes to several hours depending on image count and quality settings)

### Step 5: Export Results
1. Go to **"4. Output"** tab
2. Select output directory
3. Click **"Export Results"**
4. Results include:
   - 3D textured mesh
   - Orthophoto (2D map)
   - Digital Surface Model (DSM)
   - Point cloud

## Configuration

### Frame Extraction Rate
- **0.5 fps**: Lower quality, faster processing, smaller files
- **1.0 fps**: Recommended balance (default)
- **2.0 fps**: Higher quality, slower processing, larger files

### WebODM Processing Options
Default settings provide good quality:
- DSM and DTM generation: Enabled
- Orthophoto resolution: 2 cm/pixel
- Feature quality: High
- Point cloud quality: High
- Mesh octree depth: 11

## Technical Details

### SRT Format Parsing
The application parses DJI SRT format with regex patterns:
```
[latitude: -34.6037] [longitude: -58.3816] [altitude: 150.5] 
[rel_alt: 50.2] [gimbal_pitch: -90.0] [yaw: 45.0]
```

### Interpolation Methods
- **Linear**: GPS coordinates, altitude, gimbal pitch
- **Circular**: Yaw angles (handles wrap-around at 0°/360°)

### EXIF Tags Injected
- `GPSLatitude`, `GPSLatitudeRef`
- `GPSLongitude`, `GPSLongitudeRef`
- `GPSAltitude`, `GPSAltitudeRef`
- `AbsoluteAltitude`, `RelativeAltitude`
- `XMP:GimbalPitchDegree`
- `XMP:GimbalYawDegree`
- `XMP:FlightYawDegree`
- `GPSImgDirection`
- Camera settings: ISO, Shutter Speed

## Troubleshooting

### "FFmpeg not found"
- Install FFmpeg from https://ffmpeg.org/
- Add FFmpeg bin directory to system PATH
- Restart the application

### "ExifTool not found"
- Download from https://exiftool.org/
- Place `exiftool.exe` in the application directory
- Or install and add to system PATH

### "WebODM connection failed"
- Ensure WebODM is running
- Check URL, username, and password
- For local instance: `docker-compose up` in WebODM directory

### "SRT duration mismatch"
- Video and SRT files may not match
- Check that files are from the same recording
- Application will ask to continue anyway

### Processing is slow
- Reduce frame extraction rate (try 0.5 fps)
- Ensure sufficient RAM is available
- Close other applications
- WebODM processing time scales with image count

## Development

### Running Tests
```bash
pytest test_*.py -v
```

### Building Executable
```bash
pyinstaller --name="DJI_3D_Mapper" \
  --windowed \
  --onefile \
  --add-binary="exiftool.exe;." \
  main_app.py
```

### Project Structure
```
Video-SRT_to_3D_Map/
├── main_app.py           # Main GUI application
├── srt_parser.py         # SRT telemetry parser
├── frame_extractor.py    # Video frame extraction
├── telemetry_sync.py     # Synchronization and interpolation
├── exif_injector.py      # EXIF metadata injection
├── webodm_client.py      # WebODM API client
├── test_*.py             # Unit tests
├── requirements.txt      # Python dependencies
└── .github/workflows/    # CI/CD workflows
```

## Credits

### Technologies Used
- **Python 3.10+**: Core language
- **FFmpeg**: Video processing
- **ExifTool**: Metadata manipulation
- **WebODM**: 3D reconstruction
- **Tkinter**: GUI framework
- **Pandas/NumPy**: Data processing

### External Resources
- DJI telemetry format documentation
- WebODM API: https://github.com/OpenDroneMap/WebODM
- ExifTool: https://exiftool.org/

## License

This project is open-source software. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Roadmap

Future enhancements:
- [ ] Google Drive direct integration
- [ ] Batch processing multiple videos
- [ ] Real-time preview of extracted frames
- [ ] Custom WebODM processing presets
- [ ] Support for other drone models
- [ ] GPS path visualization
- [ ] Automated quality assessment
