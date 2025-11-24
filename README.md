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
- **Interactive 3D Viewer**: Automatic CesiumJS-based 3D visualization in your browser
  - View 3D models directly after processing
  - Interactive controls for rotation, zoom, and pan
  - Terrain integration
  - Orthophoto overlay support
- **Export Options**: Save results to local folders or Google Drive

### User Interface
- Clean tabbed interface for step-by-step workflow
- Drag-and-drop file selection
- Real-time processing log
- Progress indicators
- Error handling and validation
- Automatic dependency management with installation wizards

## Requirements

### System Requirements
- Windows 10 or later
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space for processing
- Internet connection for first-run dependency downloads (if needed)

### Software Dependencies

#### Bundled with Application
- **FFmpeg**: Required for video frame extraction
  - Automatically bundled with the executable
  - Downloaded on first run if not bundled
- **ExifTool**: Required for geotagging images
  - Automatically bundled with the executable
  - Downloaded on first run if not bundled

#### Required for 3D Reconstruction
- **Docker Desktop**: Required for WebODM 3D map creation
  - Download from: https://www.docker.com/products/docker-desktop
  - Docker Desktop must be installed and running to use 3D reconstruction features
  - The application will guide you to install Docker if not present

#### Embedded Components
- **WebODM**: Embedded in the application
  - Included as a submodule from https://github.com/OpenDroneMap/WebODM
  - Automatically managed by the application
  - Requires Docker to run

## Installation

### Option 1: Download Pre-built Executable (Recommended)
1. Go to [Releases](https://github.com/Paisano7780/Video-SRT_to_3D_Map/releases)
2. Download the latest `DJI_3D_Mapper.exe`
3. Run the application
4. On first run, the application will:
   - Check for required dependencies (FFmpeg, ExifTool)
   - Automatically download and install any missing dependencies
   - Guide you to install Docker Desktop if you want 3D reconstruction features

### Option 2: Run from Source
```bash
# Clone repository with submodules
git clone --recurse-submodules https://github.com/Paisano7780/Video-SRT_to_3D_Map.git
cd Video-SRT_to_3D_Map

# If already cloned without submodules, initialize them:
git submodule update --init --recursive

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Install Docker Desktop for 3D reconstruction
# Download from https://www.docker.com/products/docker-desktop

# Run application
python main_app.py
```

The application will automatically check and install FFmpeg and ExifTool on first run if not already installed.

## Usage Guide

### Step 1: Prepare Your Files
1. Copy video files (`.MP4`) and telemetry files (`.SRT`) from your DJI Mini 3 drone
2. Ensure files have matching names (e.g., `DJI_0001.MP4` and `DJI_0001.SRT`)

### Step 2: Input Files
1. Open the application
2. Navigate to **"1. Input Files"** tab
3. Select video file (SRT will auto-detect if named correctly)
4. Choose buffer directory for geotagged images (the directory will be created automatically if it doesn't exist)

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

### Step 4: WebODM Integration & 3D Viewing
1. Go to **"3. WebODM"** tab
2. The embedded WebODM status will be displayed automatically
3. If WebODM is not running, click **"Start WebODM"** (first start may take several minutes to download Docker images)
4. Once WebODM is running, click **"Create 3D Map"**
5. The application will automatically start WebODM if needed
6. Wait for processing (can take 30 minutes to several hours depending on image count and quality settings)
7. **NEW:** After processing completes, a CesiumJS 3D viewer will automatically open in your browser
   - Interact with your 3D model in real-time
   - Use mouse controls to rotate, pan, and zoom
   - Toggle terrain and orthophoto layers
   - The viewer runs on a local web server (http://localhost:8080)

**Note:** WebODM runs in Docker containers managed by the application. Ensure Docker Desktop is running before using 3D map creation.

**Docker Not Installed?** The application will guide you through the Docker Desktop installation process if it's not detected.

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

### Dependencies Not Installed

The application now automatically handles dependency installation. If you encounter issues:

1. **FFmpeg or ExifTool Missing**
   - The application will detect missing dependencies on startup
   - It will prompt you to download and install them automatically
   - If automatic installation fails:
     - FFmpeg: Download from https://www.gyan.dev/ffmpeg/builds/
     - ExifTool: Download from https://exiftool.org/
     - Extract and add to your system PATH

2. **Docker Not Installed (for 3D reconstruction)**
   - Download Docker Desktop: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Restart the application
   - The 3D reconstruction features will become available

### "El sistema no puede encontrar el archivo especificado" (Windows)
This error occurs when FFmpeg is not accessible.

**Solution:**
- The application now bundles FFmpeg and should handle this automatically
- If the error persists, restart the application to trigger dependency check
- As a last resort, manually install FFmpeg and add to PATH

### "Docker is not installed" Error in WebODM Tab

**Solution:**
The application now includes an **interactive Docker installation wizard**:

1. When Docker is not detected, the application will automatically prompt you
2. Click "Yes" to open the Docker Desktop download page in your browser
3. Follow the installation instructions provided
4. After installing Docker Desktop:
   - Start Docker Desktop from the Start Menu
   - Wait for Docker to fully start (green icon in system tray)
   - The application will verify your installation
5. If verification fails, click "Check Status" in the WebODM tab to retry

**Manual Installation:**
1. Visit https://www.docker.com/products/docker-desktop
2. Download and install Docker Desktop
3. Start Docker Desktop
4. Restart the application

### Automatic Download Fails

If automatic dependency download fails:

**Firewall/Antivirus Issues:**
- Temporarily disable firewall/antivirus
- Run the application as Administrator
- Or manually download and install dependencies

**No Internet Connection:**
- Ensure you have an active internet connection
- The application requires internet only for first-run dependency downloads

### "Docker not found" or "Docker not running"
- Install Docker Desktop from https://www.docker.com/products/docker-desktop
- Start Docker Desktop application
- Wait for Docker to fully start (icon in system tray should show running)
- Restart the application

### "WebODM not found"
- Ensure you cloned the repository with submodules: `git clone --recurse-submodules`
- If already cloned, run: `git submodule update --init --recursive`
- Check that the `webodm` directory exists in the application folder

### "WebODM failed to start"
- Ensure Docker Desktop is running
- Check available disk space (WebODM needs at least 10GB)
- Check Docker logs for errors
- Try manually starting WebODM: `cd webodm && ./webodm.sh start` (Linux/Mac) or use Git Bash on Windows

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
├── webodm_manager.py     # WebODM lifecycle manager
├── dependency_manager.py # Dependency installation manager
├── cesium_viewer.py      # CesiumJS 3D viewer integration
├── test_*.py             # Unit tests
├── requirements.txt      # Python dependencies
├── webodm/               # Embedded WebODM (submodule)
└── .github/workflows/    # CI/CD workflows
```

## Credits

### Technologies Used
- **Python 3.10+**: Core language
- **FFmpeg**: Video processing
- **ExifTool**: Metadata manipulation
- **WebODM**: 3D reconstruction
- **CesiumJS**: Interactive 3D geospatial visualization
- **Docker**: Container runtime for WebODM
- **Tkinter**: GUI framework
- **Pandas/NumPy**: Data processing

### External Resources
- DJI telemetry format documentation
- WebODM API: https://github.com/OpenDroneMap/WebODM
- CesiumJS: https://cesium.com/platform/cesiumjs/
- ExifTool: https://exiftool.org/
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
