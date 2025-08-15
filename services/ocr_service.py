# services/ocr_service.py

import tempfile
from pathlib import Path

# Temporary storage for files per user
user_files = {}  # chat_id -> {"path": Path, "type": ...}


def save_file(chat_id, file_bytes, filename):
    """
    Save an uploaded file to a temp folder and register it in user_files.
    Returns (Path, file_type).
    """
    temp_dir = Path(tempfile.gettempdir()) / "ocr_bot"
    temp_dir.mkdir(parents=True, exist_ok=True)

    file_path = temp_dir / filename
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    ext = file_path.suffix.lower()
    if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]:
        file_type = "image"
    elif ext == ".pdf":
        file_type = "pdf"
    elif ext in [".xls", ".xlsx"]:
        file_type = "excel"
    else:
        file_type = "unknown"

    user_files[chat_id] = {"path": file_path, "type": file_type}
    return file_path, file_type


def get_user_file(chat_id):
    return user_files.get(chat_id)


def remove_user_file(chat_id):
    if chat_id in user_files:
        try:
            # try to remove the saved file as well
            p = user_files[chat_id].get("path")
            if p and Path(p).exists():
                Path(p).unlink(missing_ok=True)
        except Exception:
            pass
        del user_files[chat_id]
