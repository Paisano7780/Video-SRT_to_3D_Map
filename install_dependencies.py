"""
Dependency Installer for DJI 3D Mapper
Downloads and installs FFmpeg and ExifTool if not present
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import tempfile
import winreg
from pathlib import Path


def check_ffmpeg_installed():
    """Check if FFmpeg is installed and in PATH"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_exiftool_installed():
    """Check if ExifTool is installed and in PATH"""
    try:
        result = subprocess.run(
            ['exiftool', '-ver'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def add_to_path(directory):
    """Add directory to user PATH environment variable"""
    try:
        # Open the user environment variables registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Environment',
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # Get current PATH
        try:
            current_path, _ = winreg.QueryValueEx(key, 'PATH')
        except WindowsError:
            current_path = ''
        
        # Add directory if not already in PATH
        if directory not in current_path:
            new_path = f"{current_path};{directory}" if current_path else directory
            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✓ Added {directory} to PATH")
            
            # Broadcast environment change
            subprocess.run(
                ['setx', 'PATH', new_path],
                capture_output=True,
                timeout=10
            )
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"✗ Failed to add to PATH: {e}")
        return False


def download_with_progress(url, filepath):
    """Download file with progress indicator"""
    print(f"Downloading {os.path.basename(filepath)}...")
    
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f'\r{percent}% ')
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, filepath, reporthook)
    print()  # New line after progress


def install_ffmpeg(install_dir):
    """Download and install FFmpeg"""
    print("=" * 60)
    print("Installing FFmpeg...")
    print("=" * 60)
    
    ffmpeg_dir = os.path.join(install_dir, 'ffmpeg')
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # Download FFmpeg essentials build
    url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
    zip_path = os.path.join(tempfile.gettempdir(), 'ffmpeg.zip')
    
    try:
        download_with_progress(url, zip_path)
        
        # Extract
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract to temp directory first
            temp_extract = os.path.join(tempfile.gettempdir(), 'ffmpeg_extract')
            zip_ref.extractall(temp_extract)
        
        # Find the bin directory and copy executables
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
        
        # Add to PATH
        add_to_path(ffmpeg_dir)
        
        print(f"✓ FFmpeg installed to {ffmpeg_dir}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to install FFmpeg: {e}")
        print("Please download manually from: https://ffmpeg.org/download.html")
        return False


def install_exiftool(install_dir):
    """Download and install ExifTool"""
    print("=" * 60)
    print("Installing ExifTool...")
    print("=" * 60)
    
    exiftool_dir = os.path.join(install_dir, 'exiftool')
    os.makedirs(exiftool_dir, exist_ok=True)
    
    # Download ExifTool
    url = 'https://exiftool.org/exiftool-12.76_64.zip'
    zip_path = os.path.join(tempfile.gettempdir(), 'exiftool.zip')
    
    try:
        download_with_progress(url, zip_path)
        
        # Extract
        print("Extracting ExifTool...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(exiftool_dir)
        
        # Rename exiftool(-k).exe to exiftool.exe
        for file in os.listdir(exiftool_dir):
            if file == 'exiftool(-k).exe':
                os.rename(
                    os.path.join(exiftool_dir, file),
                    os.path.join(exiftool_dir, 'exiftool.exe')
                )
                break
        
        # Clean up
        os.remove(zip_path)
        
        # Add to PATH
        add_to_path(exiftool_dir)
        
        print(f"✓ ExifTool installed to {exiftool_dir}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to install ExifTool: {e}")
        print("Please download manually from: https://exiftool.org/")
        return False


def main():
    """Main installer function"""
    print("=" * 60)
    print("DJI 3D Mapper - Dependency Installer")
    print("=" * 60)
    print()
    
    # Determine installation directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        install_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        install_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Installation directory: {install_dir}")
    print()
    
    # Check what's already installed
    ffmpeg_ok = check_ffmpeg_installed()
    exiftool_ok = check_exiftool_installed()
    
    if ffmpeg_ok:
        print("✓ FFmpeg is already installed")
    if exiftool_ok:
        print("✓ ExifTool is already installed")
    
    # Install missing dependencies
    if not ffmpeg_ok:
        if not install_ffmpeg(install_dir):
            print("\n⚠ Warning: FFmpeg installation failed")
    
    if not exiftool_ok:
        if not install_exiftool(install_dir):
            print("\n⚠ Warning: ExifTool installation failed")
    
    print()
    print("=" * 60)
    if ffmpeg_ok and exiftool_ok:
        print("✓ All dependencies are already installed!")
    elif check_ffmpeg_installed() and check_exiftool_installed():
        print("✓ Installation complete!")
        print("\nPlease restart your command prompt or terminal")
        print("for PATH changes to take effect.")
    else:
        print("⚠ Some dependencies could not be installed automatically.")
        print("\nPlease install manually:")
        if not check_ffmpeg_installed():
            print("  - FFmpeg: https://ffmpeg.org/download.html")
        if not check_exiftool_installed():
            print("  - ExifTool: https://exiftool.org/")
    print("=" * 60)
    
    input("\nPress Enter to exit...")


if __name__ == '__main__':
    if sys.platform != 'win32':
        print("This installer is only for Windows")
        sys.exit(1)
    
    main()
