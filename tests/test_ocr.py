import easyocr

# Create a Reader object (specify languages)
reader = easyocr.Reader(['en'])  # For English
# For Persian: reader = easyocr.Reader(['fa'])
# For English + Persian: reader = easyocr.Reader(['en', 'fa'])

# Run OCR on an image
results = reader.readtext('t1.png', detail=0)

# detail=0 → just text list, detail=1 → boxes + confidence + text
print(results)
