from pydantic import BaseModel, field_validator
from typing import Literal

class ChunkMetadata(BaseModel):
    subject: str
    content: str

class Chunk(BaseModel):
    id: str
    section: Literal["vocabulary", "grammar"]
    language: str
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    metadata: ChunkMetadata

    @field_validator("level")
    @classmethod
    def no_combined_levels(cls, v: str) -> str:
        if "/" in v or "-" in v:
            raise ValueError(f"Poziom musi być pojedynczy, dostałem: '{v}'")
        return v