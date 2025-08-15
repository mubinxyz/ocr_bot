# bot.py

import logging
from telegram.ext import Application, MessageHandler, filters
from config import LOG_LEVEL, BOT_TOKEN
from handlers.start_handler import handler as start_handler
from services.db_service import init_db
from services import ocr_flow

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

    # /start handler is now just welcome/help
    application.add_handler(start_handler)

    # Always listen for photos and documents
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, ocr_flow.handle_file))

    # Start polling
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
