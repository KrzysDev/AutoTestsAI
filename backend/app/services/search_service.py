from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
from dotenv import load_dotenv

from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.models.schemas import RetrivedChunk, Chunk

load_dotenv()


class SearchService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.embeddings_service = EmbeddingsService()

    def search(self, query: str, top_k: int = 5) -> list[RetrivedChunk]:
        query_vector = self.embeddings_service.embed_text(query)

        hits = self.client.query_points(
            collection_name="Grammar Collection",
            query=query_vector,
            limit=top_k,
        ).points

        results: list[RetrivedChunk] = []

        for hit in hits:
            results.append(
                RetrivedChunk(
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
                )
            )

        return results

    def get_all_by_field(
        self,
        collection_name: str,
        field_name: str,
        field_value,
        limit: int = 100,
    ):
        points = []
        offset = None

        while True:
            batch, next_offset = self.client.scroll(
                collection_name="Grammar Collection",
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            points.extend(batch)
            
            return_points = []
            for point in points:
                if point.payload.get(field_name) == field_value:
                    return_points.append(point)
                else:
                    print(point.payload.get(field_name))

            if next_offset is None:
                break

        offset = next_offset

        return return_points