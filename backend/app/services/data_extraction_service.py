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
        self.vocab_count = 0
        self.gram_count = 0

    def extract_data(self, photo_path: str, extraction_type: Literal["vocab", "gram"], language: Literal["en", "de"]):
        if extraction_type == "vocab":
            return self.__extract_vocab(photo_path, language)
        elif extraction_type == "gram":
            return self.__extract_gram(photo_path, language)
        

    """Used to extract vocabulary from OCR text"""
    def __extract_vocab(self, photo_path: str, language: Literal["en", "de"]):

        #deleting sliced photos from previous extractions

        if os.path.exists(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}"):
            for filename in os.listdir(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}"):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    os.remove(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}\\{filename}")

        image_slicer.slice_image(photo_path, 
        cols=2, 
        rows=2, 
        output_dir=rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}"
        )

        all_answers = []

        all_files = len(os.listdir(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}"))
        files_elapsed = 0
        for filename in os.listdir(rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}"):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                    path = rf"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\vocabulary_dataset\tiles_{self.vocab_count}\\{filename}"
                    answer = self.ai_service.ask_ollama_local_with_photo(prompts.get_data_extraction_prompt(language), path)
                    files_elapsed += 1
                    corrected_answer = self.ai_service.ask_ollama_cloud(prompts.get_data_correction_prompt(language, answer), model='gpt-oss:120b')
                    all_answers.append(corrected_answer)

        self.vocab_count += 1
        
        return all_answers
       
        

    def __extract_gram(self, photo_path: str, language: Literal["en", "de"]):
        all_answers = []
        for filename in os.listdir(rf"{photo_path}"):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                path = rf"{photo_path}\\{filename}"
                answer = self.ai_service.ask_ollama_local_with_photo(prompts.get_grammar_extraction_prompt(language), path)
                corrected_answer = self.ai_service.ask_ollama_cloud(prompts.get_data_grammar_correction_prompt(language, answer), model='gpt-oss:120b')
                all_answers.append(corrected_answer)

        self.gram_count += 1
        
        return all_answers
        
