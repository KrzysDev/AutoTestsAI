from backend.app.services.data_extraction_service import DataExtractionService

def main():
    service = DataExtractionService()
    data = service.extract_data(r"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\Ai Test Generator Dataset - Grammar", "gram", "en")
    print(data)

if __name__ == "__main__":
    main()