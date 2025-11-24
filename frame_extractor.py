"""
Video Frame Extractor
Extracts frames from video files using ffmpeg
"""

import subprocess
import os
from typing import Optional
import json


class FrameExtractor:
    """Extract frames from video files using ffmpeg"""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.video_duration = None
        self.fps = None
        
    def get_video_info(self) -> dict:
        """Get video information using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                self.video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = next(
                (s for s in info.get('streams', []) if s.get('codec_type') == 'video'),
                None
            )
            
            if video_stream:
                # Parse FPS
                fps_str = video_stream.get('r_frame_rate', '30/1')
                num, denom = map(int, fps_str.split('/'))
                self.fps = num / denom if denom != 0 else 30.0
            
            # Get duration
            format_info = info.get('format', {})
            self.video_duration = float(format_info.get('duration', 0))
            
            return {
                'duration': self.video_duration,
                'fps': self.fps,
                'width': video_stream.get('width') if video_stream else None,
                'height': video_stream.get('height') if video_stream else None,
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get video info: {e}")
        except Exception as e:
            raise RuntimeError(f"Error parsing video info: {e}")
    
    def extract_frames(self, output_dir: str, frame_rate: float = 1.0, 
                      quality: int = 2) -> list:
        """
        Extract frames from video
        
        Args:
            output_dir: Directory to save extracted frames
            frame_rate: Frames per second to extract (default: 1 fps)
            quality: JPEG quality (1-31, lower is better, default: 2)
            
        Returns:
            List of extracted frame paths
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Output pattern
        output_pattern = os.path.join(output_dir, 'frame_%06d.jpg')
        
        # Build ffmpeg command
        cmd = [
            'ffmpeg',
            '-i', self.video_path,
            '-vf', f'fps={frame_rate}',  # Set frame rate
            '-q:v', str(quality),  # Quality setting
            '-y',  # Overwrite output files
            output_pattern
        ]
        
        try:
            # Run ffmpeg
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            # Get list of extracted frames
            frames = sorted([
                os.path.join(output_dir, f) 
                for f in os.listdir(output_dir) 
                if f.startswith('frame_') and f.endswith('.jpg')
            ])
            
            print(f"Extracted {len(frames)} frames to {output_dir}")
            return frames
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract frames: {e.stderr}")
    
    def calculate_frame_timestamps(self, num_frames: int, frame_rate: float) -> list:
        """
        Calculate timestamp for each extracted frame
        
        Args:
            num_frames: Number of frames extracted
            frame_rate: Frame extraction rate
            
        Returns:
            List of timestamps in seconds
        """
        if frame_rate <= 0:
            raise ValueError("Frame rate must be positive")
        
        interval = 1.0 / frame_rate
        timestamps = [i * interval for i in range(num_frames)]
        
        return timestamps
