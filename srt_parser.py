"""
SRT Parser for DJI Drone Telemetry
Extracts GPS, altitude, gimbal, and other telemetry data from DJI SRT files
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd


class SRTParser:
    """Parser for DJI SRT subtitle files containing telemetry data"""
    
    def __init__(self, srt_file_path: str):
        self.srt_file_path = srt_file_path
        self.telemetry_data = []
        
    def parse(self) -> pd.DataFrame:
        """
        Parse the SRT file and extract telemetry data
        
        Returns:
            DataFrame with columns: timestamp, latitude, longitude, altitude, 
                                   gimbal_pitch, yaw, etc.
        """
        with open(self.srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines to separate subtitle blocks
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            telemetry = self._parse_block(block)
            if telemetry:
                self.telemetry_data.append(telemetry)
        
        if not self.telemetry_data:
            raise ValueError(f"No telemetry data found in {self.srt_file_path}")
        
        df = pd.DataFrame(self.telemetry_data)
        
        # Ensure numeric columns are float64, not object type
        # This prevents errors when None values create object-type columns
        numeric_columns = [
            'latitude', 'longitude', 'altitude', 'rel_altitude',
            'gimbal_pitch', 'gimbal_yaw', 'yaw', 'iso', 'shutter'
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _parse_block(self, block: str) -> Optional[Dict]:
        """Parse a single subtitle block"""
        lines = block.strip().split('\n')
        
        if len(lines) < 3:
            return None
        
        # Extract timestamp from line 2 (format: HH:MM:SS,mmm --> HH:MM:SS,mmm)
        timestamp_line = lines[1]
        timestamp = self._parse_timestamp(timestamp_line)
        
        if timestamp is None:
            return None
        
        # Extract telemetry from remaining lines
        telemetry_text = ' '.join(lines[2:])
        
        # Support multiple DJI SRT formats:
        # Format A: [latitude: -34.6037] or latitude: -34.6037
        # Format B: Lat: 34.052200, Lon: -118.243700, Alt: 2.0m, GimbalYaw: 10.0
        telemetry = {
            'timestamp': timestamp,
            # Latitude: supports "latitude:", "Lat:", with optional brackets/units
            'latitude': self._extract_value(telemetry_text, r'(?:latitude|lat)[:\s]+(-?\d+\.?\d*)'),
            # Longitude: supports "longitude:", "Lon:"
            'longitude': self._extract_value(telemetry_text, r'(?:longitude|lon)[:\s]+(-?\d+\.?\d*)'),
            # Altitude: supports "altitude:", "Alt:" with optional unit (m)
            'altitude': self._extract_value(telemetry_text, r'(?:altitude|alt)[:\s]+(-?\d+\.?\d*)'),
            # Relative altitude: supports "rel_alt:"
            'rel_altitude': self._extract_value(telemetry_text, r'rel_alt[:\s]+(-?\d+\.?\d*)'),
            # Gimbal pitch: supports "gimbal_pitch:", "GimbalPitch:"
            'gimbal_pitch': self._extract_value(telemetry_text, r'gimbal_?pitch[:\s]+(-?\d+\.?\d*)'),
            # Gimbal yaw: supports "gimbal_yaw:", "GimbalYaw:"
            'gimbal_yaw': self._extract_value(telemetry_text, r'gimbal_?yaw[:\s]+(-?\d+\.?\d*)'),
            # Yaw (flight direction): supports "yaw:" but not "GimbalYaw:"
            'yaw': self._extract_value(telemetry_text, r'(?<!gimbal_)(?<!Gimbal)yaw[:\s]+(-?\d+\.?\d*)'),
            # ISO: supports "iso:", "ISO:"
            'iso': self._extract_value(telemetry_text, r'iso[:\s]+(\d+)'),
            # Shutter: supports "shutter:", "Shutter:" with fractions
            'shutter': self._extract_value(telemetry_text, r'shutter[:\s]+([0-9/.]+)'),
        }
        
        return telemetry
    
    def _parse_timestamp(self, timestamp_line: str) -> Optional[float]:
        """Parse timestamp from SRT format to seconds"""
        try:
            # Extract start time (before -->)
            start_time_str = timestamp_line.split('-->')[0].strip()
            
            # Parse HH:MM:SS,mmm format
            time_pattern = r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})'
            match = re.search(time_pattern, start_time_str)
            
            if match:
                hours, minutes, seconds, milliseconds = map(int, match.groups())
                total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
                return total_seconds
        except Exception as e:
            print(f"Error parsing timestamp: {e}")
        
        return None
    
    def _extract_value(self, text: str, pattern: str) -> Optional[float]:
        """Extract numeric value using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1)
                # Handle fractions like "1/60"
                if '/' in value_str:
                    num, denom = value_str.split('/')
                    return float(num) / float(denom)
                return float(value_str)
            except ValueError:
                return None
        return None
    
    @staticmethod
    def validate_duration(srt_df: pd.DataFrame, video_duration: float, tolerance: float = 2.0) -> bool:
        """
        Validate that SRT duration matches video duration
        
        Args:
            srt_df: DataFrame with telemetry data
            video_duration: Video duration in seconds
            tolerance: Acceptable difference in seconds
            
        Returns:
            True if durations match within tolerance
        """
        if srt_df.empty:
            return False
        
        srt_duration = srt_df['timestamp'].max()
        diff = abs(srt_duration - video_duration)
        
        if diff > tolerance:
            print(f"Warning: SRT duration ({srt_duration:.2f}s) differs from video duration ({video_duration:.2f}s) by {diff:.2f}s")
            return False
        
        return True
