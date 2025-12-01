"""
Video processor module for video manipulation and analysis
"""
import logging
import subprocess
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self):
        """Initialize video processor"""
        logger.info("Video Processor initialized")
    
    async def process_video(self, video_path: str) -> dict:
        """
        Process video and extract metadata
        
        Args:
            video_path: Path to the video file
            
        Returns:
            dict: Video metadata including duration, resolution, fps
        """
        try:
            # Get video metadata using ffprobe
            metadata = self.get_video_metadata(video_path)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return {
                "duration": "Unknown",
                "resolution": "Unknown",
                "fps": "Unknown"
            }
    
    def get_video_metadata(self, video_path: str) -> dict:
        """
        Extract video metadata using ffprobe
        
        Args:
            video_path: Path to the video file
            
        Returns:
            dict: Video metadata
        """
        try:
            # Use ffprobe to get video information
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Extract video stream info
                video_stream = next(
                    (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
                    {}
                )
                
                duration = float(data.get("format", {}).get("duration", 0))
                width = video_stream.get("width", 0)
                height = video_stream.get("height", 0)
                fps = eval(video_stream.get("r_frame_rate", "0/1"))
                
                return {
                    "duration": f"{duration:.1f}",
                    "resolution": f"{width}x{height}",
                    "fps": f"{fps:.1f}"
                }
            else:
                logger.warning("ffprobe failed, returning default values")
                return {
                    "duration": "Unknown",
                    "resolution": "Unknown",
                    "fps": "Unknown"
                }
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {
                "duration": "Unknown",
                "resolution": "Unknown",
                "fps": "Unknown"
            }
    
    async def compress_video(self, input_path: str, output_path: str) -> bool:
        """
        Compress video file
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", "28",
                "-c:a", "aac",
                "-b:a", "128k",
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error compressing video: {e}")
            return False
