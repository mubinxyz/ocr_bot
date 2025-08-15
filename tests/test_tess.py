import pytesseract
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tesseract binary
TESS_PATH = os.path.join(BASE_DIR, "..", "vendor", "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESS_PATH

# Correct: point to the 'tessdata' folder
tessdata_dir = os.path.join(BASE_DIR, "..", "vendor", "Tesseract-OCR", "tessdata")
os.environ["TESSDATA_PREFIX"] = tessdata_dir

# Debug
print("Binary exists?", os.path.exists(TESS_PATH))
print("tessdata exists?", os.path.exists(tessdata_dir))
print("eng.traineddata exists?", os.path.exists(os.path.join(tessdata_dir, "eng.traineddata")))

# OCR test
img = Image.open("sample.png")
text = pytesseract.image_to_string(img, lang="eng")
print(text)
