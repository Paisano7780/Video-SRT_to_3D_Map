"""
Unit Tests for EXIF Metadata Injector
Tests GPS data injection and verification
"""

import pytest
import os
import tempfile
import subprocess
import shutil
import numpy as np
from unittest.mock import patch, MagicMock


def is_exiftool_available():
    """Check if exiftool is available for testing"""
    return shutil.which('exiftool') is not None


def create_test_image(filepath):
    """Create a minimal test JPEG image"""
    # Try to use PIL/Pillow if available
    try:
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(filepath, 'JPEG')
        return True
    except ImportError:
        # Fallback: Create minimal valid JPEG
        # This is a 1x1 red pixel JPEG
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
            0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
            0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
            0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
            0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
            0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
            0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
            0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
            0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
            0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
            0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
            0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
            0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
            0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
            0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD3, 0x28, 0xA2, 0x80, 0x0A, 0x28, 0xA0,
            0x02, 0xFF, 0xD9
        ])
        with open(filepath, 'wb') as f:
            f.write(jpeg_data)
        return True


def has_gps_latitude(image_path: str) -> bool:
    """
    Helper function to check if an image has GPS latitude data
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if GPS Latitude is present in the image EXIF data
    """
    result = subprocess.run(
        ['exiftool', '-GPSLatitude', image_path],
        capture_output=True,
        text=True
    )
    return 'GPS Latitude' in result.stdout and result.stdout.strip() != ''


def has_gps_longitude(image_path: str) -> bool:
    """
    Helper function to check if an image has GPS longitude data
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if GPS Longitude is present in the image EXIF data
    """
    result = subprocess.run(
        ['exiftool', '-GPSLongitude', image_path],
        capture_output=True,
        text=True
    )
    return 'GPS Longitude' in result.stdout and result.stdout.strip() != ''


class TestExifInjector:
    """Tests for EXIF metadata injection"""
    
    @pytest.fixture
    def test_image(self, tmp_path):
        """Create a test image for each test"""
        image_path = tmp_path / "test_image.jpg"
        create_test_image(str(image_path))
        return str(image_path)
    
    def test_import_exif_injector(self):
        """Test that ExifInjector can be imported"""
        from exif_injector import ExifInjector
        assert ExifInjector is not None
    
    def test_is_valid_number_method(self):
        """Test the _is_valid_number static method handles various values correctly"""
        from exif_injector import ExifInjector
        
        # Use mock to avoid needing exiftool installed for this test
        with patch.object(ExifInjector, '_find_exiftool', return_value='exiftool'):
            injector = ExifInjector()
        
        # Valid numbers
        assert injector._is_valid_number(0) is True
        assert injector._is_valid_number(0.0) is True
        assert injector._is_valid_number(-34.6037) is True
        assert injector._is_valid_number(150.5) is True
        assert injector._is_valid_number(100) is True
        
        # Invalid values
        assert injector._is_valid_number(None) is False
        assert injector._is_valid_number(np.nan) is False
        assert injector._is_valid_number(float('nan')) is False
        assert injector._is_valid_number('invalid') is False
        assert injector._is_valid_number([1, 2, 3]) is False
        assert injector._is_valid_number({}) is False
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_with_valid_gps(self, test_image):
        """Test GPS metadata injection with valid coordinates"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': -34.6037,
            'longitude': -58.3816,
            'altitude': 150.5,
            'rel_altitude': 50.2,
            'gimbal_pitch': -90.0,
            'gimbal_yaw': 0.0,
            'yaw': 45.0,
            'iso': 100,
            'shutter': 1/60
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True
        
        # Verify GPS data was written using helper functions
        assert has_gps_latitude(test_image)
        assert has_gps_longitude(test_image)
        
        # Check additional GPS data
        exif_result = subprocess.run(
            ['exiftool', '-GPS*', test_image],
            capture_output=True,
            text=True
        )
        output = exif_result.stdout
        assert 'GPS Altitude' in output
        # Check approximate values (South latitude, West longitude)
        assert 'S' in output  # South
        assert 'W' in output  # West
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_with_nan_gps(self, test_image):
        """Test that NaN GPS values are NOT injected (bug fix verification)"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': np.nan,
            'longitude': np.nan,
            'altitude': 150.5,
            'rel_altitude': 50.2,
            'gimbal_pitch': -90.0,
            'yaw': 45.0,
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True  # Injection should succeed (just skip NaN values)
        
        # Verify GPS lat/lon was NOT written using helper functions
        assert not has_gps_latitude(test_image)
        assert not has_gps_longitude(test_image)
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_with_none_gps(self, test_image):
        """Test that None GPS values are NOT injected"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': None,
            'longitude': None,
            'altitude': 150.5,
            'gimbal_pitch': -90.0,
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True
        
        # Verify GPS lat/lon was NOT written using helper function
        assert not has_gps_latitude(test_image)
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_positive_coordinates(self, test_image):
        """Test GPS metadata with positive (North/East) coordinates"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': 40.7128,   # New York (North)
            'longitude': -74.0060,  # New York (West)
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True
        
        # Verify GPS data was written
        assert has_gps_latitude(test_image)
        assert has_gps_longitude(test_image)
        
        exif_result = subprocess.run(
            ['exiftool', '-GPSLatitudeRef', '-GPSLongitudeRef', test_image],
            capture_output=True,
            text=True
        )
        
        output = exif_result.stdout
        assert 'N' in output or 'North' in output  # North latitude
        assert 'W' in output or 'West' in output   # West longitude
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_all_positive_coordinates(self, test_image):
        """Test GPS metadata with all positive (North/East) coordinates"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': 51.5074,   # London (North)
            'longitude': 0.1278,   # London (East)
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True
        
        exif_result = subprocess.run(
            ['exiftool', '-GPSLatitudeRef', '-GPSLongitudeRef', test_image],
            capture_output=True,
            text=True
        )
        
        output = exif_result.stdout
        assert 'North' in output or 'N' in output
        assert 'East' in output or 'E' in output
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_dji_tags(self, test_image):
        """Test DJI-specific XMP tags are written"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': -34.6037,
            'longitude': -58.3816,
            'altitude': 150.5,
            'rel_altitude': 50.2,
            'gimbal_pitch': -45.0,
            'gimbal_yaw': 90.0,
            'yaw': 180.0,
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True
        
        # Check XMP tags
        exif_result = subprocess.run(
            ['exiftool', '-XMP:*', test_image],
            capture_output=True,
            text=True
        )
        
        output = exif_result.stdout
        assert 'Gimbal Pitch' in output or 'GimbalPitch' in output
        assert 'Gimbal Yaw' in output or 'GimbalYaw' in output
        assert 'Flight Yaw' in output or 'FlightYaw' in output
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_metadata_camera_settings(self, test_image):
        """Test camera settings are written correctly"""
        from exif_injector import ExifInjector
        
        telemetry = {
            'latitude': -34.6037,
            'longitude': -58.3816,
            'iso': 200,
            'shutter': 1/125,
        }
        
        injector = ExifInjector()
        result = injector.inject_metadata(test_image, telemetry)
        
        assert result is True
        
        exif_result = subprocess.run(
            ['exiftool', '-ISO', '-Make', '-Model', test_image],
            capture_output=True,
            text=True
        )
        
        output = exif_result.stdout
        assert '200' in output  # ISO value
        assert 'DJI' in output  # Make
        assert 'Mini 3' in output  # Model
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_batch_inject(self, tmp_path):
        """Test batch injection of multiple images"""
        from exif_injector import ExifInjector
        
        # Create multiple test images
        image_paths = []
        for i in range(3):
            path = tmp_path / f"test_image_{i}.jpg"
            create_test_image(str(path))
            image_paths.append(str(path))
        
        # Create telemetry for each image
        telemetry_list = [
            {'latitude': -34.6037, 'longitude': -58.3816, 'altitude': 100.0},
            {'latitude': -34.6038, 'longitude': -58.3817, 'altitude': 101.0},
            {'latitude': -34.6039, 'longitude': -58.3818, 'altitude': 102.0},
        ]
        
        injector = ExifInjector()
        success_count = injector.batch_inject(image_paths, telemetry_list)
        
        assert success_count == 3
        
        # Verify all images have GPS data using helper function
        for path in image_paths:
            assert has_gps_latitude(path)
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_batch_inject_with_nan_values(self, tmp_path):
        """Test batch injection handles NaN values gracefully"""
        from exif_injector import ExifInjector
        
        # Create test images
        image_paths = []
        for i in range(3):
            path = tmp_path / f"test_image_{i}.jpg"
            create_test_image(str(path))
            image_paths.append(str(path))
        
        # Include NaN values in some records
        telemetry_list = [
            {'latitude': -34.6037, 'longitude': -58.3816, 'altitude': 100.0},
            {'latitude': np.nan, 'longitude': np.nan, 'altitude': 101.0},  # NaN GPS
            {'latitude': -34.6039, 'longitude': -58.3818, 'altitude': 102.0},
        ]
        
        injector = ExifInjector()
        success_count = injector.batch_inject(image_paths, telemetry_list)
        
        # All should succeed (NaN values are just skipped)
        assert success_count == 3
        
        # First and third should have GPS, second should not using helper function
        for i, path in enumerate(image_paths):
            if i == 1:  # Second image had NaN
                assert not has_gps_latitude(path)
            else:
                assert has_gps_latitude(path)
    
    def test_inject_metadata_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file"""
        from exif_injector import ExifInjector
        
        # Mock exiftool to avoid needing it installed
        with patch.object(ExifInjector, '_find_exiftool', return_value='exiftool'):
            injector = ExifInjector()
            
            with pytest.raises(FileNotFoundError):
                injector.inject_metadata('/nonexistent/path/image.jpg', {})
    
    def test_batch_inject_mismatched_lengths(self):
        """Test that batch_inject raises error for mismatched list lengths"""
        from exif_injector import ExifInjector
        
        with patch.object(ExifInjector, '_find_exiftool', return_value='exiftool'):
            injector = ExifInjector()
            
            with pytest.raises(ValueError, match="must match"):
                injector.batch_inject(
                    ['/path/img1.jpg', '/path/img2.jpg'],
                    [{'latitude': 1.0}]  # Only one telemetry entry
                )


class TestExifInjectorWithDataFrame:
    """Tests for EXIF injection with pandas DataFrame input (real-world scenario)"""
    
    @pytest.mark.skipif(not is_exiftool_available(), reason="ExifTool not installed")
    def test_inject_from_dataframe_records(self, tmp_path):
        """Test injection using DataFrame.to_dict('records') output"""
        import pandas as pd
        from exif_injector import ExifInjector
        
        # Simulate telemetry DataFrame with some NaN values (as would come from interpolation)
        df = pd.DataFrame({
            'timestamp': [0.0, 1.0, 2.0],
            'latitude': [-34.6037, -34.6038, np.nan],
            'longitude': [-58.3816, -58.3817, -58.3818],
            'altitude': [100.0, 101.0, 102.0],
            'gimbal_pitch': [-90.0, np.nan, -88.0],
        })
        
        # Convert to records (how main_app.py does it)
        telemetry_records = df.to_dict('records')
        
        # Create test images
        image_paths = []
        for i in range(3):
            path = tmp_path / f"frame_{i:06d}.jpg"
            create_test_image(str(path))
            image_paths.append(str(path))
        
        injector = ExifInjector()
        success_count = injector.batch_inject(image_paths, telemetry_records)
        
        assert success_count == 3
        
        # Verify first two have GPS latitude, third does not using helper function
        for i, path in enumerate(image_paths):
            if i == 2:  # Third image had NaN latitude
                assert not has_gps_latitude(path)
            else:
                assert has_gps_latitude(path)
