import copy
import hashlib
from backend.app.models.schemas import FlashcardChunk

class ChunkingService:
    def __init__(self):
        pass

    def chunk_vocabulary(self, extracted_chunk: FlashcardChunk, chunk_size: int = 10):
        chunks = []
        current_string = ""
        content = extracted_chunk['metadata']['content']

        for i in range(len(content)):
            current_string += content[i]
            if content[i] == "." and (i + 1) % chunk_size == 0:
                new_chunk = copy.deepcopy(extracted_chunk)
                new_chunk['metadata']['content'] = current_string
                content_hash = hashlib.md5(current_string.encode()).hexdigest()[:8]
                new_chunk['id'] = f'vocab-{content_hash}'
                chunks.append(new_chunk)
                current_string = ""

        if current_string.strip():
            new_chunk = copy.deepcopy(extracted_chunk)
            new_chunk['metadata']['content'] = current_string
            content_hash = hashlib.md5(current_string.encode()).hexdigest()[:8]
            new_chunk['id'] = f'vocab-{content_hash}'
            chunks.append(new_chunk)

        return chunks
