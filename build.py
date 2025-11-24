"""
Build script for creating Windows executable
Run this script to build the application:

    python build.py

Requirements:
- PyInstaller installed (pip install pyinstaller)
- ExifTool downloaded and in exiftool/ directory
"""

import os
import sys
import subprocess
import urllib.request
import zipfile

# ExifTool version to download
EXIFTOOL_VERSION = "12.76_64"


def download_exiftool():
    """Download ExifTool if not present"""
    exiftool_dir = "exiftool"
    exiftool_exe = os.path.join(exiftool_dir, "exiftool.exe")
    
    if os.path.exists(exiftool_exe):
        print(f"✓ ExifTool already present at {exiftool_exe}")
        return exiftool_exe
    
    print("⏳ Downloading ExifTool...")
    os.makedirs(exiftool_dir, exist_ok=True)
    
    url = f"https://exiftool.org/exiftool-{EXIFTOOL_VERSION}.zip"
    zip_path = "exiftool.zip"
    
    try:
        urllib.request.urlretrieve(url, zip_path)
        
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
        print("Please download manually from: https://exiftool.org/")
        return None


def build_executable():
    """Build the Windows executable using PyInstaller"""
    print("=" * 60)
    print("Building DJI_3D_Mapper executable")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Download ExifTool
    exiftool_path = download_exiftool()
    if not exiftool_path:
        print("⚠ Warning: ExifTool not available. Build will continue but may not work.")
    
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
    
    # Add ExifTool if available
    if exiftool_path and os.path.exists(exiftool_path):
        cmd.append(f"--add-binary={exiftool_path};.")
    
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
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False
    
    # Build dependency installer
    print("\n" + "=" * 60)
    print("Building dependency installer...")
    print("=" * 60)
    
    installer_cmd = [
        "pyinstaller",
        "--name=Install_Dependencies",
        "--onefile",
        "--console",
        "--clean",
        "--noconfirm",
        "install_dependencies.py"
    ]
    
    print(f"⏳ Running PyInstaller for installer...")
    
    try:
        subprocess.run(installer_cmd, check=True)
        print("✓ Dependency installer built successfully!")
        
        print("=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
        print(f"Main application: dist/DJI_3D_Mapper.exe")
        print(f"Dependency installer: dist/Install_Dependencies.exe")
        print()
        print("Next steps:")
        print("1. Run Install_Dependencies.exe to install FFmpeg and ExifTool")
        print("2. Test the DJI_3D_Mapper.exe application")
        print("3. Ensure WebODM is running (for 3D reconstruction)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Installer build failed: {e}")
        print("Main application is still available in dist/")
        return False


if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
