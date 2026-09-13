from app.tools.ocr import extract_text_from_image


image_path = r"C:\Users\Diksha\OneDrive\Desktop\test.png.png"

result = extract_text_from_image(image_path)

print("\n===== OCR RESULT =====")
print(result)