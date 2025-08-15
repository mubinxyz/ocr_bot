# services/ocr_flow.py
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from services.start_service import init_user, clear_awaiting_file
from services.ocr_service import save_file, remove_user_file
from services.ocr_runner import run_tesseract, save_txt, save_docx, contains_rtl

USER_FILES = {}  # chat_id -> {"path": Path, "type": "pdf/photo"}

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tg_user = update.effective_user

    # Ensure user exists in DB
    init_user(
        chat_id=chat_id,
        username=tg_user.username if tg_user else None,
        first_name=tg_user.first_name if tg_user else None,
        last_name=tg_user.last_name if tg_user else None
    )

    # Receive file (document or highest-res photo)
    if update.message.document:
        doc = update.message.document
        f = await doc.get_file()
        filename = doc.file_name or f"{chat_id}_document"
    elif update.message.photo:
        photo = update.message.photo[-1]
        f = await photo.get_file()
        filename = f"{chat_id}_photo.jpg"
    else:
        await update.message.reply_text("Unsupported file type.")
        return

    file_bytes = await f.download_as_bytearray()
    saved_path, file_type = save_file(chat_id, file_bytes, filename)

    # Inform user and start processing in background thread
    message = await update.message.reply_text("File received. Processing with Tesseract, please wait...")

    path = Path(saved_path)
    loop = asyncio.get_running_loop()
    try:
        # run_tesseract (CPU-bound) in executor
        text = await loop.run_in_executor(None, run_tesseract, path)
    except Exception as e:
        await message.edit_text(f"Error during OCR: {e}")
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
    await message.edit_text(f"✅ OCR finished. Preview:\n\n{preview}")
    await update.message.reply_document(open(txt_path, "rb"))
    await update.message.reply_document(open(docx_path, "rb"))

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
