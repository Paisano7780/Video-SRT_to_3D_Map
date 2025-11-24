"""
Telemetry Synchronization and Interpolation
Synchronizes frame timestamps with SRT telemetry data and performs interpolation
"""

import numpy as np
import pandas as pd
from typing import List, Tuple


class TelemetrySynchronizer:
    """Synchronize and interpolate telemetry data with video frames"""
    
    def __init__(self, telemetry_df: pd.DataFrame):
        self.telemetry_df = telemetry_df.copy()
        
    def synchronize_and_interpolate(self, frame_timestamps: List[float]) -> pd.DataFrame:
        """
        Synchronize frame timestamps with telemetry and interpolate missing values
        
        Args:
            frame_timestamps: List of frame timestamps in seconds
            
        Returns:
            DataFrame with interpolated telemetry for each frame
        """
        # Create DataFrame for frame timestamps
        frame_df = pd.DataFrame({'timestamp': frame_timestamps})
        
        # Combine telemetry and frame timestamps
        combined = pd.concat([
            self.telemetry_df[['timestamp']].assign(is_telemetry=True),
            frame_df.assign(is_telemetry=False)
        ]).sort_values('timestamp').reset_index(drop=True)
        
        # Merge telemetry data
        combined = combined.merge(
            self.telemetry_df,
            on='timestamp',
            how='left'
        )
        
        # Interpolate linear values (latitude, longitude, altitude)
        linear_columns = ['latitude', 'longitude', 'altitude', 'rel_altitude', 'gimbal_pitch']
        for col in linear_columns:
            if col in combined.columns:
                combined[col] = combined[col].interpolate(method='linear', limit_direction='both')
        
        # Interpolate circular values (yaw angles)
        circular_columns = ['yaw', 'gimbal_yaw']
        for col in circular_columns:
            if col in combined.columns:
                combined[col] = self._interpolate_circular(
                    combined['timestamp'].values,
                    combined[col].values
                )
        
        # Filter to only frame timestamps
        result = combined[combined['is_telemetry'] == False].copy()
        result = result.drop(columns=['is_telemetry'])
        
        return result
    
    def _interpolate_circular(self, timestamps: np.ndarray, angles: np.ndarray) -> np.ndarray:
        """
        Interpolate circular/angular values (handles 359° to 0° transition)
        
        Args:
            timestamps: Array of timestamps
            angles: Array of angle values in degrees
            
        Returns:
            Interpolated angles
        """
        # Convert to radians
        valid_mask = ~np.isnan(angles)
        
        if not valid_mask.any():
            return angles
        
        # Get valid data points
        valid_times = timestamps[valid_mask]
        valid_angles = angles[valid_mask]
        
        # Convert to unit circle (sin, cos)
        radians = np.deg2rad(valid_angles)
        sin_vals = np.sin(radians)
        cos_vals = np.cos(radians)
        
        # Interpolate sin and cos separately
        sin_interp = np.interp(timestamps, valid_times, sin_vals)
        cos_interp = np.interp(timestamps, valid_times, cos_vals)
        
        # Convert back to angles
        interpolated_radians = np.arctan2(sin_interp, cos_interp)
        interpolated_degrees = np.rad2deg(interpolated_radians)
        
        # Ensure positive angles (0-360)
        interpolated_degrees = interpolated_degrees % 360
        
        return interpolated_degrees
    
    @staticmethod
    def classify_flight_type(telemetry_df: pd.DataFrame) -> str:
        """
        Classify flight type based on gimbal pitch and yaw variation
        
        Args:
            telemetry_df: DataFrame with gimbal_pitch and yaw columns
            
        Returns:
            Flight type: "Nadir Mapping" or "Orbit/Structure"
        """
        if telemetry_df.empty:
            return "Unknown"
        
        # Calculate statistics
        avg_pitch = telemetry_df['gimbal_pitch'].mean() if 'gimbal_pitch' in telemetry_df else 0
        
        # Calculate yaw variation (circular standard deviation)
        if 'yaw' in telemetry_df and not telemetry_df['yaw'].isna().all():
            yaw_values = telemetry_df['yaw'].dropna().values
            yaw_rad = np.deg2rad(yaw_values)
            
            # Circular variance
            C = np.mean(np.cos(yaw_rad))
            S = np.mean(np.sin(yaw_rad))
            R = np.sqrt(C**2 + S**2)
            circular_variance = 1 - R
            
            # Convert to degrees for interpretation
            # Maximum circular variance is 180 degrees (complete dispersion)
            MAX_CIRCULAR_VARIANCE_DEG = 180
            yaw_variation = np.rad2deg(np.sqrt(-2 * np.log(R))) if R > 0 else MAX_CIRCULAR_VARIANCE_DEG
        else:
            yaw_variation = 0
        
        # Classification logic
        # Nadir: gimbal pitch close to -90° and low yaw variation
        is_nadir = (avg_pitch < -80) and (yaw_variation < 30)
        
        # Orbit: oblique gimbal pitch and high yaw variation
        is_orbit = (-60 < avg_pitch < -30) and (yaw_variation > 30)
        
        if is_nadir:
            flight_type = "Nadir Mapping"
            print(f"✓ Flight classified as: {flight_type}")
            print(f"  Average Gimbal Pitch: {avg_pitch:.1f}°, Yaw Variation: {yaw_variation:.1f}°")
        elif is_orbit:
            flight_type = "Orbit/Structure"
            print(f"✓ Flight classified as: {flight_type}")
            print(f"  Average Gimbal Pitch: {avg_pitch:.1f}°, Yaw Variation: {yaw_variation:.1f}°")
        else:
            flight_type = "Mixed/Other"
            print(f"⚠ Flight classified as: {flight_type}")
            print(f"  Average Gimbal Pitch: {avg_pitch:.1f}°, Yaw Variation: {yaw_variation:.1f}°")
        
        return flight_type
