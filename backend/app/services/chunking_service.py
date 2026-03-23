import copy
import hashlib
from backend.app.models.schemas import FlashcardChunk

class ChunkingService:
    def __init__(self):
        pass

    def chunk_vocabulary(self, extracted_chunk: FlashcardChunk, chunk_size: int = 50, overlap_size: int = 10, min_chunk_size: int = 20):
        chunks = []
        content = extracted_chunk['metadata']['content']
        words = content.split()

        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            new_chunk = copy.deepcopy(extracted_chunk)
            new_chunk['metadata']['content'] = chunk_text
            content_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
            new_chunk['id'] = f'vocab-{content_hash}'
            chunks.append(new_chunk)
            
            #overlap
            start += chunk_size - overlap_size

        if len(chunks) > 1:
            last_words = chunks[-1]['metadata']['content'].split()
            if len(last_words) < min_chunk_size:
                merged_text = chunks[-2]['metadata']['content'] + " " + chunks[-1]['metadata']['content']
                chunks[-2]['metadata']['content'] = merged_text
                content_hash = hashlib.md5(merged_text.encode()).hexdigest()[:8]
                chunks[-2]['id'] = f'vocab-{content_hash}'
                chunks.pop()

        return chunks
