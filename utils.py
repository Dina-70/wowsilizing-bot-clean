"""
Utility functions for the bot
"""
import logging
import sys
from config import LOG_LEVEL


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, LOG_LEVEL),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size (e.g., "5.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_video_file(file_path: str, max_size_mb: int = 50) -> tuple[bool, str]:
    """
    Validate video file
    
    Args:
        file_path: Path to the video file
        max_size_mb: Maximum allowed file size in MB
        
    Returns:
        tuple: (is_valid, error_message)
    """
    import os
    
    if not os.path.exists(file_path):
        return False, "Файл не найден"
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        return False, f"Файл слишком большой ({file_size_mb:.1f} MB). Максимальный размер: {max_size_mb} MB"
    
    return True, ""
