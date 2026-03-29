from backend.app.services.data_extraction_service import DataExtractionService
import tkinter as tk
from tkinter import filedialog
import os
import json
from backend.app.models.schemas import Chunk

import sys

def main():
    root = tk.Tk()
    root.withdraw()

    extracted_data = []

    extractor = DataExtractionService()

    directory_path = filedialog.askdirectory(
        title="Select folder with images"
    )
    
    if not directory_path:
        print("No folder selected.")
        return

    print(f"Selected folder: {directory_path}")

    file_name = input("Enter file name (for saved data): ")
    
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.jpg', '.png'))]
    
    if not image_files:
        print("No .jpg or .png files found in selected folder.")
        return

    print(f"Found {len(image_files)} images to process.")

    images_processed = 0

    for filename in image_files:
        file_path = os.path.join(directory_path, filename)
        print(f"\n--- Processing file: {file_path} ---")
        
        try:
            print(f"processing images... {images_processed}/{len(image_files)}")
            
            chunks = extractor.extract_data("vocab", "en", "B2", file_path, ExtractionType.local)
            
        except Exception as e:
            print(f"Error while extracting data from file {filename}: {e}")
            images_processed += 1

        try:
            extracted_data.extend([chunk.model_dump() for chunk in chunks])
            with open(f"C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\checkpoints\\{images_processed}_{file_name}.json", "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            images_processed += 1

        except Exception as e:
            print(f"Error while saving data from file {filename}: {e}")

            print(f"Saving current work....")

            try:
                with open(f"C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\{file_name}.json", "w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"CANNOT SAVE - Error while saving data from file {filename}: {e}")

            sys.exit(1)
            
            images_processed += 1
    
    with open(f"C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    
    

if __name__ == "__main__":
    main()
