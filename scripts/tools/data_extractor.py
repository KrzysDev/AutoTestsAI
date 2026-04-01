from backend.app.services.data_extraction_service import DataExtractionService
import os
import tkinter as tk
from backend.app.models.schemas import Chunk, ChunkMetadata
from backend.app.services.ai_service import AiService
import hashlib

from tkinter import filedialog
from typing import Literal
import json

def main():
   level : Literal["A1", "A2", "B1", "B2", "C1", "C2"] = input("Enter level: ")
   language : Literal["en", "de"] = input("Enter language: ")
   section : Literal["vocab", "gram"] = input("Enter section: ")
   file_name : str = input("Enter file name: ")

   root = tk.Tk()
   root.withdraw()

   extraction_path : str = filedialog.askdirectory(title="Select folder with photos to extract data from")
   save_path : str = filedialog.askdirectory(title="Select folder to save data to")

   service = DataExtractionService()

   all_chunks : list[Chunk] = []

   for filename in os.listdir(extraction_path):
       if filename.endswith(".jpg") or filename.endswith(".png"):
           path = os.path.join(extraction_path, filename)
           data = service.extract_data(path, section, language)
           try:
               chunk = Chunk(
                   id=hashlib.md5(path.encode()).hexdigest(),
                   section=section,
                   language=language,
                   level=level,
                   metadata=ChunkMetadata(
                       subject=data["subject"],
                       content="".join(f"{word['word']} - {word['translation']}\n" for word in data["content"])
                   )
               )
               all_chunks.append(chunk)
           except Exception as e:
               print(f"Error with file {filename}: {e}")

   with open(os.path.join(save_path, f"{file_name}.json"), "w", encoding="utf-8") as f:
       json.dump([chunk.model_dump() for chunk in all_chunks], f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()