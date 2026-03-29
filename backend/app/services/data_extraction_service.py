import enum


class ExtractionType(Enum):
    cloud = 1
    local = 2

class DataExtractionService:
    def __init__(self):
        self.ai_service = AiService()
        self.chunking_service = ChunkingService()
        self.existing_subjects = []

    def extract_data(self):
        pass

    """Used to extract vocabulary from OCR text"""
    def __extract_vocab(self, text: str,language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], extraction_type: ExtractionType = ExtractionType.cloud) -> list[Chunk]:
        pass

        
            

        

    def __extract_gram(self, text: str):
        pass
        
