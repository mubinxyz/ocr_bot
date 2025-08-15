from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from services.start_service import init_user, set_awaiting_file

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user or update.message.from_user

    # Init user and reset state
    init_user(
        chat_id=update.effective_chat.id,
        username=tg_user.username if tg_user else None,
        first_name=tg_user.first_name if tg_user else None,
        last_name=tg_user.last_name if tg_user else None
    )

    # Set bot to wait for a file now
    set_awaiting_file(update.effective_chat.id)

    await update.message.reply_text(
        "👋 Hi! Send me a photo, PDF, or Excel file and I'll OCR it for you.\n\n"
        "After you send the file I'll ask you to choose an OCR method:\n"
        "• TESSERACT — very fast, best for printed / clean text\n"
        "• EASYOCR — slower but better with handwriting and messy layouts\n\n"
        "When you're ready, just upload the file or image now."
    )

# Handler instance to register in bot.py
handler = CommandHandler("start", start_command)
