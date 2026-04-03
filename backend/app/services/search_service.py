from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv
from app.services.embeddings_service import EmbeddingsService

load_dotenv()

class SearchService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.embeddings_service = EmbeddingsService()

    def search(self, query: str, top_k: int = 5):

        query_vector = self.embeddings_service.embed_text(query)

        hits = self.client.query_points(
            collection_name="Language Collection",
            query=query_vector,
            limit=top_k,
        ).points
        
        data = []

        for hit in hits:
            data.append({
                "payload" : hit.payload,
                "score" : hit.score
            })

        return data






        