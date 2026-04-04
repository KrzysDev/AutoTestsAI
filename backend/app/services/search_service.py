from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv
from app.services.embeddings_service import EmbeddingsService
from app.models.schemas import RetrivedChunk, Chunk

load_dotenv()

class SearchService:
    def __init__(self):
        self.embeddings_service = EmbeddingsService()

    def search(self, query: str, top_k: int = 5) -> list[RetrivedChunk]:
        self.client = QdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        query_vector = self.embeddings_service.embed_text(query)

        hits = self.client.query_points(
            collection_name="Language Collection",
            query=query_vector,
            limit=top_k,
        ).points
        
        data = []

        for hit in hits:
            data.append(RetrivedChunk(
                payload=Chunk(
                    id=str(hit.id),
                    section=hit.payload.get("section", "grammar"),
                    language=hit.payload.get("language", "en"),
                    level=hit.payload.get("level", "B2"),
                    metadata={
                        "subject": hit.payload.get("subject", ""),
                        "content": hit.payload.get("content", "")
                    }
                ),
                score=hit.score
            ))

        return data






        