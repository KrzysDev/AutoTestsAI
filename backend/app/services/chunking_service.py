from backend.app.models.schemas import Chunk, ChunkMetadata
class ChunkingService:
    def __init__(self):
        pass

    """Used to chunk one big FlashcardChunk into smaller ones"""
    def chunk_data(self, data: Chunk, chunk_size: int = 30) -> list[Chunk]:

       content = data.metadata.content.split("\n")
       chunks = []
       current_words = []

       for word in content:
        if not word.strip(): 
            continue
        
        current_words.append(word)  
        
        if len(current_words) == chunk_size:  
            chunks.append(Chunk(
                id=data.id,
                section=data.section,
                language=data.language,
                level=data.level,
                metadata=ChunkMetadata(
                    subject=data.metadata.subject,
                    content="\n".join(current_words)
                )
            ))
            current_words = [] 

       if current_words:
            chunks.append(Chunk(
                id=data.id,
                section=data.section,
                language=data.language,
                level=data.level,
                metadata=ChunkMetadata(
                    subject=data.metadata.subject,
                    content="\n".join(current_words)
                )
            ))

       return chunks