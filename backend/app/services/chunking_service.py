import copy
import hashlib
from typing import Union, Dict, Any
from backend.app.models.schemas import FlashcardChunk

class ChunkingService:
    def __init__(self):
        pass

    def chunk_vocabulary(
        self, 
        extracted_chunk: Union[FlashcardChunk, Dict[str, Any]], 
        max_lines_per_chunk: int = 5, 
        overlap_lines: int = 1
    ):
        chunks = []
        is_dict = isinstance(extracted_chunk, dict)
        
        if is_dict:
            content = extracted_chunk['metadata']['content']
        else:
            content = extracted_chunk.metadata.content
            
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        if not lines:
            return []

        start = 0
        while start < len(lines):
            end = min(start + max_lines_per_chunk, len(lines))
            chunk_lines = lines[start:end]
            chunk_text = "\n".join(chunk_lines)

            new_chunk = copy.deepcopy(extracted_chunk)
            content_hash = hashlib.md5(chunk_text.encode('utf-8')).hexdigest()[:8]
            new_chunk_id = f'vocab-{content_hash}'
            
            if is_dict:
                new_chunk['metadata']['content'] = chunk_text
                new_chunk['id'] = new_chunk_id
            else:
                new_chunk.metadata.content = chunk_text
                new_chunk.id = new_chunk_id
                
            chunks.append(new_chunk)
            
            #overlap
            step = max_lines_per_chunk - overlap_lines
            start += step if step > 0 else 1

        if len(chunks) > 1:
            if is_dict:
                last_lines = chunks[-1]['metadata']['content'].split('\n')
            else:
                last_lines = chunks[-1].metadata.content.split('\n')
                
            if len(last_lines) < (max_lines_per_chunk // 2) or len(last_lines) <= 1:
                if is_dict:
                    merged_text = chunks[-2]['metadata']['content'] + "\n" + chunks[-1]['metadata']['content']
                    chunks[-2]['metadata']['content'] = merged_text
                    content_hash = hashlib.md5(merged_text.encode('utf-8')).hexdigest()[:8]
                    chunks[-2]['id'] = f'vocab-{content_hash}'
                else:
                    merged_text = chunks[-2].metadata.content + "\n" + chunks[-1].metadata.content
                    chunks[-2].metadata.content = merged_text
                    content_hash = hashlib.md5(merged_text.encode('utf-8')).hexdigest()[:8]
                    chunks[-2].id = f'vocab-{content_hash}'
                chunks.pop()

        return chunks
