"""
Unit Tests for Telemetry Synchronization
"""

import pytest
import numpy as np
import pandas as pd
from telemetry_sync import TelemetrySynchronizer


class TestTelemetrySynchronizer:
    
    def test_linear_interpolation(self):
        """Test linear interpolation for GPS coordinates"""
        telemetry_df = pd.DataFrame({
            'timestamp': [0.0, 2.0, 4.0],
            'latitude': [-34.0, -34.2, -34.4],
            'longitude': [-58.0, -58.2, -58.4],
            'altitude': [100.0, 110.0, 120.0],
            'rel_altitude': [50.0, 55.0, 60.0],
            'gimbal_pitch': [-90.0, -85.0, -80.0],
            'yaw': [0.0, 45.0, 90.0]
        })
        
        synchronizer = TelemetrySynchronizer(telemetry_df)
        
        # Frame at 1 second (midpoint between 0 and 2)
        frame_timestamps = [1.0]
        result = synchronizer.synchronize_and_interpolate(frame_timestamps)
        
        # Check interpolated values
        assert len(result) == 1
        assert abs(result['latitude'].iloc[0] - (-34.1)) < 0.01
        assert abs(result['longitude'].iloc[0] - (-58.1)) < 0.01
        assert abs(result['altitude'].iloc[0] - 105.0) < 0.1
    
    def test_circular_interpolation(self):
        """Test circular interpolation for yaw angles"""
        # Test case: yaw goes from 350° to 10° (crossing 0°)
        telemetry_df = pd.DataFrame({
            'timestamp': [0.0, 1.0, 2.0],
            'latitude': [-34.0, -34.0, -34.0],
            'longitude': [-58.0, -58.0, -58.0],
            'altitude': [100.0, 100.0, 100.0],
            'rel_altitude': [50.0, 50.0, 50.0],
            'gimbal_pitch': [-90.0, -90.0, -90.0],
            'yaw': [350.0, 0.0, 10.0]
        })
        
        synchronizer = TelemetrySynchronizer(telemetry_df)
        
        # Interpolate at 0.5 seconds
        frame_timestamps = [0.5]
        result = synchronizer.synchronize_and_interpolate(frame_timestamps)
        
        # Should be around 355° (midpoint between 350 and 0)
        interpolated_yaw = result['yaw'].iloc[0]
        assert 350 <= interpolated_yaw <= 360 or 0 <= interpolated_yaw <= 5
    
    def test_multiple_frames(self):
        """Test synchronization with multiple frame timestamps"""
        telemetry_df = pd.DataFrame({
            'timestamp': [0.0, 2.0],
            'latitude': [-34.0, -34.2],
            'longitude': [-58.0, -58.2],
            'altitude': [100.0, 110.0],
            'rel_altitude': [50.0, 55.0],
            'gimbal_pitch': [-90.0, -85.0],
            'yaw': [0.0, 90.0]
        })
        
        synchronizer = TelemetrySynchronizer(telemetry_df)
        
        # Multiple frames
        frame_timestamps = [0.5, 1.0, 1.5]
        result = synchronizer.synchronize_and_interpolate(frame_timestamps)
        
        assert len(result) == 3
        assert all(result['timestamp'] == frame_timestamps)
    
    def test_classify_nadir_flight(self):
        """Test classification of nadir mapping flight"""
        telemetry_df = pd.DataFrame({
            'timestamp': [0.0, 1.0, 2.0, 3.0],
            'gimbal_pitch': [-90.0, -89.0, -91.0, -90.0],
            'yaw': [45.0, 46.0, 45.5, 45.2]  # Low variation
        })
        
        flight_type = TelemetrySynchronizer.classify_flight_type(telemetry_df)
        assert flight_type == "Nadir Mapping"
    
    def test_classify_orbit_flight(self):
        """Test classification of orbit/structure flight"""
        telemetry_df = pd.DataFrame({
            'timestamp': [0.0, 1.0, 2.0, 3.0],
            'gimbal_pitch': [-45.0, -46.0, -44.0, -45.5],  # Oblique
            'yaw': [0.0, 90.0, 180.0, 270.0]  # High variation
        })
        
        flight_type = TelemetrySynchronizer.classify_flight_type(telemetry_df)
        assert flight_type == "Orbit/Structure"
    
    def test_object_dtype_with_none_values(self):
        """Test handling of object dtype columns with None values (Windows error case)"""
        # Create DataFrame with object dtype columns containing None values
        # This simulates the error case from the Windows testing bug
        telemetry_df = pd.DataFrame({
            'timestamp': [0.0, 2.0, 4.0],
            'latitude': [-34.0, -34.2, -34.4],
            'longitude': [-58.0, -58.2, -58.4],
            'altitude': [100.0, 110.0, 120.0],
            'rel_altitude': [50.0, 55.0, 60.0],
            'gimbal_pitch': [-90.0, -85.0, -80.0],
            'gimbal_yaw': pd.Series([None, 10.0, 20.0], dtype=object),
            'yaw': pd.Series([0.0, None, 90.0], dtype=object)
        })
        
        synchronizer = TelemetrySynchronizer(telemetry_df)
        frame_timestamps = [1.0, 3.0]
        
        # Should not raise TypeError about isnan
        result = synchronizer.synchronize_and_interpolate(frame_timestamps)
        
        # Verify result shape and that interpolation worked
        assert len(result) == 2
        assert all(result['timestamp'] == frame_timestamps)
        # Yaw should be interpolated even with None values
        assert not result['yaw'].isna().all()
        # gimbal_yaw should have interpolated value at timestamp 1.0
        assert not pd.isna(result['gimbal_yaw'].iloc[0])
