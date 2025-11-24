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
    
    def check_docker_desktop_exists(self) -> bool:
        """
        Check if Docker Desktop executable exists at standard installation path
        
        Returns:
            True if Docker Desktop.exe exists
        """
        from config import DOCKER_DESKTOP_INSTALL_PATH
        return os.path.exists(DOCKER_DESKTOP_INSTALL_PATH)
    
    def is_admin(self) -> bool:
        """
        Check if the current process has administrator privileges (Windows only)
        
        Returns:
            True if running with admin privileges
        """
        if sys.platform != 'win32':
            return False
        
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def download_docker_installer(self, progress_callback=None) -> Optional[str]:
        """
        Download Docker Desktop installer
        
        Args:
            progress_callback: Optional callback(current, total, percentage)
            
        Returns:
            Path to downloaded installer, or None if failed
        """
        from config import DOCKER_DESKTOP_INSTALLER_URL, DOCKER_DESKTOP_INSTALLER_FILENAME
        
        installer_path = os.path.join(tempfile.gettempdir(), DOCKER_DESKTOP_INSTALLER_FILENAME)
        
        # If already downloaded, return existing path
        if os.path.exists(installer_path):
            return installer_path
        
        try:
            if not self.download_with_progress(
                DOCKER_DESKTOP_INSTALLER_URL, 
                installer_path, 
                progress_callback
            ):
                return None
            
            return installer_path
        except Exception as e:
            # Return None on error - caller will handle the failure
            return None
    
    def elevate_and_run_installer(self, installer_path: str) -> Tuple[bool, str]:
        """
        Run Docker installer with UAC elevation if needed
        
        Args:
            installer_path: Path to Docker Desktop installer
            
        Returns:
            Tuple of (success, message)
        """
        if sys.platform != 'win32':
            return False, "UAC elevation is only supported on Windows"
        
        try:
            import ctypes
            
            # ShellExecute with 'runas' verb to trigger UAC elevation
            # Parameters: hwnd, operation, file, parameters, directory, show_cmd
            ret = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # Trigger UAC elevation
                installer_path,
                "install --quiet --accept-license --backend=wsl-2",  # Installation parameters with WSL 2 backend
                None,
                1  # SW_SHOWNORMAL
            )
            
            # ShellExecute returns > 32 on success
            if ret > 32:
                return True, "Installation started with elevated privileges"
            else:
                return False, f"Failed to elevate installer (error code: {ret})"
                
        except Exception as e:
            return False, f"UAC elevation failed: {str(e)}"
    
    def install_docker_desktop(self, installer_path: str, parent_window=None) -> Tuple[bool, str]:
        """
        Install Docker Desktop using silent installation with WSL 2 backend
        
        Args:
            installer_path: Path to Docker Desktop installer
            parent_window: Optional parent window for dialogs
            
        Returns:
            Tuple of (success, message)
        """
        if sys.platform != 'win32':
            return False, "Docker Desktop automated installation is only supported on Windows"
        
        if not os.path.exists(installer_path):
            return False, f"Installer not found at: {installer_path}"
        
        # Check for admin privileges
        if not self.is_admin():
            # Try to elevate privileges using UAC
            messagebox.showinfo(
                "Administrator Privileges Required",
                "Docker Desktop installation requires administrator privileges.\n\n"
                "A User Account Control (UAC) prompt will appear.\n"
                "Please click 'Yes' to allow the installation to proceed.",
                icon='info'
            )
            
            success, message = self.elevate_and_run_installer(installer_path)
            
            if not success:
                return False, (
                    "Failed to run installer with administrator privileges.\n\n"
                    "Please try:\n"
                    "1. Close this application\n"
                    "2. Right-click the application icon\n"
                    "3. Select 'Run as administrator'\n"
                    "4. Try the installation again\n\n"
                    f"Error: {message}"
                )
            
            # Installation started with elevation, inform user to wait
            return True, (
                "Docker Desktop installation has been started with administrator privileges.\n\n"
                "Please wait for the installation to complete.\n"
                "This may take 5-10 minutes."
            )
        
        try:
            # Execute silent installation with WSL 2 backend and license acceptance
            # Run the installation command using subprocess.run
            # We use a list to avoid shell injection
            result = subprocess.run(
                ['cmd', '/c', 'start', '/wait', '', installer_path, 
                 'install', '--quiet', '--accept-license', '--backend=wsl-2'],
                capture_output=True,
                timeout=600,  # 10 minutes timeout
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0:
                return True, "Docker Desktop installation completed successfully with WSL 2 backend"
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "Unknown error"
                return False, (
                    f"Installation failed with code {result.returncode}: {error_msg}\n\n"
                    "Please ensure:\n"
                    "• You are running as Administrator\n"
                    "• WSL 2 is installed on your system\n"
                    "• Your Windows version supports WSL 2 (Windows 10 version 1903 or higher)"
                )
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out after 10 minutes"
        except Exception as e:
            return False, (
                f"Installation failed: {str(e)}\n\n"
                "Please ensure:\n"
                "• You are running as Administrator\n"
                "• WSL 2 is installed on your system"
            )
    
    def prompt_restart_for_docker(self, parent_window=None) -> bool:
        """
        Show dialog informing user that a restart is required for Docker
        
        Args:
            parent_window: Optional parent window for dialogs
            
        Returns:
            True if user acknowledges restart requirement
        """
        message = (
            "Docker Desktop installation requires a system restart.\n\n"
            "This is necessary to enable Windows virtualization features (Hyper-V or WSL2).\n\n"
            "What to do next:\n"
            "1. Click OK to acknowledge this message\n"
            "2. Save any open work\n"
            "3. Restart your computer\n"
            "4. After restart, start Docker Desktop from the Start Menu\n"
            "5. Wait for Docker to fully start (green icon in system tray)\n"
            "6. Restart this application\n\n"
            "Note: The first Docker Desktop startup after installation may take several minutes."
        )
        
        messagebox.showinfo(
            "System Restart Required",
            message,
            icon='info'
        )
        
        return True
    
    def ensure_docker_is_installed(self, parent_window=None) -> Tuple[bool, str]:
        """
        Ensure Docker Desktop is installed, offering automated installation if not found
        
        Args:
            parent_window: Optional parent window for dialogs
            
        Returns:
            Tuple of (success, message)
        """
        # First check if Docker Desktop executable exists
        if self.check_docker_desktop_exists():
            # Check if Docker service is available
            if self.check_docker_installed():
                if self.check_docker_running():
                    return True, "Docker Desktop is installed and running"
                else:
                    return False, (
                        "Docker Desktop is installed but not running.\n\n"
                        "Please start Docker Desktop from the Start Menu."
                    )
            else:
                return False, (
                    "Docker Desktop is installed but Docker service is not available.\n\n"
                    "You may need to restart your computer or reinstall Docker Desktop."
                )
        
        # Docker Desktop not found - offer automated installation
        if sys.platform != 'win32':
            from config import DOCKER_DESKTOP_URL
            return False, f"Please install Docker Desktop manually from: {DOCKER_DESKTOP_URL}"
        
        # Ask user if they want to install Docker Desktop automatically
        response = messagebox.askyesno(
            "Docker Desktop Not Found",
            "Docker Desktop is required for 3D reconstruction features.\n\n"
            "Would you like to download and install Docker Desktop automatically?\n\n"
            "This will:\n"
            "• Download Docker Desktop installer (~500MB)\n"
            "• Install Docker Desktop silently\n"
            "• Require administrator privileges\n"
            "• Require a system restart\n\n"
            "Click 'Yes' to proceed with automated installation.\n"
            "Click 'No' for manual installation instructions.",
            icon='question'
        )
        
        if not response:
            # User declined automated installation, offer manual installation
            self.prompt_docker_installation(parent_window)
            return False, "User declined automated installation"
        
        # Check admin privileges early
        if not self.is_admin():
            messagebox.showerror(
                "Administrator Privileges Required",
                "This application must be run as Administrator to install Docker Desktop.\n\n"
                "Please:\n"
                "1. Close this application\n"
                "2. Right-click the application icon\n"
                "3. Select 'Run as administrator'\n"
                "4. Try again",
                icon='error'
            )
            return False, "Administrator privileges required for installation"
        
        # Download installer
        messagebox.showinfo(
            "Downloading Docker Desktop",
            "Docker Desktop installer will now be downloaded.\n\n"
            "This may take several minutes depending on your internet connection.\n\n"
            "Click OK to continue.",
            icon='info'
        )
        
        installer_path = self.download_docker_installer()
        
        if not installer_path:
            return False, "Failed to download Docker Desktop installer"
        
        # Confirm installation
        confirm = messagebox.askyesno(
            "Ready to Install",
            "Docker Desktop installer has been downloaded.\n\n"
            "The installation will:\n"
            "• Install Docker Desktop silently\n"
            "• May take 5-10 minutes\n"
            "• Require a system restart afterward\n\n"
            "Click 'Yes' to begin installation.\n"
            "Click 'No' to cancel.",
            icon='question'
        )
        
        if not confirm:
            return False, "Installation cancelled by user"
        
        # Install Docker Desktop
        success, message = self.install_docker_desktop(installer_path, parent_window)
        
        if success:
            # Show restart dialog
            self.prompt_restart_for_docker(parent_window)
            return True, (
                "Docker Desktop has been installed successfully.\n\n"
                "Please restart your computer and then start Docker Desktop before using 3D features."
            )
        else:
            return False, f"Docker Desktop installation failed: {message}"
    
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
