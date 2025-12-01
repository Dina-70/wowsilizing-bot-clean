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
from utils import setup_logging

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
    try:
        user_id = update.effective_user.id
        
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Обрабатываю видео...")
        
        # Download video
        video_file = await update.message.video.get_file()
        video_path = f"temp_{user_id}_{video_file.file_id}.mp4"
        await video_file.download_to_drive(video_path)
        
        # Process video
        result = await video_processor.process_video(video_path)
        
        # Get AI analysis
        analysis = await ai_processor.analyze_video(result)
        
        # Send result
        await processing_msg.edit_text(
            f"✅ Видео обработано!\n\n{analysis}"
        )
        
        # Clean up
        os.remove(video_path)
        
        # Log to database
        db.log_video_processing(user_id)
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке видео.")


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
