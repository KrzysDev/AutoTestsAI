import json
import hashlib
from typing import Literal
from enum import Enum
from backend.app.services.ai_service import AiService
from backend.app.services.chunking_service import ChunkingService
from backend.app.models.schemas import Chunk, ChunkMetadata
import sys



from backend.app.models.prompts import SystemPrompts as prompts

class ExtractionType(Enum):
    cloud = 1
    local = 2

class DataExtractionService:
    def __init__(self):
        self.ai_service = AiService()
        self.chunking_service = ChunkingService()
        self.existing_subjects = []

    def extract_data(self, section: Literal["vocab", "gram"], language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], photo_path: str = None, extraction_type: ExtractionType = ExtractionType.cloud):
        if section == "vocab":
            return self.__extract_vocab(text, language, level, extraction_type)
        elif section == "gram":
            return self.__extract_gram(text, language, level, extraction_type)

    """Used to extract vocabulary from OCR text"""
    def __extract_vocab(self, text: str,language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], extraction_type: ExtractionType = ExtractionType.cloud) -> list[Chunk]:
        pass

        
            

        

    def __extract_gram(self, text: str):
        pass
        
