"""
EXIF Metadata Injector
Injects GPS and camera metadata into images using ExifTool
"""

import os
import subprocess
from typing import Optional
import tempfile
import sys


class ExifInjector:
    """Inject EXIF/XMP metadata into images for photogrammetry"""
    
    def __init__(self):
        self.exiftool_path = self._find_exiftool()
        
    def _find_exiftool(self) -> str:
        """Find exiftool executable"""
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            try:
                bundle_dir = sys._MEIPASS
                bundled_exiftool = os.path.join(bundle_dir, 'exiftool.exe')
                if os.path.exists(bundled_exiftool):
                    return bundled_exiftool
            except AttributeError:
                # sys._MEIPASS not available in this PyInstaller configuration
                pass
        
        # Check if exiftool is in PATH
        try:
            result = subprocess.run(
                ['exiftool', '-ver'],
                capture_output=True,
                text=True,
                check=True
            )
            return 'exiftool'
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try common Windows installation paths
            common_paths = [
                r'C:\Program Files\exiftool\exiftool.exe',
                r'C:\exiftool\exiftool.exe',
                r'exiftool.exe',
                # Also check in the same directory as the executable
                os.path.join(os.path.dirname(sys.executable), 'exiftool.exe')
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
            
            raise RuntimeError(
                "ExifTool not found. Please install from: https://exiftool.org/\n"
                "Download and place exiftool.exe in the application directory or system PATH."
            )
    
    def inject_metadata(self, image_path: str, telemetry: dict) -> bool:
        """
        Inject GPS and camera metadata into an image
        
        Args:
            image_path: Path to the image file
            telemetry: Dictionary with telemetry data
            
        Returns:
            True if successful
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Build ExifTool command
        cmd = [self.exiftool_path]
        
        # GPS data
        if telemetry.get('latitude') is not None:
            lat = telemetry['latitude']
            lat_ref = 'N' if lat >= 0 else 'S'
            cmd.extend([
                f'-GPSLatitude={abs(lat)}',
                f'-GPSLatitudeRef={lat_ref}'
            ])
        
        if telemetry.get('longitude') is not None:
            lon = telemetry['longitude']
            lon_ref = 'E' if lon >= 0 else 'W'
            cmd.extend([
                f'-GPSLongitude={abs(lon)}',
                f'-GPSLongitudeRef={lon_ref}'
            ])
        
        # Altitude (use rel_altitude if available, otherwise altitude)
        altitude = telemetry.get('rel_altitude') or telemetry.get('altitude')
        if altitude is not None:
            cmd.extend([
                f'-GPSAltitude={abs(altitude)}',
                f'-GPSAltitudeRef={0 if altitude >= 0 else 1}',  # 0 = above sea level
                f'-AbsoluteAltitude={altitude}',
                f'-RelativeAltitude={telemetry.get("rel_altitude", altitude)}'
            ])
        
        # Gimbal/Camera orientation
        if telemetry.get('gimbal_pitch') is not None:
            cmd.append(f'-XMP:GimbalPitchDegree={telemetry["gimbal_pitch"]}')
            cmd.append(f'-CameraElevationAngle={telemetry["gimbal_pitch"]}')
        
        if telemetry.get('gimbal_yaw') is not None:
            cmd.append(f'-XMP:GimbalYawDegree={telemetry["gimbal_yaw"]}')
        
        if telemetry.get('yaw') is not None:
            cmd.append(f'-XMP:FlightYawDegree={telemetry["yaw"]}')
            # Some photogrammetry software uses different tags
            cmd.append(f'-GPSImgDirection={telemetry["yaw"]}')
            cmd.append(f'-GPSImgDirectionRef=T')  # T = True North
        
        # Camera settings
        if telemetry.get('iso') is not None:
            cmd.append(f'-ISO={int(telemetry["iso"])}')
        
        if telemetry.get('shutter') is not None:
            cmd.append(f'-ShutterSpeed={telemetry["shutter"]}')
        
        # Additional metadata
        cmd.extend([
            '-Make=DJI',
            '-Model=Mini 3',
            '-overwrite_original',  # Don't create backup files
            image_path
        ])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error injecting metadata into {image_path}: {e.stderr}")
            return False
    
    def batch_inject(self, image_paths: list, telemetry_list: list, 
                    progress_callback=None) -> int:
        """
        Inject metadata into multiple images
        
        Args:
            image_paths: List of image file paths
            telemetry_list: List of telemetry dictionaries (same order as images)
            progress_callback: Optional callback function(current, total)
            
        Returns:
            Number of successfully processed images
        """
        if len(image_paths) != len(telemetry_list):
            raise ValueError("Number of images and telemetry entries must match")
        
        success_count = 0
        total = len(image_paths)
        
        for i, (img_path, telemetry) in enumerate(zip(image_paths, telemetry_list)):
            try:
                if self.inject_metadata(img_path, telemetry):
                    success_count += 1
                
                if progress_callback:
                    progress_callback(i + 1, total)
                    
            except Exception as e:
                print(f"Failed to process {img_path}: {e}")
        
        return success_count
