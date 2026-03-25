from backend.app.services.data_extraction_service import DataExtractionService
import easyocr

reader = easyocr.Reader(['en', 'pl'])

text = reader.readtext("C:\\Users\\USER\\Desktop\\Ai Test Generator Dataset-20260321T142317Z-1-001\\Ai Test Generator Dataset\\1.jpg")

extracted_text = ""
for _, text, _ in text:
    extracted_text += text + "\n"

print("OCR text: ")
print(extracted_text)
print('\n'*3)
print("Extracted data: ")

service = DataExtractionService()

print(service.extract_data(extracted_text, "vocabulary", "en", "B2"))
