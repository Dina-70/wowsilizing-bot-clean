"""
Utility functions for the bot
"""
import logging
import sys
import httpx
from pathlib import Path
from config import LOG_LEVEL, BOT_TOKEN

logger = logging.getLogger(__name__)


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


async def download_large_file(file_id: str, file_size: int, output_path: str) -> tuple[bool, str]:
    """
    Download large files from Telegram using direct file_path URL.
    This bypasses the 20 MB limit of bot.get_file()
    
    Args:
        file_id: Telegram file ID
        file_size: File size in bytes
        output_path: Path where to save the downloaded file
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        # Check if file is too large (> 2 GB)
        max_size_bytes = 2 * 1024 * 1024 * 1024  # 2 GB
        if file_size > max_size_bytes:
            size_gb = file_size / (1024 * 1024 * 1024)
            return False, f"❌ Файл слишком большой ({size_gb:.2f} ГБ). Максимальный размер: 2 ГБ"
        
        # First, try to get file info from Telegram API
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get file path from Telegram
            get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
            response = await client.get(get_file_url, params={"file_id": file_id})
            
            if response.status_code != 200:
                logger.error(f"Failed to get file info: {response.text}")
                return False, "❌ Не удалось получить информацию о файле"
            
            result = response.json()
            if not result.get("ok"):
                logger.error(f"Telegram API error: {result}")
                return False, "❌ Ошибка при получении файла от Telegram"
            
            file_path = result["result"]["file_path"]
            
            # Download the file using direct URL
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            logger.info(f"Downloading file from: {download_url}")
            
            # Download with streaming to handle large files
            async with client.stream("GET", download_url) as stream_response:
                if stream_response.status_code != 200:
                    logger.error(f"Failed to download file: {stream_response.status_code}")
                    return False, "❌ Не удалось скачать файл"
                
                # Write file in chunks
                with open(output_path, "wb") as f:
                    async for chunk in stream_response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
            
            logger.info(f"File downloaded successfully to: {output_path}")
            return True, ""
            
    except httpx.TimeoutException:
        logger.error("Timeout while downloading file")
        return False, "❌ Превышено время ожидания при загрузке файла"
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False, f"❌ Ошибка при загрузке файла: {str(e)}"
