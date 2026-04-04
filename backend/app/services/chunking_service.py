import re
from backend.app.models.schemas import Chunk, ChunkMetadata

class ChunkingService:
    def __init__(self):
        pass

    def chuk_vocabulary(self, data: Chunk, chunk_size: int = 30) -> list[Chunk]:
        content = data.metadata.content.split("\n")
        chunks = []

        current_chunk: Chunk = Chunk(
            id=data.id,
            section=data.section,
            language=data.language,
            level=data.level,
            metadata=ChunkMetadata(
                subject=data.metadata.subject,
                content=""
            )
        )

        chunks_elapsed = 0

        for word in content:
            if not word.strip():
                continue

            if chunks_elapsed % chunk_size == 0 and chunks_elapsed != 0:
                chunks.append(current_chunk)
                current_chunk = Chunk(
                    id=data.id,
                    section=data.section,
                    language=data.language,
                    level=data.level,
                    metadata=ChunkMetadata(
                        subject=data.metadata.subject,
                        content=""
                    )
                )
            
            current_chunk.metadata.content += word + "\n"
            chunks_elapsed += 1

        

    def chunk_matura(self, text: str) -> list[str]:
        text = re.sub(r"Więcej arkuszy znajdziesz na stronie: arkusze\.pl", "", text)
        text = re.sub(r"Strona \d+ z \d+", "", text)
        text = re.sub(r"[A-Z0-9]+-[A-Z0-9]+-[0-9]+", "", text)
        chunks = re.split(r"(?i)(?=Zadanie\s+\d+)", text)
        cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        return cleaned_chunks
