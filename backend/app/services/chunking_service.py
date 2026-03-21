from backend.app.models.schemas import FlashcardChunk

class ChunkingService:
    def __init__(self):
        pass

    def chunk_vocabulary(self, extracted_chunk: FlashcardChunk, chunk_size: int = 10):
        chunks = []
        current_string = ""
        
        for i in range(1, chunk_size):
            if(chunks_size['metadata']['content'][i] == "." and i % chunk_size == 0):
                new_chunk = extracted_chunk
                new_chunk['metadata']['content'] = current_string
                chunks.append(new_chunk)
                current_string = ""
            else:
                current_string += chunks_size['metadata']['content'][i]
