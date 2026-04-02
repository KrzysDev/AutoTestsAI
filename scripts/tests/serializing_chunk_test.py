import json

from backend.app.models.schemas import Chunk, ChunkMetadata

chunk = Chunk(
    id="1",
    section="vocabulary",
    language="en",
    level="A1",
    metadata=ChunkMetadata(
        subject="test",
        content="test"
    )
)

with open("chunk.json", "w", encoding="utf-8") as f:
    json.dump(chunk.model_dump(), f, ensure_ascii=False, indent=2)