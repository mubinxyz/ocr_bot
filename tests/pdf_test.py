# import pdfplumber
# import easyocr
# import numpy as np
# from PIL import Image

# reader = easyocr.Reader(['en', 'fa'])

# with pdfplumber.open("sample.pdf") as pdf:
#     for page_num, page in enumerate(pdf.pages, start=1):
#         text = page.extract_text()
#         if text:
#             print(f"Page {page_num} text (no OCR needed):\n{text}")
#         else:
#             # Render image and OCR
#             img = page.to_image(resolution=300).original
#             text_ocr = reader.readtext(np.array(img), detail=0)
#             print(f"Page {page_num} OCR:\n", "\n".join(text_ocr))
#         print("-" * 50)

import fitz  # pymupdf
import easyocr
import numpy as np

# Create EasyOCR reader
reader = easyocr.Reader(['en', 'fa'])  # English + Persian

# Open the PDF
pdf = fitz.open("sample.pdf")

for page_num in range(len(pdf)):
    page = pdf[page_num]
    # Render page to a high-resolution image (pixmap)
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # 3x zoom for better OCR
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    
    # OCR
    text = reader.readtext(img, detail=0)
    print(f"Page {page_num+1}:\n", "\n".join(text))
    print("-" * 50)
