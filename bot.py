"""
Telegram Bot for Video Processing with AI
Main bot file
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_ID
from database import Database
from ai_processor import AIProcessor
from video_processor import VideoProcessor
from utils import setup_logging, download_large_file, format_file_size

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize components
db = Database()
ai_processor = AIProcessor()
video_processor = VideoProcessor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    db.add_user(user_id, username)
    
    await update.message.reply_text(
        "👋 Привет! Я бот для обработки видео с AI.\n\n"
        "Отправьте мне видео, и я обработаю его для вас!"
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video messages"""
    video_path = None
    try:
        user_id = update.effective_user.id
        video = update.message.video
        
        if not video:
            await update.message.reply_text("❌ Не удалось получить информацию о видео.")
            return
        
        # Get video file info
        file_id = video.file_id
        file_size = video.file_size
        file_name = video.file_name or f"video_{file_id}.mp4"
        
        # Check file size limit (2 GB)
        max_size_bytes = 2 * 1024 * 1024 * 1024  # 2 GB
        if file_size > max_size_bytes:
            size_gb = file_size / (1024 * 1024 * 1024)
            await update.message.reply_text(
                f"❌ Файл слишком большой ({size_gb:.2f} ГБ).\n"
                f"Максимальный размер: 2 ГБ"
            )
            return
        
        # Send processing message with file info
        file_size_str = format_file_size(file_size)
        processing_msg = await update.message.reply_text(
            f"⏳ Загружаю видео...\n"
            f"📦 Размер: {file_size_str}"
        )
        
        # Download video using new method for large files
        video_path = f"temp_{user_id}_{file_id}.mp4"
        
        # Try to download the video
        success, error_msg = await download_large_file(file_id, file_size, video_path)
        
        if not success:
            await processing_msg.edit_text(error_msg)
            return
        
        # Update status
        await processing_msg.edit_text(
            f"✅ Видео загружено!\n"
            f"⏳ Обрабатываю видео..."
        )
        
        # Process video
        result = await video_processor.process_video(video_path)
        
        # Get AI analysis
        analysis = await ai_processor.analyze_video(result)
        
        # Send result
        await processing_msg.edit_text(
            f"✅ Видео обработано!\n\n{analysis}"
        )
        
        # Log to database
        db.log_video_processing(user_id)
        
    except Exception as e:
        logger.error(f"Ошибка обработки видео: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке видео.\n"
                "Пожалуйста, попробуйте ещё раз позже."
            )
        except:
            pass
    finally:
        # Clean up: remove temporary file
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"Temporary file removed: {video_path}")
            except Exception as e:
                logger.error(f"Failed to remove temporary file: {e}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    stats_data = db.get_stats()
    await update.message.reply_text(
        f"📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {stats_data['total_users']}\n"
        f"🎬 Обработано видео: {stats_data['total_videos']}"
    )


def main():
    """Start the bot"""
    logger.info("Starting bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Start bot
    logger.info("Bot is running!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
