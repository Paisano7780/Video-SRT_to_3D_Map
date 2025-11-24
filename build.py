"""
Build script for creating Windows executable with bundled dependencies
Run this script to build the application:

    python build.py

Requirements:
- PyInstaller installed (pip install pyinstaller)
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import tempfile

# Dependency versions and URLs
EXIFTOOL_VERSION = "12.76"
# Note: ExifTool Windows standalone uses format exiftool-VERSION.zip (not VERSION_64)
EXIFTOOL_URL = f"https://exiftool.org/exiftool-{EXIFTOOL_VERSION}.zip"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def download_exiftool():
    """Download ExifTool if not present"""
    exiftool_dir = "bundled_deps/exiftool"
    exiftool_exe = os.path.join(exiftool_dir, "exiftool.exe")
    
    if os.path.exists(exiftool_exe):
        print(f"✓ ExifTool already present at {exiftool_exe}")
        return exiftool_exe
    
    print("⏳ Downloading ExifTool...")
    os.makedirs(exiftool_dir, exist_ok=True)
    
    zip_path = os.path.join(tempfile.gettempdir(), "exiftool.zip")
    
    try:
        print(f"  URL: {EXIFTOOL_URL}")
        urllib.request.urlretrieve(EXIFTOOL_URL, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(exiftool_dir)
        
        # Rename exiftool(-k).exe to exiftool.exe
        original = os.path.join(exiftool_dir, "exiftool(-k).exe")
        if os.path.exists(original):
            os.rename(original, exiftool_exe)
        
        os.remove(zip_path)
        print(f"✓ ExifTool downloaded to {exiftool_exe}")
        return exiftool_exe
        
    except Exception as e:
        print(f"✗ Failed to download ExifTool: {e}")
        print("  Note: ExifTool will be downloaded on first run if bundling fails")
        return None


def download_ffmpeg():
    """Download FFmpeg if not present"""
    ffmpeg_dir = "bundled_deps/ffmpeg"
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_exe):
        print(f"✓ FFmpeg already present at {ffmpeg_exe}")
        return ffmpeg_dir
    
    print("⏳ Downloading FFmpeg (this may take a while, ~70MB)...")
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    zip_path = os.path.join(tempfile.gettempdir(), "ffmpeg.zip")
    
    try:
        print(f"  URL: {FFMPEG_URL}")
        
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f'\r  Progress: {percent}% ')
                sys.stdout.flush()
        
        urllib.request.urlretrieve(FFMPEG_URL, zip_path, reporthook)
        print()  # New line after progress
        
        # Extract
        print("  Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            temp_extract = os.path.join(tempfile.gettempdir(), 'ffmpeg_extract')
            zip_ref.extractall(temp_extract)
        
        # Find and copy executables from bin directory
        for root, dirs, files in os.walk(temp_extract):
            if 'bin' in dirs:
                bin_dir = os.path.join(root, 'bin')
                for file in os.listdir(bin_dir):
                    if file.endswith('.exe'):
                        shutil.copy2(
                            os.path.join(bin_dir, file),
                            os.path.join(ffmpeg_dir, file)
                        )
                break
        
        # Clean up
        os.remove(zip_path)
        shutil.rmtree(temp_extract, ignore_errors=True)
        
        print(f"✓ FFmpeg downloaded to {ffmpeg_dir}")
        return ffmpeg_dir
        
    except Exception as e:
        print(f"✗ Failed to download FFmpeg: {e}")
        print("  Note: FFmpeg will be downloaded on first run if bundling fails")
        return None


def build_executable():
    """Build the Windows executable using PyInstaller"""
    print("=" * 60)
    print("Building DJI_3D_Mapper with bundled dependencies")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Download dependencies
    print("\n" + "=" * 60)
    print("Downloading bundled dependencies...")
    print("=" * 60)
    
    exiftool_path = download_exiftool()
    ffmpeg_dir = download_ffmpeg()
    
    # Build main application
    print("\n" + "=" * 60)
    print("Building main application...")
    print("=" * 60)
    
    cmd = [
        "pyinstaller",
        "--name=DJI_3D_Mapper",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
    ]
    
    # Add bundled dependencies if available
    if exiftool_path and os.path.exists(exiftool_path):
        cmd.append(f"--add-binary={exiftool_path};.")
        print(f"  ✓ Bundling ExifTool: {exiftool_path}")
    else:
        print("  ⚠ ExifTool not bundled - will be downloaded on first run")
    
    if ffmpeg_dir and os.path.exists(ffmpeg_dir):
        # Bundle entire ffmpeg directory
        cmd.append(f"--add-data={ffmpeg_dir};ffmpeg")
        print(f"  ✓ Bundling FFmpeg directory: {ffmpeg_dir}")
    else:
        print("  ⚠ FFmpeg not bundled - will be downloaded on first run")
    
    # Add the new modules
    cmd.append("--add-data=dependency_manager.py;.")
    cmd.append("--add-data=cesium_viewer.py;.")
    
    # Hidden imports
    hidden_imports = [
        "pandas",
        "numpy",
        "tkinter",
        "requests",
        "json",
        "threading",
        "re",
        "subprocess",
        "http.server",
        "socketserver",
        "webbrowser",
        "atexit",
    ]
    
    for module in hidden_imports:
        cmd.append(f"--hidden-import={module}")
    
    # Main script
    cmd.append("main_app.py")
    
    print(f"⏳ Running PyInstaller for main app...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ Main application built successfully!")
        
        print("\n" + "=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
        print(f"Executable: dist/DJI_3D_Mapper.exe")
        print()
        print("Application features:")
        print("  ✓ Dependencies bundled (FFmpeg & ExifTool)")
        print("  ✓ Automatic dependency checking on startup")
        print("  ✓ Downloads missing dependencies if needed")
        print()
        print("Next steps:")
        print("1. Test the DJI_3D_Mapper.exe application")
        print("2. Install Docker Desktop for 3D reconstruction features")
        print("   Download: https://www.docker.com/products/docker-desktop")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False


if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
