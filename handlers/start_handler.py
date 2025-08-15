# handlers/start_handler.py

import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ContextTypes
from services.start_service import init_user, set_awaiting_file

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start: ensure user exists, put them in awaiting-file state,
    and send a short instruction message.
    """
    try:
        tg_user = update.effective_user or update.message.from_user

        # Persist user and reset awaiting flag
        init_user(
            chat_id=update.effective_chat.id,
            username=tg_user.username if tg_user else None,
            first_name=tg_user.first_name if tg_user else None,
            last_name=tg_user.last_name if tg_user else None
        )

        # Bot will now wait for a file from this user
        set_awaiting_file(update.effective_chat.id)

        # Send instructions (only Tesseract is used now)
        await update.message.reply_text(
            "👋 Hi! Send me a photo or PDF and I'll OCR it using Tesseract.\n\n"
            "• Send a photo (JPG/PNG) or a PDF file.\n"
            "• I'll process it and return a text preview, a .txt file and a .docx (each PDF page becomes a Word page).\n\n"
            "When you're ready, upload the file now.",
            reply_markup=ReplyKeyboardRemove()
        )

        logger.info("Started OCR session for chat_id=%s", update.effective_chat.id)

    except Exception as e:
        logger.exception("Error in start_command: %s", e)
        await update.message.reply_text("Something went wrong starting the OCR session. Please try /start again.")

# Handler instance to register in bot.py
handler = CommandHandler("start", start_command)
