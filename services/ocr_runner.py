# services/ocr_runner.py
import os
from pathlib import Path
import logging

import pytesseract
import easyocr
from PIL import Image
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import fitz  # PyMuPDF for PDF -> image conversion

from config import TESSERACT_CMD, TESSDATA_DIR, OCR_LANGS

logger = logging.getLogger(__name__)

# --- Discover vendor tesseract if present ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_TESS_PATH = PROJECT_ROOT / "vendor" / "Tesseract-OCR" / "tesseract.exe"
VENDOR_TESSDATA = PROJECT_ROOT / "vendor" / "Tesseract-OCR" / "tessdata"

tess_cmd = None
if TESSERACT_CMD:
    tess_cmd = Path(TESSERACT_CMD)
    logger.debug("Using TESSERACT_CMD from config: %s", tess_cmd)
elif VENDOR_TESS_PATH.exists():
    tess_cmd = VENDOR_TESS_PATH
    logger.debug("Found vendor tesseract at: %s", tess_cmd)

if tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = str(tess_cmd)

# TESSDATA_PREFIX
if TESSDATA_DIR:
    tessdata_dir = Path(TESSDATA_DIR)
    logger.debug("Using TESSDATA_DIR from config: %s", tessdata_dir)
elif VENDOR_TESSDATA.exists():
    tessdata_dir = VENDOR_TESSDATA
    logger.debug("Using vendor tessdata at: %s", tessdata_dir)
else:
    tessdata_dir = None

if tessdata_dir:
    os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

# EasyOCR reader reuse
_reader = None


def _get_easyocr_reader():
    global _reader
    if _reader is None:
        langs = OCR_LANGS if OCR_LANGS else ["en"]
        logger.info("Initializing EasyOCR Reader for languages: %s", langs)
        _reader = easyocr.Reader(langs, gpu=False)
    return _reader


# --- helper: convert PDF to list of PIL Images ---
def pdf_to_images(pdf_path: Path, dpi: int = 300):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    images = []
    doc = fitz.open(str(pdf_path))
    mat = fitz.Matrix(dpi / 72, dpi / 72)  # scale to desired DPI
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        mode = "RGB" if pix.n == 3 else "RGBA"
        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        images.append(img)
    doc.close()
    return images


# --- OCR functions (handle images and PDFs) ---
def run_tesseract(file_path: Path, langs: str = "eng+fas"):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Tesseract: file not found: {file_path}")

    if file_path.suffix.lower() == ".pdf":
        images = pdf_to_images(file_path)
        pages_text = []
        for img in images:
            pages_text.append(pytesseract.image_to_string(img, lang=langs))
        return "\f".join(pages_text)
    else:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang=langs)


def run_easyocr(file_path: Path):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"EasyOCR: file not found: {file_path}")

    reader = _get_easyocr_reader()
    if file_path.suffix.lower() == ".pdf":
        images = pdf_to_images(file_path)
        pages = []
        for img in images:
            res = reader.readtext(img, detail=0)
            pages.append("\n".join(res))
        return "\f".join(pages)
    else:
        res = reader.readtext(str(file_path), detail=0)
        return "\n".join(res)


# --- Output helpers ---
def save_txt(text: str, out_path: Path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)


def save_docx(text: str, out_path: Path, rtl: bool = False):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()
    pages = text.split("\f") if "\f" in text else [text]
    for pi, page in enumerate(pages):
        for line in page.splitlines():
            p = doc.add_paragraph(line)
            if rtl:
                p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        if pi != len(pages) - 1:
            doc.add_page_break()
    doc.save(out_path)


def contains_rtl(text: str) -> bool:
    for ch in text:
        if "\u0600" <= ch <= "\u06FF":
            return True
    return False
