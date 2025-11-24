"""
Unit Tests for SRT Parser
"""

import pytest
import os
import tempfile
import pandas as pd
from srt_parser import SRTParser


def create_sample_srt(filepath):
    """Create a sample SRT file for testing"""
    content = """1
00:00:00,000 --> 00:00:01,000
latitude: -34.6037 longitude: -58.3816 altitude: 150.5 rel_alt: 50.2 gimbal_pitch: -90.0 gimbal_yaw: 0.0 yaw: 45.0 iso: 100 shutter: 1/60

2
00:00:01,000 --> 00:00:02,000
latitude: -34.6038 longitude: -58.3817 altitude: 151.0 rel_alt: 50.7 gimbal_pitch: -89.5 gimbal_yaw: 1.0 yaw: 46.0 iso: 100 shutter: 1/60

3
00:00:02,000 --> 00:00:03,000
latitude: -34.6039 longitude: -58.3818 altitude: 151.5 rel_alt: 51.2 gimbal_pitch: -89.0 gimbal_yaw: 2.0 yaw: 47.0 iso: 100 shutter: 1/60
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


class TestSRTParser:
    
    def test_parse_srt_file(self, tmp_path):
        """Test parsing a valid SRT file"""
        srt_file = tmp_path / "test.SRT"
        create_sample_srt(srt_file)
        
        parser = SRTParser(str(srt_file))
        df = parser.parse()
        
        assert len(df) == 3
        assert 'timestamp' in df.columns
        assert 'latitude' in df.columns
        assert 'longitude' in df.columns
        assert 'altitude' in df.columns
        
    def test_timestamp_parsing(self, tmp_path):
        """Test timestamp parsing"""
        srt_file = tmp_path / "test.SRT"
        create_sample_srt(srt_file)
        
        parser = SRTParser(str(srt_file))
        df = parser.parse()
        
        # Check timestamps are sequential
        assert df['timestamp'].iloc[0] == 0.0
        assert df['timestamp'].iloc[1] == 1.0
        assert df['timestamp'].iloc[2] == 2.0
    
    def test_telemetry_extraction(self, tmp_path):
        """Test telemetry data extraction"""
        srt_file = tmp_path / "test.SRT"
        create_sample_srt(srt_file)
        
        parser = SRTParser(str(srt_file))
        df = parser.parse()
        
        # Check first record
        first = df.iloc[0]
        assert first['latitude'] == -34.6037
        assert first['longitude'] == -58.3816
        assert first['altitude'] == 150.5
        assert first['gimbal_pitch'] == -90.0
        assert first['yaw'] == 45.0
    
    def test_empty_file(self, tmp_path):
        """Test handling of empty SRT file"""
        srt_file = tmp_path / "empty.SRT"
        srt_file.write_text("")
        
        parser = SRTParser(str(srt_file))
        
        with pytest.raises(ValueError, match="No telemetry data found"):
            parser.parse()
    
    def test_duration_validation(self, tmp_path):
        """Test duration validation"""
        srt_file = tmp_path / "test.SRT"
        create_sample_srt(srt_file)
        
        parser = SRTParser(str(srt_file))
        df = parser.parse()
        
        # Should match
        assert parser.validate_duration(df, 3.0, tolerance=1.0) == True
        
        # Should not match
        assert parser.validate_duration(df, 10.0, tolerance=1.0) == False
