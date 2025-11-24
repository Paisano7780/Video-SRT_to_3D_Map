"""
Setup configuration for PyInstaller builds
"""

# Application metadata
APP_NAME = "DJI_3D_Mapper"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Video-SRT_to_3D_Map"
APP_DESCRIPTION = "DJI Video to 3D Map Pipeline"

# PyInstaller configuration
PYINSTALLER_OPTIONS = {
    'name': APP_NAME,
    'onefile': True,
    'windowed': True,
    'hidden_imports': [
        'pandas',
        'numpy',
        'tkinter',
        'requests',
        'PIL',
        're',
        'json',
        'threading',
    ],
    'excludes': [
        'matplotlib',
        'scipy',
        'IPython',
    ],
}

# Default directories
DEFAULT_BUFFER_DIR = "DroneBuffer"
DEFAULT_OUTPUT_DIR = "DroneOutput"

# Processing defaults
DEFAULT_FRAME_RATE = 1.0  # fps
DEFAULT_JPEG_QUALITY = 2  # 1-31, lower is better

# WebODM defaults
DEFAULT_WEBODM_URL = "http://localhost:8000"
DEFAULT_WEBODM_USERNAME = "admin"
DEFAULT_WEBODM_PASSWORD = "admin"

# External resources
DOCKER_DESKTOP_URL = "https://www.docker.com/products/docker-desktop"

# Docker Desktop installation (Windows x64)
DOCKER_DESKTOP_INSTALLER_URL = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
DOCKER_DESKTOP_INSTALLER_FILENAME = "DockerDesktopInstaller.exe"
DOCKER_DESKTOP_INSTALL_PATH = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"

