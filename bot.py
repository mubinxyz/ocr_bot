# bot.py

import logging
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
from config import LOG_LEVEL, BOT_TOKEN
from handlers.start_handler import handler as start_handler
from services.db_service import init_db
from services.ocr_flow import handle_file, handle_ocr_choice

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    init_db()  # Create tables if not exist
    
    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(start_handler)  # /start
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    application.add_handler(CallbackQueryHandler(handle_ocr_choice))

    # Start polling
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
