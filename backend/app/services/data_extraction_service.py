from backend.app.services.ai_service import AiService
from backend.app.models.schemas import Chunk, ChunkMetadata
import sys
import os
from backend.app.models.prompts import SystemPrompts as prompts

import image_slicer

from typing import Literal

class DataExtractionService:
    def __init__(self):
        self.ai_service = AiService()
        self.count = 0

    def extract_data(self, photo_path: str, extraction_type: Literal["vocab", "gram"], language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]):
        if extraction_type == "vocab":
            return self.__extract_vocab(photo_path, language, level)
        elif extraction_type == "gram":
            return self.__extract_gram(photo_path, language, level)
        

    """Used to extract vocabulary from OCR text"""
    def __extract_vocab(self, photo_path: str, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]):
        image_slicer.slice_image(photo_path, 
        cols=4, 
        rows=4, 
        output_dir=rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}"
        )

        all_answers = []

        tiles = []

        all_files = len(os.listdir(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}"))
        current_file = 0
        for filename in os.listdir(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}"):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                    path = rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.count}\\{filename}"
                    answer = self.ai_service.ask_ollama_local_with_photo(prompts.get_data_extraction_prompt(language), path)
                    print("current answer: ", answer, f"({current_file}/{all_files})")
                    all_answers.append(answer)
                    current_file += 1

        self.count += 1

        return all_answers
       
        

    def __extract_gram(self, photo_path: str, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]):
        pass
        
