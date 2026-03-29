import easyocr

class OCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'de', 'pl'], gpu=True)

    def extract_text(self, photo_path: str) -> str:
        result = self.reader.readtext(photo_path)
        return "\n".join([item[1] for item in result])