from backend.app.services.data_extraction_service import DataExtractionService
import os
import tkinter as tk
from backend.app.models.schemas import Chunk, ChunkMetadata
from backend.app.services.ai_service import AiService
import hashlib

from tkinter import filedialog


def main():

    ai_service = AiService()

    service = DataExtractionService()

    root = tk.Tk()

    root.withdraw()

    extraction_path = filedialog.askdirectory(title="Select folder with photos")

    subjects = []

    count = 0

    for filename in os.listdir(extraction_path):
        if count % 2 == 1:
            subjects.append(ai_service.ask_ollama_local(f"zwroc tylko naglowek ktory okresla temat slowek. Nic wiecej. {filename}"))
        count += 1


    save_path = filedialog.askdirectory(title="Select folder to save data")

    total_data = []

    language = input("Enter language (en/de): ")
    level = input("Enter level (A1/A2/B1/B2/C1/C2): ")
    section = input("Enter section (vocab/gram): ")

    for filename in os.listdir(extraction_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            total_data.append(service.extract_data(os.path.join(extraction_path, filename), section, language))

    count = 1

    i = 0

    current_chunk = Chunk(
        id=f"",
        section=section,
        language=language,
        level=level,
        metadata=ChunkMetadata(
            subject=subjects[0],
            content=""
        )
    )   

    all_chunks = []

    for data in total_data:
        if count % 16 == 0:
            i += 1
            all_chunks.append(current_chunk)
            current_chunk = Chunk(
                id=f"",
                section=section,
                language=language,
                level=level,
                metadata=ChunkMetadata(
                    subject=subjects[i],
                    content=""
                )
            )   
        current_chunk.metadata.content += f"{data["content"]["word"]} - {data["content"]["translation"]}\n"
    
    with open(os.path.join(save_path, "data.json"), "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=4)
     

    
    
    

if __name__ == "__main__":
    main()