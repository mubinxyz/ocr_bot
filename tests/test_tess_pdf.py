import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tesseract binary
TESS_PATH = os.path.join(BASE_DIR, "..", "vendor", "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESS_PATH

# TESSDATA_PREFIX points to 'tessdata' folder
tessdata_dir = os.path.join(BASE_DIR, "..", "vendor", "Tesseract-OCR", "tessdata")
os.environ["TESSDATA_PREFIX"] = tessdata_dir

# PDF path
pdf_path = os.path.join(BASE_DIR, "sample.pdf")

# Open PDF
doc = fitz.open(pdf_path)
all_text = ""

for page_number in range(len(doc)):
    page = doc.load_page(page_number)
    # Convert page to image (RGB)
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # OCR
    text = pytesseract.image_to_string(img, lang="eng")
    all_text += f"\n\n--- Page {page_number + 1} ---\n{text}"

# Save or print
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print("OCR done! Output saved to output.txt")
