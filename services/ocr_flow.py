# services/ocr_flow.py
import asyncio
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from services.start_service import is_awaiting_file, clear_awaiting_file
from services.ocr_service import save_file, get_user_file, remove_user_file
from services.ocr_runner import run_tesseract, run_easyocr, save_txt, save_docx, contains_rtl

USER_FILES = {}  # chat_id -> {"path": Path, "type": "pdf/photo"}

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_awaiting_file(chat_id):
        # ignore files if not expecting one (or notify user)
        await update.message.reply_text("Please send /start first to begin an OCR session.")
        return

    # get file
    if update.message.document:
        doc = update.message.document
        f = await doc.get_file()
        filename = doc.file_name or f"{chat_id}_document"
    elif update.message.photo:
        # highest resolution photo
        photo = update.message.photo[-1]
        f = await photo.get_file()
        filename = f"{chat_id}_photo.jpg"
    else:
        await update.message.reply_text("Unsupported file type.")
        return

    file_bytes = await f.download_as_bytearray()
    saved_path, file_type = save_file(chat_id, file_bytes, filename)

    USER_FILES[chat_id] = {"path": Path(saved_path), "type": file_type}

    keyboard = [
        [
            InlineKeyboardButton("TESSERACT", callback_data="TESSERACT"),
            InlineKeyboardButton("EASYOCR", callback_data="EASYOCR")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select OCR method:\nTesseract: fast, printed text\nEasyOCR: slower, better for handwriting",
        reply_markup=reply_markup
    )


async def handle_ocr_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    method = query.data

    file_info = get_user_file(chat_id)
    if not file_info:
        await query.edit_message_text("File not found. Please send it again (use /start).")
        return

    await query.edit_message_text("Processing your file — this may take a moment...")

    path = Path(file_info["path"])

    loop = asyncio.get_running_loop()
    try:
        if method == "TESSERACT":
            text = await loop.run_in_executor(None, run_tesseract, path)
        else:
            text = await loop.run_in_executor(None, run_easyocr, path)
    except Exception as e:
        await query.edit_message_text(f"Error during OCR: {e}")
        remove_user_file(chat_id)
        clear_awaiting_file(chat_id)
        USER_FILES.pop(chat_id, None)
        return

    # Save outputs
    txt_path = path.with_suffix(".txt")
    docx_path = path.with_suffix(".docx")
    save_txt(text, txt_path)
    rtl = contains_rtl(text)
    save_docx(text, docx_path, rtl=rtl)

    # Send results (preview + files)
    preview = (text.strip()[:4000] + "...") if len(text.strip()) > 4000 else text.strip()
    await query.message.reply_text(f"✅ OCR finished. Preview:\n\n{preview}")
    await query.message.reply_document(open(txt_path, "rb"))
    await query.message.reply_document(open(docx_path, "rb"))

    # cleanup
    remove_user_file(chat_id)
    clear_awaiting_file(chat_id)
    USER_FILES.pop(chat_id, None)

    try:
        path.unlink(missing_ok=True)
        txt_path.unlink(missing_ok=True)
        docx_path.unlink(missing_ok=True)
    except Exception:
        pass
