from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
from dotenv import load_dotenv

from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.models.schemas import RetrivedChunk, Chunk

import math

load_dotenv()

embeddings_service = EmbeddingsService()

class SearchService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        

    def search(self, query: str, top_k: int = 5) -> list[RetrivedChunk]:
        query_vector = embeddings_service.embed_text(query)

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

    def __cosine_similarity(self, a, b):
        import math
        dot = sum(x*y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(x*x for x in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0

    def search_with_filter(
    self,
    collection_name: str,
    field_name: str,
    field_value,
    query_vector: list[float],
    top_k: int = 5,
    ) -> list[RetrivedChunk]:
        all_points = []
        offset = None

        while True:
            batch, next_offset = self.client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True, 
            )

            all_points.extend(batch)

            if next_offset is None:
                break

            offset = next_offset

        filtered_points = [
            point for point in all_points
            if point.payload.get(field_name) == field_value
        ]



        scored_points = [
            (point, self.__cosine_similarity(query_vector, point.vector))
            for point in filtered_points
        ]

        scored_points.sort(key=lambda x: x[1], reverse=True)

        chunks : list[RetrivedChunk] = []

        for point, score in scored_points[:top_k]:
            chunk = RetrivedChunk(
                payload=Chunk(
                    id=str(point.id),
                    section=point.payload.get("section", "grammar"),
                    language=point.payload.get("language", "en"),
                    level=point.payload.get("level", "B2"),
                    metadata={
                        "subject": point.payload.get("subject", ""),
                        "content": point.payload.get("content", "")
                    }
                ),
                score=score
            )
            chunks.append(chunk)

            chunks.append(chunk)

        return chunks

    def get_points_with_subject(self, subject : str):
        all_points = []
        offset = None

        while True:
            batch, next_offset = self.client.scroll(
                collection_name="Grammar Collection",
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True, 
            )

            all_points.extend(batch)

            if next_offset is None:
                break

            offset = next_offset

        filtered_points = [
            point for point in all_points
            if point.payload.get("subject").startswith(subject)
        ]

        return [point.payload for point in filtered_points]


        
