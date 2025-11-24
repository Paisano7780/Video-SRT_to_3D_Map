"""
Dependency Manager for DJI 3D Mapper
Handles checking, downloading, and installing dependencies
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import tempfile
import webbrowser
from pathlib import Path
from typing import Tuple, Optional
import tkinter as tk
from tkinter import messagebox

# Import Windows-specific modules only on Windows
if sys.platform == 'win32':
    import winreg


class DependencyManager:
    """Manages application dependencies"""
    
    # ExifTool - using LATEST_64 for Windows 64-bit standalone executable
    # This URL always points to the latest 64-bit version
    EXIFTOOL_URL = "https://exiftool.org/exiftool-LATEST_64.zip"
    
    # FFmpeg essentials build
    FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    def __init__(self, app_dir: Optional[str] = None):
        """
        Initialize dependency manager
        
        Args:
            app_dir: Application directory for installing dependencies
        """
        if app_dir is None:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.app_dir = app_dir
        self.deps_dir = os.path.join(app_dir, 'dependencies')
        os.makedirs(self.deps_dir, exist_ok=True)
        
    def check_ffmpeg_installed(self) -> bool:
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
    
    def check_exiftool_installed(self) -> bool:
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
    
    def check_docker_installed(self) -> bool:
        """Check if Docker is installed"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_docker_running(self) -> bool:
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def prompt_docker_installation(self, parent_window=None) -> bool:
        """
        Prompt user to install Docker Desktop and guide them through the process
        
        Args:
            parent_window: Optional parent window for dialogs
            
        Returns:
            True if user confirms they installed Docker, False otherwise
        """
        from config import DOCKER_DESKTOP_URL
        
        message = (
            "Docker Desktop is required for 3D reconstruction features.\n\n"
            "Docker Desktop is not currently installed on your system.\n\n"
            "Would you like to:\n"
            "1. Open the Docker Desktop download page now?\n"
            "2. Install Docker Desktop\n"
            "3. Restart this application after installation\n\n"
            "Note: Docker Desktop installation requires administrator privileges "
            "and a system restart may be required."
        )
        
        response = messagebox.askyesno(
            "Docker Desktop Required",
            message,
            icon='warning'
        )
        
        if response:
            # Open Docker Desktop download page
            try:
                webbrowser.open(DOCKER_DESKTOP_URL)
                
                # Show installation instructions
                instructions = (
                    "Docker Desktop download page has been opened in your browser.\n\n"
                    "Installation Steps:\n"
                    "1. Download Docker Desktop for Windows\n"
                    "2. Run the installer (requires administrator privileges)\n"
                    "3. Follow the installation wizard\n"
                    "4. Restart your computer if prompted\n"
                    "5. Start Docker Desktop from the Start Menu\n"
                    "6. Wait for Docker to fully start (green icon in system tray)\n"
                    "7. Restart this application\n\n"
                    "Click OK when you have completed the installation."
                )
                
                messagebox.showinfo("Docker Desktop Installation", instructions)
                
                # Ask if user has completed installation
                completed = messagebox.askyesno(
                    "Installation Completed?",
                    "Have you completed the Docker Desktop installation and started Docker?\n\n"
                    "Click 'Yes' to verify Docker installation.\n"
                    "Click 'No' to continue without Docker (3D features will be disabled)."
                )
                
                return completed
                
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to open Docker download page: {e}\n\n"
                    f"Please manually visit: {DOCKER_DESKTOP_URL}"
                )
                return False
        
        return False
    
    def verify_docker_installation(self, parent_window=None) -> Tuple[bool, str]:
        """
        Verify Docker installation after user claims to have installed it
        
        Args:
            parent_window: Optional parent window for dialogs
            
        Returns:
            Tuple of (success, message)
        """
        if not self.check_docker_installed():
            return False, (
                "Docker Desktop is still not detected.\n\n"
                "Please ensure:\n"
                "1. Docker Desktop is fully installed\n"
                "2. You have restarted your computer (if required)\n"
                "3. Docker Desktop is running\n\n"
                "You may need to restart this application after installation."
            )
        
        if not self.check_docker_running():
            return False, (
                "Docker is installed but not running.\n\n"
                "Please start Docker Desktop from the Start Menu and wait for it to fully start.\n"
                "Look for the Docker icon in the system tray - it should show 'Docker Desktop is running'."
            )
        
        return True, "Docker Desktop is installed and running successfully!"
    
    def get_bundled_ffmpeg_path(self) -> Optional[str]:
        """Get path to bundled FFmpeg if it exists"""
        # Check if FFmpeg is bundled with the executable
        if getattr(sys, 'frozen', False):
            # PyInstaller bundles files in sys._MEIPASS
            bundled_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg.exe')
            if os.path.exists(bundled_path):
                return os.path.dirname(bundled_path)
        
        # Check dependencies directory
        deps_ffmpeg = os.path.join(self.deps_dir, 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(deps_ffmpeg):
            return os.path.dirname(deps_ffmpeg)
        
        return None
    
    def get_bundled_exiftool_path(self) -> Optional[str]:
        """Get path to bundled ExifTool if it exists"""
        # Check if ExifTool is bundled with the executable
        if getattr(sys, 'frozen', False):
            bundled_path = os.path.join(sys._MEIPASS, 'exiftool.exe')
            if os.path.exists(bundled_path):
                return sys._MEIPASS
        
        # Check dependencies directory
        deps_exiftool = os.path.join(self.deps_dir, 'exiftool', 'exiftool.exe')
        if os.path.exists(deps_exiftool):
            return os.path.dirname(deps_exiftool)
        
        return None
    
    def add_to_path(self, directory: str) -> bool:
        """Add directory to user PATH environment variable"""
        if sys.platform != 'win32':
            return False
        
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
            except OSError:
                current_path = ''
            
            # Add directory if not already in PATH
            if directory not in current_path:
                # Clean up current path (remove trailing semicolon if present)
                current_path = current_path.rstrip(';')
                new_path = f"{current_path};{directory}" if current_path else directory
                winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                
                # Also set for current process
                os.environ['PATH'] = new_path
                
                # Broadcast environment change (best effort)
                try:
                    subprocess.run(
                        ['setx', 'PATH', new_path],
                        capture_output=True,
                        timeout=10
                    )
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    pass  # setx is optional, don't fail if it doesn't work
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Failed to add to PATH: {e}")
            return False
    
    def download_with_progress(self, url: str, filepath: str, progress_callback=None) -> bool:
        """
        Download file with optional progress callback
        
        Args:
            url: URL to download from
            filepath: Destination file path
            progress_callback: Optional callback(current, total, percentage)
            
        Returns:
            True if successful
        """
        try:
            def reporthook(count, block_size, total_size):
                if progress_callback and total_size > 0:
                    current = count * block_size
                    percentage = min(100, int(current * 100 / total_size))
                    progress_callback(current, total_size, percentage)
            
            urllib.request.urlretrieve(url, filepath, reporthook)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def install_ffmpeg(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Download and install FFmpeg
        
        Args:
            progress_callback: Optional callback(current, total, percentage)
            
        Returns:
            Tuple of (success, message)
        """
        ffmpeg_dir = os.path.join(self.deps_dir, 'ffmpeg')
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        zip_path = os.path.join(tempfile.gettempdir(), 'ffmpeg.zip')
        
        try:
            # Download
            if not self.download_with_progress(self.FFMPEG_URL, zip_path, progress_callback):
                return False, "Failed to download FFmpeg"
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                temp_extract = os.path.join(tempfile.gettempdir(), 'ffmpeg_extract')
                zip_ref.extractall(temp_extract)
            
            # Find and copy executables
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
            self.add_to_path(ffmpeg_dir)
            
            return True, f"FFmpeg installed to {ffmpeg_dir}"
            
        except Exception as e:
            return False, f"Failed to install FFmpeg: {str(e)}"
    
    def install_exiftool(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Download and install ExifTool
        
        Args:
            progress_callback: Optional callback(current, total, percentage)
            
        Returns:
            Tuple of (success, message)
        """
        exiftool_dir = os.path.join(self.deps_dir, 'exiftool')
        os.makedirs(exiftool_dir, exist_ok=True)
        
        zip_path = os.path.join(tempfile.gettempdir(), 'exiftool.zip')
        
        try:
            # Download
            if not self.download_with_progress(self.EXIFTOOL_URL, zip_path, progress_callback):
                return False, "Failed to download ExifTool"
            
            # Extract and rename exiftool(-k).exe to exiftool.exe
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Search for the exiftool(-k).exe file in the ZIP
                exiftool_found = False
                for member in zip_ref.namelist():
                    if 'exiftool(-k).exe' in member:
                        # Extract the file
                        zip_ref.extract(member, path=exiftool_dir)
                        
                        # Get paths
                        original_path = os.path.join(exiftool_dir, member)
                        final_path = os.path.join(exiftool_dir, 'exiftool.exe')
                        
                        # Rename to exiftool.exe
                        os.rename(original_path, final_path)
                        exiftool_found = True
                        break
                
                if not exiftool_found:
                    return False, "ExifTool executable not found in downloaded archive"
            
            # Clean up
            os.remove(zip_path)
            
            # Add to PATH
            self.add_to_path(exiftool_dir)
            
            return True, f"ExifTool installed to {exiftool_dir}"
            
        except Exception as e:
            return False, f"Failed to install ExifTool: {str(e)}"
    
    def check_all_dependencies(self) -> dict:
        """
        Check status of all dependencies
        
        Returns:
            Dictionary with dependency status
        """
        # First check if bundled versions exist
        bundled_ffmpeg = self.get_bundled_ffmpeg_path()
        bundled_exiftool = self.get_bundled_exiftool_path()
        
        # If bundled, add to PATH
        if bundled_ffmpeg:
            self.add_to_path(bundled_ffmpeg)
        if bundled_exiftool:
            self.add_to_path(bundled_exiftool)
        
        return {
            'ffmpeg': {
                'installed': self.check_ffmpeg_installed(),
                'bundled': bundled_ffmpeg is not None,
                'bundled_path': bundled_ffmpeg
            },
            'exiftool': {
                'installed': self.check_exiftool_installed(),
                'bundled': bundled_exiftool is not None,
                'bundled_path': bundled_exiftool
            },
            'docker': {
                'installed': self.check_docker_installed(),
                'running': self.check_docker_running()
            }
        }
    
    def ensure_dependencies(self, parent_window=None) -> Tuple[bool, str]:
        """
        Ensure all required dependencies are available
        
        Args:
            parent_window: Optional parent window for dialogs
            
        Returns:
            Tuple of (success, message)
        """
        status = self.check_all_dependencies()
        
        missing = []
        if not status['ffmpeg']['installed']:
            missing.append('FFmpeg')
        if not status['exiftool']['installed']:
            missing.append('ExifTool')
        
        if not missing:
            return True, "All dependencies are installed"
        
        # Ask user if they want to download missing dependencies
        if parent_window:
            response = messagebox.askyesno(
                "Missing Dependencies",
                f"The following dependencies are missing:\n" +
                "\n".join(f"  - {dep}" for dep in missing) +
                f"\n\nWould you like to download and install them now?\n" +
                f"(This will download approximately 50-100 MB)"
            )
            
            if not response:
                return False, "User cancelled dependency installation"
        
        # Install missing dependencies
        failures = []
        
        if not status['ffmpeg']['installed']:
            success, msg = self.install_ffmpeg()
            if not success:
                failures.append(f"FFmpeg: {msg}")
        
        if not status['exiftool']['installed']:
            success, msg = self.install_exiftool()
            if not success:
                failures.append(f"ExifTool: {msg}")
        
        if failures:
            return False, "Some dependencies failed to install:\n" + "\n".join(failures)
        
        return True, "All dependencies installed successfully"


def show_dependency_setup_wizard(parent=None):
    """
    Show a setup wizard for installing dependencies
    
    Args:
        parent: Optional parent window
        
    Returns:
        True if setup completed successfully
    """
    manager = DependencyManager()
    status = manager.check_all_dependencies()
    
    # Build status message
    messages = []
    needs_setup = False
    
    # FFmpeg
    if status['ffmpeg']['installed']:
        messages.append("✓ FFmpeg is installed")
    elif status['ffmpeg']['bundled']:
        messages.append("⚠ FFmpeg is bundled but not in PATH (will be added automatically)")
    else:
        messages.append("✗ FFmpeg is not installed")
        needs_setup = True
    
    # ExifTool
    if status['exiftool']['installed']:
        messages.append("✓ ExifTool is installed")
    elif status['exiftool']['bundled']:
        messages.append("⚠ ExifTool is bundled but not in PATH (will be added automatically)")
    else:
        messages.append("✗ ExifTool is not installed")
        needs_setup = True
    
    # Docker
    if status['docker']['installed']:
        if status['docker']['running']:
            messages.append("✓ Docker is installed and running")
        else:
            messages.append("⚠ Docker is installed but not running\n  (Start Docker Desktop to use 3D reconstruction features)")
    else:
        messages.append("⚠ Docker is not installed\n  (Required for 3D reconstruction - download from https://www.docker.com/products/docker-desktop)")
    
    if not needs_setup:
        return True
    
    # Show setup dialog
    message = "Dependency Status:\n\n" + "\n".join(messages)
    message += "\n\nWould you like to download and install missing dependencies?"
    
    if messagebox.askyesno("Dependency Setup", message):
        success, msg = manager.ensure_dependencies(parent)
        if success:
            messagebox.showinfo("Success", "Dependencies installed successfully!\n\n" + msg)
            return True
        else:
            messagebox.showerror("Error", "Failed to install dependencies:\n\n" + msg)
            return False
    
    return False
