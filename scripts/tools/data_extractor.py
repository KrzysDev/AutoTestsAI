from backend.app.services.data_extraction_service import DataExtractionService
import tkinter as tk
from tkinter import filedialog
import os
import json
from backend.app.models.schemas import Chunk

def main():
    root = tk.Tk()
    root.withdraw()

    extracted_data = []

    extractor = DataExtractionService()

    directory_path = filedialog.askdirectory(
        title="Wybierz folder ze zdjęciami"
    )
    
    if not directory_path:
        print("Nie wybrano folderu.")
        return

    print(f"Wybrano folder: {directory_path}")

    file_name = input("Podaj nazwę pliku (z zapisanymi danymi): ")
    
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.jpg', '.png'))]
    
    if not image_files:
        print("Nie znaleziono plików .jpg ani .png w wybranym folderze.")
        return

    print(f"Znaleziono {len(image_files)} zdjęć do przetworzenia.")

    images_processed = 0

    for filename in image_files:
        file_path = os.path.join(directory_path, filename)
        print(f"\n--- Przetwarzanie pliku: {file_path} ---")
        
        try:
            print(f"processing images... {images_processed}/{len(image_files)}")
            
            chunks = extractor.extract_data("vocab", "en", "B2", file_path)
            
            extracted_data.extend(chunks)

            images_processed += 1
            
        except Exception as e:
            print(f"Błąd podczas odpytywania modelu dla pliku {filename}: {e}")
            images_processed += 1
    
    with open(f"C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    
    

if __name__ == "__main__":
    main()
