# Dependency Installer

This installer automatically downloads and installs the required dependencies for DJI 3D Mapper:

- **FFmpeg**: Required for extracting frames from videos
- **ExifTool**: Required for injecting GPS metadata into images

## Usage

1. Run `Install_Dependencies.exe`
2. The installer will:
   - Check if FFmpeg and ExifTool are already installed
   - Download and install any missing dependencies
   - Add them to your system PATH automatically

3. Restart your terminal/command prompt for PATH changes to take effect

## Manual Installation

If the automatic installer fails, you can install manually:

### FFmpeg
1. Download from: https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your PATH

### ExifTool
1. Download from: https://exiftool.org/
2. Extract to a folder (e.g., `C:\exiftool`)
3. Rename `exiftool(-k).exe` to `exiftool.exe`
4. Add the folder to your PATH

## Troubleshooting

**"Failed to add to PATH"**
- Try running the installer as Administrator
- Or manually add the installation directories to PATH

**"Download failed"**
- Check your internet connection
- Firewall/antivirus might be blocking the download
- Try manual installation instead

**"ExifTool/FFmpeg not found after installation"**
- Restart your terminal/command prompt
- Or restart your computer
- Verify PATH was updated correctly in Environment Variables
