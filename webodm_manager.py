"""
WebODM Manager
Manages the lifecycle of embedded WebODM instance
"""

import os
import sys
import subprocess
import time
import requests
from typing import Optional, Tuple
import platform


class WebODMManager:
    """Manager for embedded WebODM instance"""
    
    def __init__(self, webodm_path: Optional[str] = None):
        """
        Initialize WebODM manager
        
        Args:
            webodm_path: Path to WebODM directory (defaults to ./webodm)
        """
        if webodm_path is None:
            # Default to webodm subdirectory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            webodm_path = os.path.join(script_dir, "webodm")
        
        self.webodm_path = webodm_path
        self.host = "http://localhost:8000"
        self.username = "admin"
        self.password = "admin"
        self.process = None
        
    def check_docker_installed(self) -> bool:
        """
        Check if Docker is installed and running
        
        Returns:
            True if Docker is available
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def check_docker_running(self) -> bool:
        """
        Check if Docker daemon is running
        
        Returns:
            True if Docker daemon is running
        """
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def check_webodm_exists(self) -> bool:
        """
        Check if WebODM directory exists
        
        Returns:
            True if WebODM directory exists
        """
        webodm_script = os.path.join(self.webodm_path, "webodm.sh")
        webodm_script_bat = os.path.join(self.webodm_path, "webodm.bat")
        
        if platform.system() == "Windows":
            # On Windows, we need webodm.bat or we can use bash/WSL
            return os.path.exists(webodm_script) or os.path.exists(webodm_script_bat)
        else:
            return os.path.exists(webodm_script)
    
    def is_webodm_running(self) -> bool:
        """
        Check if WebODM is currently running
        
        Returns:
            True if WebODM is accessible
        """
        try:
            response = requests.get(f"{self.host}/api/", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def start_webodm(self, timeout: int = 300) -> Tuple[bool, str]:
        """
        Start WebODM using docker-compose
        
        Args:
            timeout: Maximum time to wait for WebODM to start (seconds)
            
        Returns:
            Tuple of (success, message)
        """
        # Check prerequisites
        if not self.check_docker_installed():
            return False, "Docker is not installed. Please install Docker Desktop first."
        
        if not self.check_docker_running():
            return False, "Docker is not running. Please start Docker Desktop."
        
        if not self.check_webodm_exists():
            return False, f"WebODM not found at {self.webodm_path}. Please ensure the repository is cloned correctly."
        
        # Check if already running
        if self.is_webodm_running():
            return True, "WebODM is already running"
        
        print("Starting WebODM... This may take a few minutes on first run.")
        
        try:
            # Change to WebODM directory
            original_dir = os.getcwd()
            os.chdir(self.webodm_path)
            
            # Determine the script to use
            if platform.system() == "Windows":
                # On Windows, try to use bash if available (Git Bash, WSL)
                script_cmd = ["bash", "./webodm.sh", "start"]
            else:
                script_cmd = ["./webodm.sh", "start"]
            
            # Start WebODM
            self.process = subprocess.Popen(
                script_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for WebODM to be ready
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                if self.is_webodm_running():
                    os.chdir(original_dir)
                    return True, f"✓ WebODM started successfully at {self.host}"
                time.sleep(5)
            
            os.chdir(original_dir)
            return False, f"Timeout waiting for WebODM to start after {timeout}s"
            
        except Exception as e:
            try:
                os.chdir(original_dir)
            except OSError:
                pass
            return False, f"Failed to start WebODM: {str(e)}"
    
    def stop_webodm(self) -> Tuple[bool, str]:
        """
        Stop WebODM
        
        Returns:
            Tuple of (success, message)
        """
        if not self.check_webodm_exists():
            return False, "WebODM not found"
        
        print("Stopping WebODM...")
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.webodm_path)
            
            # Determine the script to use
            if platform.system() == "Windows":
                script_cmd = ["bash", "./webodm.sh", "stop"]
            else:
                script_cmd = ["./webodm.sh", "stop"]
            
            result = subprocess.run(
                script_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                return True, "✓ WebODM stopped successfully"
            else:
                return False, f"Failed to stop WebODM: {result.stderr}"
                
        except Exception as e:
            try:
                os.chdir(original_dir)
            except OSError:
                pass
            return False, f"Failed to stop WebODM: {str(e)}"
    
    def get_status(self) -> dict:
        """
        Get WebODM status information
        
        Returns:
            Dictionary with status information
        """
        return {
            'docker_installed': self.check_docker_installed(),
            'docker_running': self.check_docker_running(),
            'webodm_exists': self.check_webodm_exists(),
            'webodm_running': self.is_webodm_running(),
            'host': self.host,
            'username': self.username
        }
    
    def ensure_running(self, timeout: int = 300) -> Tuple[bool, str]:
        """
        Ensure WebODM is running, starting it if necessary
        
        Args:
            timeout: Maximum time to wait for startup
            
        Returns:
            Tuple of (success, message)
        """
        if self.is_webodm_running():
            return True, "WebODM is already running"
        
        return self.start_webodm(timeout=timeout)
