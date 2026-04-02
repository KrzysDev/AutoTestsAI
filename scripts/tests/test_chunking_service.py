from backend.app.services.chunking_service import ChunkingService
from backend.app.models.schemas import Chunk, ChunkMetadata
import backend.app.models.schemas
service = ChunkingService()


ct = []


for i in range(200):
    ct.append(f"word {i} \n")

ct = "".join(ct)

chunked = service.chunk_data(Chunk(
    id="test",
    section="vocabulary",
    language="en",
    level="A1",
    metadata=ChunkMetadata(
        subject="test",
        content=ct
    )
))

print(len(chunked))
print(chunked)