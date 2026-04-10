from backend.app.services.ocr_service import OCRService

def main():
    service = OCRService()
    text = service.extract_text(r"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\Ai Test Generator Dataset\2.jpg")
    for t in text:
        print(t)
        print("\n"*2)

    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(str(text))

if __name__ == "__main__":
    main()