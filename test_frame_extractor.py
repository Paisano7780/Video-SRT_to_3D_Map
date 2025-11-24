"""
Unit Tests for Frame Extractor
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from frame_extractor import FrameExtractor


class TestFrameExtractor:
    
    def test_ffmpeg_check_success(self):
        """Test that initialization succeeds when ffmpeg is available"""
        # This test will only pass if ffmpeg is installed
        # If ffmpeg is not available, it should raise RuntimeError
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                video_path = f.name
            
            # This should not raise if ffmpeg is available
            extractor = FrameExtractor(video_path)
            assert extractor.video_path == video_path
            
        except RuntimeError as e:
            # If ffmpeg is not installed, check error message is helpful
            assert "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower()
            assert "PATH" in str(e) or "install" in str(e).lower()
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)
    
    def test_ffmpeg_not_available_error_message(self):
        """Test that helpful error message is shown when ffmpeg is not available"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
        
        try:
            # Mock shutil.which to return None (ffmpeg not found)
            with patch('frame_extractor.shutil.which') as mock_which:
                mock_which.return_value = None
                
                with pytest.raises(RuntimeError) as exc_info:
                    FrameExtractor(video_path)
                
                error_message = str(exc_info.value)
                # Check that error message is helpful
                assert "not found" in error_message
                assert "ffmpeg.org" in error_message or "PATH" in error_message
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)
    
    def test_calculate_frame_timestamps(self):
        """Test frame timestamp calculation"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
        
        try:
            # Mock the ffmpeg check
            with patch('frame_extractor.shutil.which') as mock_which:
                mock_which.return_value = '/usr/bin/ffmpeg'
                
                extractor = FrameExtractor(video_path)
                
                # Test timestamp calculation
                timestamps = extractor.calculate_frame_timestamps(5, 1.0)
                assert len(timestamps) == 5
                assert timestamps == [0.0, 1.0, 2.0, 3.0, 4.0]
                
                # Test with different frame rate
                timestamps = extractor.calculate_frame_timestamps(3, 0.5)
                assert len(timestamps) == 3
                assert timestamps == [0.0, 2.0, 4.0]
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)
    
    def test_calculate_frame_timestamps_invalid_rate(self):
        """Test that invalid frame rate raises error"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
        
        try:
            with patch('frame_extractor.shutil.which') as mock_which:
                mock_which.return_value = '/usr/bin/ffmpeg'
                
                extractor = FrameExtractor(video_path)
                
                with pytest.raises(ValueError, match="Frame rate must be positive"):
                    extractor.calculate_frame_timestamps(5, 0.0)
                
                with pytest.raises(ValueError, match="Frame rate must be positive"):
                    extractor.calculate_frame_timestamps(5, -1.0)
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)
    
    def test_output_directory_creation(self, tmp_path):
        """Test that output directory is created if it doesn't exist"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
        
        try:
            with patch('frame_extractor.shutil.which') as mock_which:
                mock_which.return_value = '/usr/bin/ffmpeg'
                
                extractor = FrameExtractor(video_path)
                
                # Create a nested output directory path
                output_dir = tmp_path / "level1" / "level2" / "frames"
                assert not output_dir.exists()
                
                # Mock subprocess to avoid actually running ffmpeg
                with patch('frame_extractor.subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    
                    # Mock os.listdir to return empty list (no frames extracted)
                    with patch('frame_extractor.os.listdir') as mock_listdir:
                        mock_listdir.return_value = []
                        
                        try:
                            extractor.extract_frames(str(output_dir))
                        except (RuntimeError, FileNotFoundError):
                            # Ignore extraction errors - we only care that directory is created
                            pass
                        
                        # Check that directory was created
                        assert output_dir.exists()
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)
