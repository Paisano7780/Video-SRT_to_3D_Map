# Quick Start Guide

Get started with DJI Video to 3D Map Pipeline in minutes!

## Prerequisites

### Required Software

1. **Windows 10 or later**

2. **FFmpeg** (for video processing)
   - Download: https://www.gyan.dev/ffmpeg/builds/
   - Choose: `ffmpeg-release-essentials.zip`
   - Extract to `C:\ffmpeg`
   - Add to PATH:
     ```
     C:\ffmpeg\bin
     ```
   - Verify installation:
     ```cmd
     ffmpeg -version
     ```

3. **WebODM** (for 3D reconstruction)
   
   **Option A: Docker (Recommended)**
   ```cmd
   # Install Docker Desktop for Windows
   # Download from: https://www.docker.com/products/docker-desktop
   
   # Clone WebODM
   git clone https://github.com/OpenDroneMap/WebODM
   cd WebODM
   
   # Start WebODM
   docker-compose up
   ```
   
   **Option B: Native Installation**
   - Follow: https://github.com/OpenDroneMap/WebODM#windows-installation

## Installation

### Option 1: Download Executable (Easiest)

1. Go to [Releases](https://github.com/Paisano7780/Video-SRT_to_3D_Map/releases)
2. Download latest `DJI_3D_Mapper.exe`
3. Run the application - no installation needed!

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/Paisano7780/Video-SRT_to_3D_Map.git
cd Video-SRT_to_3D_Map

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main_app.py
```

## First Run

### Step 1: Prepare Your Data

1. Connect your DJI Mini 3 drone to your computer
2. Copy video files from `DCIM/100MEDIA/`:
   - `DJI_0001.MP4` (video)
   - `DJI_0001.SRT` (telemetry)

### Step 2: Start WebODM

```cmd
cd WebODM
docker-compose up
```

Wait for message: `WebODM is ready at http://localhost:8000`

### Step 3: Run DJI_3D_Mapper

1. **Launch** the application
2. **Input Tab:**
   - Click "Browse" for Video File
   - Select your `.MP4` file
   - SRT file should auto-detect
   - Choose a Buffer Directory (default is fine)

3. **Processing Tab:**
   - Set Frame Rate: `1.0` fps (recommended)
   - Click "Start Processing Pipeline"
   - Wait for completion (2-5 minutes for a 1-minute video)

4. **WebODM Tab:**
   - URL: `http://localhost:8000`
   - Username: `admin`
   - Password: `admin`
   - Click "Test Connection"
   - Click "Create 3D Map"
   - Wait for processing (30-120 minutes depending on images)

5. **Output Tab:**
   - Choose output directory
   - Click "Export Results"
   - Open the `all.zip` file to view your 3D model!

## Example Workflow

```
1. [Input] Select DJI_0001.MP4 and DJI_0001.SRT
2. [Process] Extract frames @ 1 fps → ~60 images for 1-min video
3. [Process] Geotag images with GPS coordinates
4. [WebODM] Upload images and start reconstruction
5. [Output] Download 3D model, orthophoto, and DSM
```

## Viewing Results

### 3D Model
- Extract `all.zip`
- Open `odm_texturing/odm_textured_model_geo.obj` in:
  - **Blender** (free): https://www.blender.org/
  - **MeshLab** (free): https://www.meshlab.net/
  - **CloudCompare** (free): https://www.cloudcompare.org/

### Orthophoto
- Open `odm_orthophoto/odm_orthophoto.tif` in:
  - **QGIS** (free GIS): https://qgis.org/

### Point Cloud
- Open `odm_georeferencing/odm_georeferenced_model.laz` in:
  - **CloudCompare**
  - **Potree** (web viewer)

## Common Issues

### "FFmpeg not found"
```cmd
# Check PATH
echo %PATH%

# Should include: C:\ffmpeg\bin

# If not, add it:
setx PATH "%PATH%;C:\ffmpeg\bin"

# Restart application
```

### "WebODM connection failed"
```cmd
# Check if Docker is running
docker ps

# Restart WebODM
cd WebODM
docker-compose restart

# Check logs
docker-compose logs -f
```

### "Not enough images"
- Increase frame rate to 2 fps
- Or use longer video (>30 seconds)
- Minimum: 20 images recommended

### "Processing is very slow"
- **Normal**: 3D reconstruction takes time
- **For 100 images**: ~30-60 minutes
- **For 500 images**: ~2-3 hours
- **Tips**:
  - Use lower frame rate (0.5 fps)
  - Process shorter video segments
  - Upgrade WebODM server specs

## Tips for Best Results

### Video Recording
- ✅ Fly at constant altitude
- ✅ Maintain 70-80% image overlap
- ✅ Use manual camera settings
- ✅ Avoid strong shadows
- ✅ Fly in good lighting conditions
- ❌ Don't fly too fast
- ❌ Don't make sudden movements

### Processing Settings
- **Nadir mapping**: 1 fps, gimbal at -90°
- **Structure/Orbit**: 2 fps, gimbal at -45°
- **Large areas**: 0.5 fps, higher altitude
- **Detailed objects**: 2 fps, lower altitude

### Quality vs Speed
| Setting | Images | Time | Quality |
|---------|--------|------|---------|
| 0.5 fps | Low    | Fast | Good    |
| 1.0 fps | Medium | Med  | Better  |
| 2.0 fps | High   | Slow | Best    |

## Next Steps

1. **Experiment** with different frame rates
2. **Try** different flight patterns
3. **Compare** nadir vs orbit reconstructions
4. **Share** your results!

## Getting Help

- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/Paisano7780/Video-SRT_to_3D_Map/issues
- **WebODM Docs**: https://docs.opendronemap.org/

## Sample Data

Test the application with provided sample data:
```
sample_data/DJI_0001.SRT
```

Note: You'll need to provide your own MP4 file for testing.

---

**Happy Mapping! 🚁📍🗺️**
