# config.py
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
DB_PATH = os.getenv("DB_PATH", "database.db")

# Optional: explicit tesseract binary and tessdata folder (absolute paths)
# If left empty, the code will try vendor/Tesseract-OCR or system PATH.
TESSERACT_CMD = os.getenv("TESSERACT_CMD")  # e.g. C:\project\vendor\Tesseract-OCR\tesseract.exe
TESSDATA_DIR = Path(os.getenv("TESSDATA_DIR")) if os.getenv("TESSDATA_DIR") else None

# OCR languages for EasyOCR and default Tesseract lang list (comma separated OR list)
# Example .env: OCR_LANGS=en,fa
OCR_LANGS = [s.strip() for s in os.getenv("OCR_LANGS", "en,fa").split(",") if s.strip()]
