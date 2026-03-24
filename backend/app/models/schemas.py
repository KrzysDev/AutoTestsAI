from pydantic import BaseModel, field_validator
from typing import Literal

class ChunkMetadata(BaseModel):
    subject: str
    content: str

class FlashcardChunk(BaseModel):
    id: str
    section: Literal["vocabulary", "grammar"]
    language: Literal["en", "de"]
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    metadata: ChunkMetadata