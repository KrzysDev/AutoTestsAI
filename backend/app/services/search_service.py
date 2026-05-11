from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Filter
import os
from dotenv import load_dotenv

import math

load_dotenv()

# <summary>
# Service used to connect to Qdrant cluster and fetch vector embeddings or points based on subjects.
# </summary>
class SearchService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        # Note: create_payload_index is also a coroutine in AsyncQdrantClient, 
        # but we can't await it in __init__. 
        # In a real app, we might want an async setup method.
        # For now, I'll remove it from __init__ or leave it if it's not critical to run every time.
        # Actually, it's better to run it once.
        
    async def search(self, subject: str, collection: str = "Grammar Collection", language: str = None):
        # Build filter conditions dynamically
        must_conditions = [
            {
                "key": "subject",
                "match": {
                    "value": subject
                }
            }
        ]

        # Optionally filter by language (e.g. "de", "en", "fr")
        if language:
            must_conditions.append(
                {
                    "key": "language",
                    "match": {
                        "value": language
                    }
                }
            )

        result = await self.client.scroll(
            collection_name=collection,
            limit=100,
            with_payload=True,
            with_vectors=False,
            scroll_filter={"must": must_conditions}
        )

        points, _ = result
        return [p.payload for p in points]


        
