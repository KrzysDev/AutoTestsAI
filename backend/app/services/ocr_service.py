import easyocr
import image_slicer
import os

class OCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'de', 'pl'], gpu=True)
        self.count = 0

    def extract_text(self, photo_path: str) -> str:
        image_slicer.slice_image(photo_path, cols=4, rows=4, output_dir=rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}")

        tiles = []
        for filename in os.listdir(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}"):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                with open(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}\{filename}", "rb") as f:
                    tiles.append(f.read())
        
        result = []

        id_count = 0

        for tile in tiles:
            extracted_text = self.reader.readtext(tile)
            result.append({
                "id": id_count,
                "text": " ".join([item[1] for item in extracted_text])
            })

            id_count += 1

        self.count += 1
        return result