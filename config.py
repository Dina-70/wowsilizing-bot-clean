"""
Configuration file for the bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# AI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# Video processing configuration
# Telegram supports up to 2 GB file uploads
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "2048"))  # 2 GB default
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"]

# Telegram file download limits
TELEGRAM_SMALL_FILE_LIMIT = 20 * 1024 * 1024  # 20 MB - limit for bot.get_file()
TELEGRAM_MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB - Telegram's max file size

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
