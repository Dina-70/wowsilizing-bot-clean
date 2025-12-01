"""
Database module for storing user data and statistics
"""
import sqlite3
import logging
from datetime import datetime
from config import DATABASE_URL

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        """Initialize database connection"""
        self.db_path = DATABASE_URL.replace("sqlite:///", "")
        self.init_db()
    
    def init_db(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Video processing log table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS video_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_user(self, user_id: int, username: str):
        """Add a new user to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                    (user_id, username)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding user: {e}")
    
    def log_video_processing(self, user_id: int):
        """Log a video processing event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO video_logs (user_id) VALUES (?)",
                    (user_id,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging video processing: {e}")
    
    def get_stats(self):
        """Get bot statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total users
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Get total processed videos
                cursor.execute("SELECT COUNT(*) FROM video_logs")
                total_videos = cursor.fetchone()[0]
                
                return {
                    "total_users": total_users,
                    "total_videos": total_videos
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_users": 0, "total_videos": 0}
