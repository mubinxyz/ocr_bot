# services/ocr_runner.py
import os
from pathlib import Path
import logging

import pytesseract
from PIL import Image
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import fitz  # PyMuPDF for PDF -> image conversion

from config import TESSERACT_CMD, TESSDATA_DIR, OCR_LANGS

logger = logging.getLogger(__name__)

# -------------------------
# Ensure Tesseract binary & tessdata are set to bundled vendor by default
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_TESS_PATH = PROJECT_ROOT / "vendor" / "Tesseract-OCR" / "tesseract.exe"
VENDOR_TESSDATA = PROJECT_ROOT / "vendor" / "Tesseract-OCR" / "tessdata"

# decide tesseract command: priority -> explicit env TESSERACT_CMD, vendor bundle, system (none)
tess_cmd = None
if TESSERACT_CMD:
    tess_cmd = Path(TESSERACT_CMD)
    logger.debug("Using TESSERACT_CMD from config: %s", tess_cmd)
elif VENDOR_TESS_PATH.exists():
    tess_cmd = VENDOR_TESS_PATH
    logger.debug("Found vendor tesseract at: %s", tess_cmd)
else:
    logger.debug("No bundled tesseract found; will rely on system tesseract if available")

if tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = str(tess_cmd)

# decide tessdata dir: priority -> explicit env TESSDATA_DIR, vendor bundle, system (none)
if TESSDATA_DIR:
    tessdata_dir = Path(TESSDATA_DIR)
    logger.debug("Using TESSDATA_DIR from config: %s", tessdata_dir)
elif VENDOR_TESSDATA.exists():
    tessdata_dir = VENDOR_TESSDATA
    logger.debug("Using vendor tessdata at: %s", tessdata_dir)
else:
    tessdata_dir = None
    logger.debug("No tessdata_dir configured; relying on default Tesseract locations")

if tessdata_dir:
    os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

# -------------------------
# language mapping helper
# -------------------------
def _map_lang_codes(codes):
    """
    Map user-friendly language codes to tesseract traineddata names.
    Accepts list of strings like ['en','fa'] or ['eng','fas'].
    Returns list of tesseract-trained names, e.g. ['eng','fas'].
    """
    code_map = {
        "en": "eng",
        "eng": "eng",
        "fa": "fas",
        "fas": "fas",
        "ar": "ara",
        "ara": "ara",
        "de": "deu",
        "deu": "deu",
        "ru": "rus",
        "rus": "rus",
        "es": "spa",
        "spa": "spa",
        "pt": "por",
        "por": "por",
        "zh": "chi_sim",
        "zh-cn": "chi_sim",
        "zh-tw": "chi_tra",
    }
    mapped = []
    for c in (codes or []):
        key = str(c).strip().lower()
        mapped.append(code_map.get(key, key))
    # preserve order, remove duplicates
    seen = set()
    final = []
    for m in mapped:
        if m not in seen:
            final.append(m)
            seen.add(m)
    return final


def _tesseract_lang_string():
    """
    Build the final Tesseract language string, e.g. "eng+fas".
    If OCR_LANGS in config is empty, default to 'eng'.
    """
    if not OCR_LANGS:
        return "eng"
    mapped = _map_lang_codes(OCR_LANGS)
    return "+".join(mapped) if mapped else "eng"


# -------------------------
# PDF -> images helper
# -------------------------
def pdf_to_images(pdf_path: Path, dpi: int = 300):
    """
    Convert a PDF to a list of PIL.Image objects (one per page).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    images = []
    doc = fitz.open(str(pdf_path))
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        mode = "RGB" if pix.n == 3 else "RGBA"
        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        images.append(img)
    doc.close()
    return images


# -------------------------
# Core OCR functions
# -------------------------
def run_tesseract(file_path, langs: str = None):
    """
    Run Tesseract on an image file or PDF.
    - file_path: Path or str to image/pdf
    - langs: optional tesseract language string like 'eng+fas'; if None, built from config OCR_LANGS
    Returns extracted text. For multi-page PDFs returns pages joined by '\f'.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Tesseract: file not found: {file_path}")

    if langs is None:
        langs = _tesseract_lang_string()

    if file_path.suffix.lower() == ".pdf":
        images = pdf_to_images(file_path)
        pages_text = []
        for img in images:
            pages_text.append(pytesseract.image_to_string(img, lang=langs))
        return "\f".join(pages_text)
    else:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang=langs)


# -------------------------
# Output helpers
# -------------------------
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
